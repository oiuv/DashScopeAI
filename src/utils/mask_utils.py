"""
mask图像处理工具
提供创建和处理mask图像的功能，用于万相局部重绘
"""

from PIL import Image, ImageDraw
import numpy as np
from typing import Tuple, Optional, List
from pathlib import Path


class MaskCreator:
    """mask图像创建器"""
    
    @staticmethod
    def create_rectangle_mask(
        image_path: str,
        x: int,
        y: int,
        width: int,
        height: int,
        output_path: Optional[str] = None
    ) -> str:
        """
        创建矩形mask
        
        Args:
            image_path: 原始图像路径
            x: 矩形左上角x坐标
            y: 矩形左上角y坐标
            width: 矩形宽度
            height: 矩形高度
            output_path: 输出mask图像路径
            
        Returns:
            str: mask图像路径
        """
        # 打开原始图像获取尺寸
        with Image.open(image_path) as img:
            img_width, img_height = img.size
        
        # 创建黑色背景
        mask = Image.new('L', (img_width, img_height), 0)
        draw = ImageDraw.Draw(mask)
        
        # 绘制白色矩形
        draw.rectangle([x, y, x + width, y + height], fill=255)
        
        # 保存mask
        if output_path is None:
            output_path = str(Path(image_path).with_suffix('')) + "_mask.png"
        
        mask.save(output_path)
        return output_path
    
    @staticmethod
    def create_circle_mask(
        image_path: str,
        center_x: int,
        center_y: int,
        radius: int,
        output_path: Optional[str] = None
    ) -> str:
        """
        创建圆形mask
        
        Args:
            image_path: 原始图像路径
            center_x: 圆心x坐标
            center_y: 圆心y坐标
            radius: 圆半径
            output_path: 输出mask图像路径
            
        Returns:
            str: mask图像路径
        """
        # 打开原始图像获取尺寸
        with Image.open(image_path) as img:
            img_width, img_height = img.size
        
        # 创建黑色背景
        mask = Image.new('L', (img_width, img_height), 0)
        draw = ImageDraw.Draw(mask)
        
        # 绘制白色圆形
        draw.ellipse([
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius
        ], fill=255)
        
        # 保存mask
        if output_path is None:
            output_path = str(Path(image_path).with_suffix('')) + "_mask.png"
        
        mask.save(output_path)
        return output_path
    
    @staticmethod
    def create_polygon_mask(
        image_path: str,
        points: List[Tuple[int, int]],
        output_path: Optional[str] = None
    ) -> str:
        """
        创建多边形mask
        
        Args:
            image_path: 原始图像路径
            points: 多边形顶点坐标列表 [(x1,y1), (x2,y2), ...]
            output_path: 输出mask图像路径
            
        Returns:
            str: mask图像路径
        """
        # 打开原始图像获取尺寸
        with Image.open(image_path) as img:
            img_width, img_height = img.size
        
        # 创建黑色背景
        mask = Image.new('L', (img_width, img_height), 0)
        draw = ImageDraw.Draw(mask)
        
        # 绘制白色多边形
        draw.polygon(points, fill=255)
        
        # 保存mask
        if output_path is None:
            output_path = str(Path(image_path).with_suffix('')) + "_mask.png"
        
        mask.save(output_path)
        return output_path
    
    @staticmethod
    def create_ellipse_mask(
        image_path: str,
        center_x: int,
        center_y: int,
        radius_x: int,
        radius_y: int,
        output_path: Optional[str] = None
    ) -> str:
        """
        创建椭圆mask
        
        Args:
            image_path: 原始图像路径
            center_x: 椭圆中心x坐标
            center_y: 椭圆中心y坐标
            radius_x: x轴半径
            radius_y: y轴半径
            output_path: 输出mask图像路径
            
        Returns:
            str: mask图像路径
        """
        # 打开原始图像获取尺寸
        with Image.open(image_path) as img:
            img_width, img_height = img.size
        
        # 创建黑色背景
        mask = Image.new('L', (img_width, img_height), 0)
        draw = ImageDraw.Draw(mask)
        
        # 绘制白色椭圆
        draw.ellipse([
            center_x - radius_x,
            center_y - radius_y,
            center_x + radius_x,
            center_y + radius_y
        ], fill=255)
        
        # 保存mask
        if output_path is None:
            output_path = str(Path(image_path).with_suffix('')) + "_mask.png"
        
        mask.save(output_path)
        return output_path
    
    @staticmethod
    def create_inverse_mask(
        image_path: str,
        mask_path: str,
        output_path: Optional[str] = None
    ) -> str:
        """
        创建反转mask（黑白互换）
        
        Args:
            image_path: 原始图像路径
            mask_path: 原始mask路径
            output_path: 输出反转mask路径
            
        Returns:
            str: 反转后的mask图像路径
        """
        # 打开原始图像获取尺寸
        with Image.open(image_path) as img:
            img_width, img_height = img.size
        
        # 打开原始mask
        with Image.open(mask_path) as mask:
            # 确保尺寸匹配
            if mask.size != (img_width, img_height):
                mask = mask.resize((img_width, img_height))
            
            # 创建反转mask
            mask_array = np.array(mask)
            inverted_mask = 255 - mask_array
            inverted_image = Image.fromarray(inverted_mask.astype('uint8'))
        
        # 保存反转mask
        if output_path is None:
            output_path = str(Path(mask_path).with_suffix('')) + "_inverted.png"
        
        inverted_image.save(output_path)
        return output_path
    
    @staticmethod
    def create_smart_mask(
        image_path: str,
        target_color: Tuple[int, int, int],
        tolerance: int = 30,
        output_path: Optional[str] = None
    ) -> str:
        """
        基于颜色创建智能mask
        
        Args:
            image_path: 原始图像路径
            target_color: 目标颜色RGB值 (r, g, b)
            tolerance: 颜色容差
            output_path: 输出mask图像路径
            
        Returns:
            str: mask图像路径
        """
        # 打开原始图像
        with Image.open(image_path) as img:
            img_rgb = img.convert('RGB')
            img_array = np.array(img_rgb)
            
            # 计算与目标颜色的差异
            target_r, target_g, target_b = target_color
            diff = np.abs(img_array - np.array([target_r, target_g, target_b]))
            
            # 计算总差异
            total_diff = np.sum(diff, axis=2)
            
            # 创建mask
            mask_array = np.where(total_diff <= tolerance * 3, 255, 0)
            mask = Image.fromarray(mask_array.astype('uint8'))
        
        # 保存mask
        if output_path is None:
            output_path = str(Path(image_path).with_suffix('')) + "_smart_mask.png"
        
        mask.save(output_path)
        return output_path


class MaskValidator:
    """mask验证器"""
    
    @staticmethod
    def validate_mask(mask_path: str, base_image_path: str) -> bool:
        """
        验证mask是否有效
        
        Args:
            mask_path: mask图像路径
            base_image_path: 基础图像路径
            
        Returns:
            bool: 是否有效
        """
        try:
            with Image.open(mask_path) as mask, Image.open(base_image_path) as base:
                # 检查尺寸是否匹配
                if mask.size != base.size:
                    print(f"⚠️ 警告：mask尺寸 {mask.size} 与基础图像 {base.size} 不匹配")
                    return False
                
                # 检查是否为灰度图
                if mask.mode != 'L':
                    print(f"⚠️ 警告：mask应为灰度图（8位），当前为 {mask.mode}")
                    return False
                
                # 检查是否包含白色区域
                mask_array = np.array(mask)
                if not np.any(mask_array > 0):
                    print("⚠️ 警告：mask不包含任何白色编辑区域")
                    return False
                
                return True
                
        except Exception as e:
            print(f"❌ 验证mask时出错: {e}")
            return False
    
    @staticmethod
    def get_mask_info(mask_path: str) -> dict:
        """
        获取mask信息
        
        Args:
            mask_path: mask图像路径
            
        Returns:
            dict: mask信息
        """
        try:
            with Image.open(mask_path) as mask:
                mask_array = np.array(mask)
                
                # 计算白色像素比例
                white_pixels = np.sum(mask_array > 0)
                total_pixels = mask_array.size
                white_ratio = white_pixels / total_pixels
                
                # 计算白色像素位置
                white_coords = np.where(mask_array > 0)
                if len(white_coords[0]) > 0:
                    min_x, max_x = white_coords[1].min(), white_coords[1].max()
                    min_y, max_y = white_coords[0].min(), white_coords[0].max()
                    bbox = (min_x, min_y, max_x, max_y)
                else:
                    bbox = None
                
                return {
                    "size": mask.size,
                    "mode": mask.mode,
                    "white_pixels": white_pixels,
                    "total_pixels": total_pixels,
                    "white_ratio": white_ratio,
                    "bounding_box": bbox,
                    "is_valid": white_pixels > 0
                }
                
        except Exception as e:
            return {"error": str(e), "is_valid": False}


def create_mask_cli():
    """创建mask的CLI工具"""
    import argparse
    
    parser = argparse.ArgumentParser(description="创建mask图像工具")
    
    parser.add_argument("image_path", help="原始图像路径")
    parser.add_argument("--type", choices=["rectangle", "circle", "ellipse", "polygon"], 
                       default="rectangle", help="mask类型")
    parser.add_argument("--coords", nargs='+', type=int, help="坐标参数")
    parser.add_argument("--output", help="输出mask路径")
    parser.add_argument("--color", nargs=3, type=int, help="智能mask目标颜色RGB")
    parser.add_argument("--tolerance", type=int, default=30, help="颜色容差")
    
    args = parser.parse_args()
    
    creator = MaskCreator()
    
    try:
        if args.type == "rectangle":
            if len(args.coords) != 4:
                print("❌ 矩形mask需要4个参数: x y width height")
                return
            mask_path = creator.create_rectangle_mask(
                args.image_path, *args.coords, args.output
            )
        elif args.type == "circle":
            if len(args.coords) != 3:
                print("❌ 圆形mask需要3个参数: center_x center_y radius")
                return
            mask_path = creator.create_circle_mask(
                args.image_path, *args.coords, args.output
            )
        elif args.type == "ellipse":
            if len(args.coords) != 4:
                print("❌ 椭圆mask需要4个参数: center_x center_y radius_x radius_y")
                return
            mask_path = creator.create_ellipse_mask(
                args.image_path, *args.coords, args.output
            )
        elif args.type == "polygon":
            if len(args.coords) < 6 or len(args.coords) % 2 != 0:
                print("❌ 多边形mask需要至少6个参数: x1 y1 x2 y2 x3 y3 ...")
                return
            points = [(args.coords[i], args.coords[i+1]) for i in range(0, len(args.coords), 2)]
            mask_path = creator.create_polygon_mask(
                args.image_path, points, args.output
            )
        elif args.color:
            mask_path = creator.create_smart_mask(
                args.image_path, tuple(args.color), args.tolerance, args.output
            )
        
        print(f"✅ mask创建成功: {mask_path}")
        
        # 验证mask
        validator = MaskValidator()
        info = validator.get_mask_info(mask_path)
        print(f"📊 mask信息: {info}")
        
    except Exception as e:
        print(f"❌ 创建mask时出错: {e}")


if __name__ == "__main__":
    create_mask_cli()