"""
图像生成数据模型
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class ModelType(str, Enum):
    """支持的模型类型"""
    QWEN = "qwen-image"  # 通义千问文生图
    WAN2_2_FLASH = "wan2.2-t2i-flash"  # 万相2.2极速版
    WAN2_2_PLUS = "wan2.2-t2i-plus"  # 万相2.2专业版
    WAN2_1_TURBO = "wanx2.1-t2i-turbo"  # 万相2.1极速版
    WAN2_1_PLUS = "wanx2.1-t2i-plus"  # 万相2.1专业版
    WAN2_0_TURBO = "wanx2.0-t2i-turbo"  # 万相2.0极速版


class ImageSize(str, Enum):
    """千问模型支持的固定尺寸"""
    SQUARE_1328 = "1328*1328"  # 1:1 默认
    WIDESCREEN_1664 = "1664*928"  # 16:9
    LANDSCAPE_1472 = "1472*1140"  # 4:3
    PORTRAIT_1140 = "1140*1472"  # 3:4
    TALL_928 = "928*1664"  # 9:16


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "PENDING"  # 任务排队中
    RUNNING = "RUNNING"  # 任务处理中
    SUCCEEDED = "SUCCEEDED"  # 任务执行成功
    FAILED = "FAILED"  # 任务执行失败
    CANCELED = "CANCELED"  # 任务取消成功
    UNKNOWN = "UNKNOWN"  # 任务不存在或状态未知


class ImageGenerationRequest(BaseModel):
    """图像生成请求模型"""
    model: str = Field(default=ModelType.WAN2_2_FLASH, description="模型名称")
    prompt: str = Field(..., description="正向提示词，支持中英文，长度不超过800个字符")
    negative_prompt: Optional[str] = Field(None, description="反向提示词，支持中英文，长度不超过500个字符")
    size: str = Field(default="1024*1024", description="输出图像的分辨率")
    n: int = Field(default=1, ge=1, le=4, description="生成图片的数量，万相支持1-4张，千问仅支持1张")
    prompt_extend: bool = Field(default=True, description="是否开启prompt智能改写")
    watermark: bool = Field(default=False, description="是否添加水印标识")
    seed: Optional[int] = Field(None, description="随机数种子，用于控制生成内容的随机性")

    def validate_for_model(self) -> Dict[str, Any]:
        """根据模型验证参数"""
        errors = []
        
        # 千问模型特殊限制
        if self.model == ModelType.QWEN:
            # 检查尺寸
            valid_qwen_sizes = ["1328*1328", "1664*928", "1472*1140", "1140*1472", "928*1664"]
            if self.size not in valid_qwen_sizes:
                errors.append(f"千问模型仅支持尺寸: {', '.join(valid_qwen_sizes)}")
            
            # 检查图片数量
            if self.n != 1:
                errors.append("千问模型仅支持生成1张图片")
        
        # 万相模型尺寸范围验证
        elif self.model.startswith("wan"):
            try:
                width, height = map(int, self.size.split("*"))
                if not (512 <= width <= 1440 and 512 <= height <= 1440):
                    errors.append("万相模型尺寸范围：512-1440像素")
                if width * height > 2000000:
                    errors.append("万相模型分辨率不超过200万像素")
            except ValueError:
                errors.append("尺寸格式错误，应为 宽*高")
        
        return {"valid": len(errors) == 0, "errors": errors}


class ImageResult(BaseModel):
    """图像结果模型"""
    orig_prompt: str = Field(..., description="原始的输入prompt")
    actual_prompt: Optional[str] = Field(None, description="开启prompt智能改写后，实际使用的prompt")
    url: str = Field(..., description="模型生成图片的URL地址，有效期为24小时")
    code: Optional[str] = Field(None, description="错误码，部分任务执行失败时会返回该字段")
    message: Optional[str] = Field(None, description="错误信息，部分任务执行失败时会返回该字段")


class ImageResult(BaseModel):
    """图像结果模型"""
    orig_prompt: str = Field(..., description="原始的输入prompt")
    actual_prompt: Optional[str] = Field(None, description="开启prompt智能改写后，实际使用的prompt")
    url: str = Field(..., description="模型生成图片的URL地址，有效期为24小时")
    code: Optional[str] = Field(None, description="错误码，部分任务执行失败时会返回该字段")
    message: Optional[str] = Field(None, description="错误信息，部分任务执行失败时会返回该字段")


class ImageGenerationResponse(BaseModel):
    """图像生成响应模型"""
    task_id: str = Field(..., description="任务ID")
    task_status: TaskStatus = Field(..., description="任务状态")
    submit_time: Optional[str] = Field(None, description="任务提交时间")
    scheduled_time: Optional[str] = Field(None, description="任务执行时间")
    end_time: Optional[str] = Field(None, description="任务完成时间")
    results: Optional[List[ImageResult]] = Field(None, description="任务结果列表")
    image_count: Optional[int] = Field(None, description="模型生成图片的数量")
    request_id: str = Field(..., description="请求唯一标识")


class TaskCreationResponse(BaseModel):
    """任务创建响应模型"""
    task_id: str = Field(..., description="任务ID")
    task_status: TaskStatus = Field(..., description="初始任务状态")
    request_id: str = Field(..., description="请求唯一标识")


class ImageGenerationError(BaseModel):
    """错误响应模型"""
    code: str = Field(..., description="错误码")
    message: str = Field(..., description="错误信息")
    request_id: Optional[str] = Field(None, description="请求唯一标识")