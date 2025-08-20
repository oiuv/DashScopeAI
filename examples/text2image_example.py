#!/usr/bin/env python3
"""
文生图功能使用示例

本示例展示了如何使用阿里云百炼的文生图功能生成图像。
运行前请确保已配置API密钥：
1. 复制 .env.example 为 .env
2. 填入你的阿里云百炼API密钥
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到Python路径
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.image import Text2ImageGenerator


def basic_usage():
    """基础使用示例 - 同步方法"""
    print("🎨 基础使用示例 - 同步方法")
    print("-" * 50)
    
    # 初始化生成器
    generator = Text2ImageGenerator()
    
    # 简单的文生图
    prompt = "一只可爱的橘猫坐在窗台上，阳光透过窗户洒进来，温馨治愈的画面"
    
    try:
        result = generator.generate_image_sync(
            prompt=prompt,
            size="1328*1328",
            prompt_extend=True,
            watermark=False
        )
        
        if result.task_status.value == "SUCCEEDED" and result.results:
            image = result.results[0]
            print(f"✅ 生成成功！")
            print(f"📋 任务ID: {result.task_id}")
            print(f"🖼️  图像URL: {image.url}")
            print(f"⏱️  耗时: {result.end_time}")
            
            # 下载图像
            save_dir = Path("./generated_images")
            file_path = generator.download_image_sync(image.url, str(save_dir))
            print(f"💾 已保存到: {file_path}")
        else:
            print(f"❌ 生成失败: {result.task_status}")
            
    except Exception as e:
        print(f"❌ 错误: {e}")


async def advanced_usage():
    """高级使用示例 - 异步方法"""
    print("\n🎨 高级使用示例 - 异步方法")
    print("-" * 50)
    
    generator = Text2ImageGenerator()
    
    # 复杂的场景描述
    prompt = """
    一副典雅庄重的对联悬挂于中式厅堂正中，画面主体为一间布置古朴、
    安静祥和的中国古典房间。房间内，红木家具沉稳大气，中央摆放着一张长桌，
    桌上陈列着几件精美的青花瓷器，纹饰细腻，釉色清雅。
    对联以飘逸洒脱的毛笔书法书写，左侧上联为"义本生知人机同道善思新"，
    右侧下联为"通云赋智乾坤启数高志远"，横批为"智启通义"。
    """
    
    negative_prompt = "低分辨率、模糊、扭曲、畸形、低质量、错误、最差质量"
    
    try:
        result = await generator.generate_image(
            prompt=prompt,
            negative_prompt=negative_prompt,
            size="1472*1140",  # 4:3 比例
            prompt_extend=True,
            watermark=False
        )
        
        if result.task_status.value == "SUCCEEDED" and result.results:
            image = result.results[0]
            print(f"✅ 高级示例生成成功！")
            print(f"📋 原始提示词: {image.orig_prompt[:100]}...")
            if image.actual_prompt:
                print(f"📋 实际提示词: {image.actual_prompt[:100]}...")
            print(f"🖼️  图像URL: {image.url}")
            
            # 下载并重命名文件
            save_dir = Path("./generated_images")
            filename = "chinese_hall.png"
            file_path = await generator.download_image(image.url, str(save_dir), filename)
            print(f"💾 已保存到: {file_path}")
        else:
            print(f"❌ 生成失败: {result.task_status}")
            
    except Exception as e:
        print(f"❌ 错误: {e}")


async def batch_generation():
    """批量生成示例"""
    print("\n🎨 批量生成示例")
    print("-" * 50)
    
    generator = Text2ImageGenerator()
    
    # 多个提示词
    prompts = [
        "一只可爱的柯基犬在草地上奔跑，阳光明媚，高清写实风格",
        "未来科技城市夜景，霓虹灯光，赛博朋克风格，高清",
        "中国传统山水画，青山绿水，云雾缭绕，水墨风格"
    ]
    
    tasks = []
    for i, prompt in enumerate(prompts):
        task = generator.generate_image(
            prompt=prompt,
            size="1328*1328",
            prompt_extend=True,
            watermark=False
        )
        tasks.append((i, task))
    
    # 并行执行
    results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
    
    save_dir = Path("./generated_images")
    
    for (i, _), result in zip(tasks, results):
        if isinstance(result, Exception):
            print(f"❌ 任务 {i+1} 失败: {result}")
        elif result.task_status.value == "SUCCEEDED" and result.results:
            image = result.results[0]
            filename = f"batch_{i+1}_{prompts[i][:20].replace(' ', '_')}.png"
            file_path = await generator.download_image(image.url, str(save_dir), filename)
            print(f"✅ 任务 {i+1} 成功，保存到: {file_path}")


async def custom_polling():
    """自定义轮询示例"""
    print("\n🎨 自定义轮询示例")
    print("-" * 50)
    
    generator = Text2ImageGenerator()
    
    # 创建任务但不等待完成
    from src.image.models import ImageGenerationRequest
    
    request = ImageGenerationRequest(
        prompt="一只优雅的波斯猫，白色长毛，蓝宝石般的眼睛，在豪华客厅中",
        size="1140*1472",  # 3:4 竖屏比例
        prompt_extend=True,
        watermark=False
    )
    
    try:
        # 创建任务
        task = await generator.create_task(request)
        print(f"📋 任务已创建: {task.task_id}")
        
        # 自定义轮询
        print("⏳ 等待任务完成...")
        poll_count = 0
        
        while True:
            result = await generator.get_task_result(task.task_id)
            poll_count += 1
            
            print(f"第{poll_count}次轮询 - 状态: {result.task_status.value}")
            
            if result.task_status == TaskStatus.SUCCEEDED:
                print("✅ 任务完成！")
                if result.results:
                    image = result.results[0]
                    file_path = await generator.download_image(
                        image.url, 
                        "./generated_images", 
                        "custom_polling.png"
                    )
                    print(f"💾 已保存到: {file_path}")
                break
            elif result.task_status in [TaskStatus.FAILED, TaskStatus.CANCELED]:
                print(f"❌ 任务失败: {result.task_status}")
                break
                
            await asyncio.sleep(2)  # 2秒轮询间隔
            
    except Exception as e:
        print(f"❌ 错误: {e}")


def download_and_save_examples():
    """下载并保存示例图像"""
    print("\n💾 下载示例")
    print("-" * 50)
    
    # 确保目录存在
    save_dir = Path("./generated_images")
    save_dir.mkdir(exist_ok=True)
    print(f"📁 保存目录: {save_dir.absolute()}")


async def main():
    """主函数"""
    print("🚀 阿里云百炼文生图功能演示")
    print("=" * 50)
    
    # 检查API密钥
    if not os.getenv("DASHSCOPE_API_KEY"):
        print("⚠️  未找到API密钥！")
        print("请复制 .env.example 为 .env 并填入你的阿里云百炼API密钥")
        return
    
    # 创建保存目录
    download_and_save_examples()
    
    # 运行示例
    basic_usage()
    await advanced_usage()
    await batch_generation()
    await custom_polling()
    
    print("\n🎉 所有示例运行完成！")
    print(f"📁 生成的图像保存在: {Path('./generated_images').absolute()}")


if __name__ == "__main__":
    asyncio.run(main())