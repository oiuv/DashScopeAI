#!/usr/bin/env python3
"""
阿里百炼图像编辑 - 统一CLI工具
支持通义千问-图像编辑和通义万相-通用图像编辑
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.image import ImageEditor, WanxEditFunction
from src.image.models import ModelType


def print_banner():
    """打印欢迎横幅"""
    print("=" * 60)
    print("🖼️ 阿里百炼图像编辑工具")
    print("支持千问-图像编辑 & 万相-通用图像编辑")
    print("=" * 60)


def check_api_key():
    """检查API密钥"""
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ 错误：未找到API密钥")
        print("请设置环境变量 DASHSCOPE_API_KEY")
        print("Windows: set DASHSCOPE_API_KEY=你的密钥")
        print("Linux/Mac: export DASHSCOPE_API_KEY=你的密钥")
        print("或者使用 --api-key 参数")
        return False
    return True


def get_model_short_name(model_name: str) -> str:
    """获取模型简称"""
    model_short_names = {
        "qwen-image-edit": "qwen_edit",
        "wanx2.1-imageedit": "wanx_edit"
    }
    return model_short_names.get(model_name, model_name)


def validate_image_path(image_path: str) -> str:
    """验证图像路径并返回URL/Base64"""
    path = Path(image_path)
    if not path.exists():
        # 如果是URL，直接返回
        if image_path.startswith(('http://', 'https://')):
            return image_path
        else:
            raise FileNotFoundError(f"图像文件不存在: {image_path}")
    
    # 本地文件转换为Base64
    editor = ImageEditor()
    return editor.encode_image_to_base64(str(path))


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="阿里百炼图像编辑工具 - 支持千问和万相模型",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
【模型差异说明】
千问-图像编辑 (qwen-image-edit):
  ✓ 同步接口，即时返回结果
  ✓ 支持：文字编辑、物体增删、姿势调整、风格迁移
  ✓ 参数：image_path + prompt + [negative_prompt]

万相-通用图像编辑 (wanx2.1-imageedit):
  ✓ 异步接口，需轮询状态
  ✓ 支持9大功能：全局风格化、局部风格化、指令编辑、局部重绘、去水印、扩图、超分、上色、线稿生图
  ✓ 参数：image_path + prompt + --function + [高级参数]

使用示例:
  # 千问编辑 - 同步返回，适合文字/物体编辑
  python image_edit.py input.jpg "将狗改为站立姿势" --model qwen-image-edit
  python image_edit.py sign.jpg "将'欢迎光临'改为'开业大吉'" --model qwen-image-edit
  
  # 万相编辑 - 需指定功能类型
  python image_edit.py input.jpg "法国绘本风格" --model wanx2.1-imageedit --function stylization_all --strength 0.7
  python image_edit.py base.jpg mask.png "在mask区域添加一只白色陶瓷兔子摆件，造型圆润可爱" --model wanx2.1-imageedit --function description_edit_with_mask
  python image_edit.py house.jpg "把房子变成冰雕风格" --model wanx2.1-imageedit --function stylization_local
  python image_edit.py blurry.jpg "高清放大提升细节" --model wanx2.1-imageedit --function super_resolution --upscale-factor 2
  python image_edit.py portrait.jpg "一家人在公园草坪上" --model wanx2.1-imageedit --function expand --top-scale 1.5 --left-scale 1.2
  python image_edit.py sketch.jpg "二次元动漫风格" --model wanx2.1-imageedit --function doodle --is-sketch
  
  # 万相9大功能对照:
  # stylization_all: 全局风格化    stylization_local: 局部风格化
  # description_edit: 指令编辑    description_edit_with_mask: 局部重绘
  # remove_watermark: 去水印      expand: 扩图
  # super_resolution: 超分辨率    colorization: 黑白上色
  # doodle: 线稿生图            control_cartoon_feature: 卡通生图
  
  # 局部风格化8种风格对照:
  # 冰雕: ice        云朵: cloud        花灯: chinese festive lantern
  # 木板: wooden     青花瓷: blue and white porcelain
  # 毛茸茸: fluffy   毛线: weaving      气球: balloon
  # 
  # 使用示例: "把房子变成冰雕风格" 或 "把背景变成云朵效果"
        """
    )
    
    # 必需参数
    parser.add_argument(
        "image_path",
        help="输入图像路径或URL"
    )
    
    parser.add_argument(
        "prompt",
        help="编辑提示词"
    )
    
    # 模型选择
    parser.add_argument(
        "-m", "--model",
        choices=["qwen-image-edit", "wanx2.1-imageedit"],
        default="qwen-image-edit",
        help="编辑模型：qwen-image-edit(千问-同步) 或 wanx2.1-imageedit(万相-异步+功能选择)"
    )
    
    # 万相模型专用参数
    wanx_group = parser.add_argument_group('万相模型专用参数')
    wanx_group.add_argument(
        "-f", "--function",
        choices=[
            "stylization_all", "stylization_local", "description_edit",
            "description_edit_with_mask", "remove_watermark", "expand",
            "super_resolution", "colorization", "doodle", "control_cartoon_feature"
        ],
        help="万相9大功能类型 (万相模型必选项)"
    )
    
    wanx_group.add_argument(
        "-n", "--n",
        type=int,
        choices=[1, 2, 3, 4],
        default=1,
        help="万相模型：生成图片数量 (1-4张，默认1)"
    )
    
    wanx_group.add_argument(
        "-S", "--seed",
        type=int,
        help="万相模型：随机种子 (控制生成随机性)"
    )
    
    wanx_group.add_argument(
        "--strength",
        type=float,
        choices=[i/10 for i in range(0, 11)],  # 0.0-1.0，步长0.1
        help="万相模型：图像修改幅度，用于全局风格化和指令编辑 (0.0-1.0，默认0.5)"
    )
    
    # 扩图功能专用参数
    expand_group = parser.add_argument_group('扩图功能专用参数（仅--function expand时有效）')
    expand_group.add_argument(
        "--top-scale",
        type=float,
        choices=[i/10 for i in range(10, 21)],  # 1.0-2.0，步长0.1
        default=1.0,
        help="向上扩展比例 [1.0-2.0]，默认1.0"
    )
    expand_group.add_argument(
        "--bottom-scale",
        type=float,
        choices=[i/10 for i in range(10, 21)],  # 1.0-2.0，步长0.1
        default=1.0,
        help="向下扩展比例 [1.0-2.0]，默认1.0"
    )
    expand_group.add_argument(
        "--left-scale",
        type=float,
        choices=[i/10 for i in range(10, 21)],  # 1.0-2.0，步长0.1
        default=1.0,
        help="向左扩展比例 [1.0-2.0]，默认1.0"
    )
    expand_group.add_argument(
        "--right-scale",
        type=float,
        choices=[i/10 for i in range(10, 21)],  # 1.0-2.0，步长0.1
        default=1.0,
        help="向右扩展比例 [1.0-2.0]，默认1.0"
    )
    
    # 超分辨率专用参数
    super_group = parser.add_argument_group('超分辨率专用参数（仅--function super_resolution时有效）')
    super_group.add_argument(
        "--upscale-factor",
        type=int,
        choices=[1, 2, 3, 4],
        default=1,
        help="放大倍数 (1-4倍，默认1。1=仅高清不放大)"
    )
    
    # 线稿生图专用参数
    doodle_group = parser.add_argument_group('线稿生图专用参数（仅--function doodle时有效）')
    doodle_group.add_argument(
        "--is-sketch",
        action="store_true",
        help="输入是否为线稿图像 (true=直接基于线稿作画，false=先提取线稿再作画)"
    )
    
    wanx_group.add_argument(
        "mask_path",
        nargs='?',
        help="万相模型：mask图像路径（仅description_edit_with_mask功能需要）"
    )
    
    # 千问模型专用参数
    qwen_group = parser.add_argument_group('千问模型专用参数')
    qwen_group.add_argument(
        "-N", "--negative",
        default="",
        help="反向提示词 (仅千问模型支持)"
    )
    
    parser.add_argument(
        "-k", "--api-key",
        help="阿里云百炼API密钥（可选，也可通过环境变量设置）"
    )
    
    parser.add_argument(
        "-o", "--output",
        default="./edited_images",
        help="输出目录 (默认: ./edited_images)"
    )
    
    parser.add_argument(
        "-w", "--watermark",
        action="store_true",
        help="添加水印标识"
    )
    
    parser.add_argument(
        "--filename",
        help="输出文件名（可选，默认自动生成）"
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    # 检查API密钥
    api_key = args.api_key or os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        check_api_key()
        return 1
    
    try:
        editor = ImageEditor(api_key=api_key)
        
        # 验证图像路径
        image_url = validate_image_path(args.image_path)
        
        # 模型专用参数验证
        mask_image_url = None
        if args.model == "wanx2.1-imageedit":
            if not args.function:
                print("❌ 错误：万相模型必须指定 --function 参数")
                print("   可用功能：stylization_all, stylization_local, description_edit, description_edit_with_mask, remove_watermark, expand, super_resolution, colorization, doodle, control_cartoon_feature")
                return 1
                
            if args.function == "description_edit_with_mask":
                if not args.mask_path:
                    print("❌ 错误：万相局部重绘功能需要提供mask图像")
                    print("   使用示例：python image_edit.py base.jpg mask.png '添加物体' --function description_edit_with_mask")
                    return 1
                mask_image_url = validate_image_path(args.mask_path)
                print(f"🎭 使用万相局部重绘：mask={args.mask_path}")
            else:
                print(f"🎨 使用万相功能：{args.function}")
                
        elif args.model == "qwen-image-edit":
            if args.function:
                print("⚠️  提醒：千问模型不需要 --function 参数，已忽略")
            print("🔍 使用千问-图像编辑（同步接口）")
        
        print(f"🖼️ 正在编辑: {args.image_path}")
        print(f"📝 编辑指令: {args.prompt}")
        print(f"🤖 使用模型: {args.model}")
        
        if args.negative:
            print(f"🚫 反向提示: {args.negative}")
        
        # 构建万相模型专用参数
        wanx_params = {}
        if args.model == "wanx2.1-imageedit":
            if args.strength is not None:
                wanx_params['strength'] = args.strength
            
            if args.function == "expand":
                wanx_params.update({
                    'top_scale': args.top_scale,
                    'bottom_scale': args.bottom_scale,
                    'left_scale': args.left_scale,
                    'right_scale': args.right_scale
                })
            
            if args.function == "super_resolution":
                wanx_params['upscale_factor'] = args.upscale_factor
            
            if args.function == "doodle":
                wanx_params['is_sketch'] = args.is_sketch
        
        # 执行编辑
        result = editor.edit_image(
            model=args.model,
            image_url=image_url,
            prompt=args.prompt,
            function=args.function,
            mask_image_url=mask_image_url,
            negative_prompt=args.negative or None,
            n=args.n,
            seed=args.seed,
            watermark=args.watermark,
            **wanx_params
        )
        
        # 获取编辑后的图像URL
        if args.model == "qwen-image-edit":
            # 千问模型直接返回URL
            edited_url = result.url
            print(f"✅ 编辑完成！")
            print(f"🌐 图像URL: {edited_url}")
        else:
            # 万相模型从结果中提取URL
            if result.results and result.results[0]:
                edited_url = result.results[0].url
                print(f"✅ 编辑完成！")
                print(f"🌐 图像URL: {edited_url}")
            else:
                print("❌ 编辑失败：未获取到结果")
                return 1
        
        # 下载图像
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        if args.filename:
            filename = args.filename
        else:
            model_short = get_model_short_name(args.model)
            safe_name = "".join(c for c in args.prompt[:20] if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name.replace(' ', '_') or "edited"
            if args.function:
                filename = f"{model_short}_{args.function}_{safe_name}.png"
            else:
                filename = f"{model_short}_{safe_name}.png"
        
        file_path = editor.download_image(edited_url, str(output_dir), filename)
        
        print(f"📁 保存路径: {file_path}")
        task_id_str = result.task_id if hasattr(result, 'task_id') and result.task_id else "同步任务(千问模型)"
        print(f"📊 任务ID: {task_id_str}")
        
        return 0
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())