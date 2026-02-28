#!/usr/bin/env python3
"""
DashScope CLI - 阿里百炼大模型统一命令行工具

使用示例:
    python -m cli text2image "一只猫咪"
    python -m cli image-edit input.jpg "修改描述"
    python -m cli sketch2image sketch.png "描述"
    python -m cli style-repaint photo.jpg --style 30
    python -m cli speech-rec --mode mic
    python -m cli batch-edit config.json
"""

import sys
import argparse

from . import __version__

# 子命令配置 - 延迟导入
SUBCOMMANDS = {
    'text2image': {
        'help': '文生图 - 根据文本描述生成图像',
        'description': '阿里云百炼文生图工具 - 根据文本描述生成精美图像',
        'module': 'text2image',
    },
    'image-edit': {
        'help': '图像编辑 - 编辑现有图像',
        'description': '阿里百炼图像编辑工具 - 支持千问和万相模型',
        'module': 'image_edit',
    },
    'sketch2image': {
        'help': '涂鸦作画 - 根据草图和描述生成图像',
        'description': '雪风 AI 涂鸦绘画工具 - 根据草图和文本描述生成图像',
        'module': 'sketch2image',
    },
    'style-repaint': {
        'help': '人像重绘 - 人像风格转换',
        'description': '阿里百炼人像风格重绘工具 - 将人像转换为不同艺术风格',
        'module': 'style_repaint',
    },
    'speech-rec': {
        'help': '语音识别 - 实时语音转文字',
        'description': '阿里百炼实时语音识别工具 - 支持麦克风和扬声器模式',
        'module': 'speech_rec',
    },
    'batch-edit': {
        'help': '批量编辑 - 批量处理图像编辑任务',
        'description': '批量图像编辑工具 - 根据配置文件批量处理图像',
        'module': 'batch_edit',
    },
    'video': {
        'help': '视频生成 - 文生视频/图生视频',
        'description': '阿里百炼视频生成工具 - 支持文生视频、图生视频、首尾帧生视频',
        'module': 'video',
    },
}


def get_command_module(module_name: str):
    """
    延迟加载命令模块

    Args:
        module_name: 模块名称

    Returns:
        模块对象
    """
    # 单独导入每个模块，避免一次性导入所有模块导致错误
    if module_name == 'text2image':
        from .commands import text2image
        return text2image
    elif module_name == 'image_edit':
        from .commands import image_edit
        return image_edit
    elif module_name == 'sketch2image':
        from .commands import sketch2image
        return sketch2image
    elif module_name == 'style_repaint':
        from .commands import style_repaint
        return style_repaint
    elif module_name == 'speech_rec':
        from .commands import speech_rec
        return speech_rec
    elif module_name == 'batch_edit':
        from .commands import batch_edit
        return batch_edit
    elif module_name == 'video':
        from .commands import video
        return video
    return None


def create_parser() -> argparse.ArgumentParser:
    """创建主解析器"""
    parser = argparse.ArgumentParser(
        prog='dashscope-cli',
        description='阿里百炼大模型统一命令行工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 文生图
  python -m cli text2image "一只可爱的猫咪"
  python -m cli text2image "赛博朋克城市" -m wan2.2-t2i-plus -s 1440*810 -n 2

  # 图像编辑
  python -m cli image-edit input.jpg "转换成卡通风格"
  python -m cli image-edit input.jpg "法国绘本风格" -m wanx2.1-imageedit -f stylization_all

  # 涂鸦作画
  python -m cli sketch2image sketch.png "一只可爱的猫咪" --style anime

  # 人像风格重绘
  python -m cli style-repaint photo.jpg 3
  python -m cli style-repaint photo.jpg --style-ref style.jpg

  # 语音识别
  python -m cli speech-rec --mode mic
  python -m cli speech-rec --mode speaker

  # 批量图像编辑
  python -m cli batch-edit config.json

可用子命令:
  text2image      文生图 - 根据文本描述生成图像
  image-edit      图像编辑 - 编辑现有图像
  sketch2image    涂鸦作画 - 根据草图和描述生成图像
  style-repaint   人像重绘 - 人像风格转换
  speech-rec      语音识别 - 实时语音转文字
  batch-edit      批量编辑 - 批量处理图像编辑任务
  video           视频生成 - 文生视频/图生视频/特效模板

视频特效模板:
  通用特效：squish(解压捏捏), rotation(转圈圈), poke(戳戳乐), inflate(气球膨胀), dissolve(分子扩散), melt(热浪融化), icecream(冰淇淋星球)
  单人/动物：flying(魔法悬浮), rose(赠人玫瑰), crystalrose(闪亮玫瑰)
  单人特效：carousel(时光木马), singleheart(爱你哟), dance1-5(舞蹈), mermaid(人鱼觉醒), graduation(学术加冕), dragon(巨兽追袭), money(财从天降), jellyfish(水母之约), pupil(瞳孔穿越)
  双人特效：hug(爱的抱抱), frenchkiss(唇齿相依), coupleheart(双倍心动)
  首尾帧特效：hanfu-1(唐韵翩然), solaron(机甲变身), magazine(闪耀封面), mech1/2(机械/赛博)

更多信息:
  使用 'python -m cli <子命令> --help' 查看特定子命令的详细帮助
        """
    )

    parser.add_argument(
        '-V', '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )

    # 创建子命令解析器
    subparsers = parser.add_subparsers(
        dest='command',
        title='可用子命令',
        description='选择一个子命令来执行具体功能',
        help='子命令帮助'
    )

    # 注册子命令 - 使用懒加载方式添加参数
    for cmd_name, cmd_config in SUBCOMMANDS.items():
        subparser = subparsers.add_parser(
            cmd_name,
            help=cmd_config['help'],
            description=cmd_config['description']
        )
        # 存储模块名供后续使用
        subparser.set_defaults(_module=cmd_config['module'])

        # 尝试加载模块并添加参数（如果可能的话）
        try:
            cmd_module = get_command_module(cmd_config['module'])
            if cmd_module and hasattr(cmd_module, 'add_arguments'):
                cmd_module.add_arguments(subparser)
        except (ImportError, ModuleNotFoundError):
            # 如果导入失败，跳过参数添加，在执行时再处理
            pass

    return parser


def main(args=None):
    """主函数"""
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    if not parsed_args.command:
        parser.print_help()
        return 0

    # 获取模块名
    module_name = getattr(parsed_args, '_module', None)
    if not module_name:
        parser.print_help()
        return 1

    # 延迟加载模块
    cmd_module = get_command_module(module_name)
    if not cmd_module:
        print(f"错误：未知命令 {parsed_args.command}")
        return 1

    # 执行子命令
    return cmd_module.execute(parsed_args)


if __name__ == '__main__':
    sys.exit(main())
