import os
import sys
from PIL import Image
import argparse
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def resize_image(input_path, output_path, width=None, height=None, scale=None, keep_ratio=True, quality=95):
    """
    调整图片尺寸
    
    参数:
    input_path: 输入图片路径
    output_path: 输出图片路径
    width: 目标宽度
    height: 目标高度
    scale: 缩放比例
    keep_ratio: 是否保持宽高比
    quality: 输出图片质量（JPEG格式有效，1-100）
    """
    try:
        # 验证输入文件
        if not os.path.exists(input_path):
            logging.error(f"输入文件不存在: {input_path}")
            return False
            
        # 检查文件扩展名
        input_path = Path(input_path)
        output_path = Path(output_path)
        
        # 支持的图片格式
        supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp', '.ico', '.ppm', '.pgm', '.pbm'}
        
        if input_path.suffix.lower() not in supported_formats:
            logging.error(f"不支持的图片格式: {input_path.suffix}")
            return False
            
        # 打开图片
        with Image.open(input_path) as img:
            # 获取原始尺寸
            original_width, original_height = img.size
            
            # 检查尺寸限制
            if original_width * original_height > 50000000:  # 限制5000万像素
                logging.error(f"图片尺寸过大: {original_width}x{original_height}")
                return False
            
            # 计算新尺寸
            if scale:
                # 使用缩放比例
                new_width = int(original_width * scale)
                new_height = int(original_height * scale)
            else:
                # 使用指定的宽度和高度
                new_width = width if width else original_width
                new_height = height if height else original_height
                
                # 如果需要保持比例
                if keep_ratio:
                    if width and height:
                        # 同时指定了宽度和高度，保持比例填充
                        width_ratio = width / original_width
                        height_ratio = height / original_height
                        if width_ratio < height_ratio:
                            new_width = int(original_width * width_ratio)
                            new_height = int(original_height * width_ratio)
                        else:
                            new_width = int(original_width * height_ratio)
                            new_height = int(original_height * height_ratio)
                    elif width and not height:
                        # 只指定了宽度，计算高度
                        ratio = width / original_width
                        new_height = int(original_height * ratio)
                    elif height and not width:
                        # 只指定了高度，计算宽度
                        ratio = height / original_height
                        new_width = int(original_width * ratio)
            
            # 检查新尺寸
            if new_width <= 0 or new_height <= 0:
                logging.error(f"计算出的尺寸无效: {new_width}x{new_height}")
                return False
                
            # 调整尺寸
            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 创建输出目录（如果不存在）
            output_dir = output_path.parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 保存图片
            save_kwargs = {}
            if output_path.suffix.lower() in ['.jpg', '.jpeg']:
                save_kwargs['quality'] = quality
                save_kwargs['optimize'] = True
            elif output_path.suffix.lower() == '.png':
                save_kwargs['optimize'] = True
                
            resized_img.save(output_path, **save_kwargs)
            logging.info(f"已处理: {input_path} -> {output_path} ({new_width}x{new_height})")
            return True
    
    except Exception as e:
        logging.error(f"处理 {input_path} 时出错: {str(e)}")
        return False

def batch_resize(input_dir, output_dir, **kwargs):
    """批量处理目录中的图片"""
    supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp', '.ico', '.ppm', '.pgm', '.pbm'}
    
    # 验证输入目录
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    
    if not input_dir.exists():
        logging.error(f"输入目录不存在: {input_dir}")
        return
    
    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 收集所有图片文件
    image_files = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix.lower() in supported_formats:
                image_files.append(file_path)
    
    if not image_files:
        logging.warning(f"在 {input_dir} 中没有找到支持的图片文件")
        return
    
    logging.info(f"找到 {len(image_files)} 个图片文件，开始处理...")
    
    # 处理图片并跟踪进度
    success_count = 0
    for i, input_path in enumerate(image_files, 1):
        # 构建输出路径，保持目录结构
        relative_path = input_path.relative_to(input_dir)
        output_path = output_dir / relative_path
        
        logging.info(f"[{i}/{len(image_files)}] 处理: {input_path.name}")
        
        if resize_image(str(input_path), str(output_path), **kwargs):
            success_count += 1
    
    logging.info(f"批量处理完成！成功: {success_count}/{len(image_files)}")

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description='Image resizing tool supporting single files and batch processing'
    )
    
    parser.add_argument('input', help='输入图片文件或目录')
    parser.add_argument('output', help='输出图片文件或目录')
    parser.add_argument('-W', '--width', type=int, help='目标宽度(像素)')
    parser.add_argument('-H', '--height', type=int, help='目标高度(像素)')
    parser.add_argument('-S', '--scale', type=float, help='缩放比例(例如0.5表示缩小到50%%)')
    parser.add_argument('-Q', '--quality', type=int, default=95, choices=range(1, 101), 
                       help='输出图片质量(JPEG格式，1-100，默认95)')
    parser.add_argument('--no-ratio', action='store_true', help='不保持宽高比')
    parser.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 验证参数
    if not args.width and not args.height and not args.scale:
        logging.error("错误：必须指定宽度、高度或缩放比例中的至少一个")
        sys.exit(1)
    
    if args.scale and (args.width or args.height):
        logging.warning("警告：同时指定了缩放比例和宽度/高度，将使用缩放比例")
    
    if args.quality < 1 or args.quality > 100:
        logging.error("错误：图片质量必须在1-100之间")
        sys.exit(1)
    
    # 构建参数字典
    resize_kwargs = {
        'width': args.width,
        'height': args.height,
        'scale': args.scale,
        'keep_ratio': not args.no_ratio,
        'quality': args.quality
    }
    
    # 处理单个文件或目录
    input_path = Path(args.input)
    
    if not input_path.exists():
        logging.error(f"错误：输入路径不存在 - {args.input}")
        sys.exit(1)
    
    if input_path.is_file():
        # 处理单个文件
        output_path = Path(args.output)
        if output_path.is_dir():
            # 如果输出是目录，自动构建输出文件名
            output_path = output_path / input_path.name
            # 添加缩放标记到文件名
            if args.scale:
                stem = output_path.stem
                suffix = output_path.suffix
                output_path = output_path.parent / f"{stem}_scaled_{args.scale}{suffix}"
        
        logging.info(f"开始处理单个文件: {args.input} -> {output_path}")
        success = resize_image(str(input_path), str(output_path), **resize_kwargs)
        if not success:
            sys.exit(1)
    elif input_path.is_dir():
        # 处理目录（批量处理）
        logging.info(f"开始批量处理目录: {args.input}")
        batch_resize(str(input_path), str(Path(args.output)), **resize_kwargs)
    else:
        logging.error(f"错误：输入路径类型不支持 - {args.input}")
        sys.exit(1)
    
    logging.info("处理完成！")

if __name__ == "__main__":
    main()
