"""
图像生成数据模型
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class ImageSize(str, Enum):
    """支持的图像尺寸"""
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
    model: str = Field(default="qwen-image", description="模型名称")
    prompt: str = Field(..., description="正向提示词，支持中英文，长度不超过800个字符")
    negative_prompt: Optional[str] = Field(None, description="反向提示词，支持中英文，长度不超过500个字符")
    size: ImageSize = Field(default=ImageSize.SQUARE_1328, description="输出图像的分辨率")
    n: int = Field(default=1, ge=1, le=1, description="生成图片的数量，当前仅支持1张")
    prompt_extend: bool = Field(default=True, description="是否开启prompt智能改写")
    watermark: bool = Field(default=False, description="是否添加水印标识")


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