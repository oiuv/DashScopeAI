"""
视频生成模块
支持文生视频、图生视频、首尾帧生视频等功能
"""

from .models import (
    ModelType,
    TaskStatus,
    VideoGenerationRequest,
    VideoGenerationResponse,
    VideoResult,
    TaskCreationResponse,
    VideoGenerationError,
    Resolution,
)

from .text2video import VideoGenerator

__all__ = [
    # 生成器
    "VideoGenerator",
    # 数据模型
    "ModelType",
    "TaskStatus",
    "VideoGenerationRequest",
    "VideoGenerationResponse",
    "VideoResult",
    "TaskCreationResponse",
    "VideoGenerationError",
    "Resolution",
]
