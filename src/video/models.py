"""
视频生成数据模型
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class ModelType(str, Enum):
    """支持的模型类型"""
    # 文生视频模型 - wan2.6 系列
    WAN2_6_T2V = "wan2.6-t2v"  # 万相 2.6 文生视频（北京）
    WAN2_6_T2V_US = "wan2.6-t2v-us"  # 万相 2.6 文生视频（美国）
    WAN2_5_T2V_PREVIEW = "wan2.5-t2v-preview"  # 万相 2.5 文生视频预览版

    # 文生视频模型 - 旧版
    WAN2_2_T2V_PLUS = "wan2.2-t2v-plus"  # 万相 2.2 专业版文生视频
    WAN2_1_T2V_TURBO = "wanx2.1-t2v-turbo"  # 万相 2.1 极速版文生视频
    WAN2_1_T2V_PLUS = "wanx2.1-t2v-plus"  # 万相 2.1 专业版文生视频

    # 图生视频模型 - wan2.6 系列
    WAN2_6_I2V_FLASH = "wan2.6-i2v-flash"  # 万相 2.6 图生视频极速版
    WAN2_6_I2V = "wan2.6-i2v"  # 万相 2.6 图生视频
    WAN2_6_I2V_US = "wan2.6-i2v-us"  # 万相 2.6 图生视频（美国）
    WAN2_5_I2V_PREVIEW = "wan2.5-i2v-preview"  # 万相 2.5 图生视频预览版

    # 图生视频模型 - 旧版
    WAN2_2_I2V_PLUS = "wan2.2-i2v-plus"  # 万相 2.2 专业版图生视频
    WAN2_2_I2V_FLASH = "wan2.2-i2v-flash"  # 万相 2.2 极速版图生视频
    WAN2_1_I2V_TURBO = "wanx2.1-i2v-turbo"  # 万相 2.1 极速版图生视频
    WAN2_1_I2V_PLUS = "wanx2.1-i2v-plus"  # 万相 2.1 专业版图生视频

    # 首尾帧生视频
    WAN2_2_KF2V_FLASH = "wan2.2-kf2v-flash"  # 万相 2.2 首尾帧生视频（新版）
    WAN2_1_KF2V_PLUS = "wanx2.1-kf2v-plus"  # 万相 2.1 首尾帧生视频（旧版）

    # 视频编辑模型
    WAN2_1_VACE_PLUS = "wanx2.1-vace-plus"  # 万相通用视频编辑
    VIDEO_STYLE_TRANSFORM = "video-style-transform"  # 视频风格重绘

    # 人像视频生成
    ANIMATE_ANYONE = "animate-anyone"  # 舞动人像
    EMO = "emo-v1"  # 悦动人像
    LIVE_PORTRAIT = "liveportrait"  # 灵动人像
    EMOJI = "emoji-v1"  # 表情包
    VIDEO_RETALK = "videoretalk"  # 声动人像


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "PENDING"  # 任务排队中
    RUNNING = "RUNNING"  # 任务处理中
    SUCCEEDED = "SUCCEEDED"  # 任务执行成功
    FAILED = "FAILED"  # 任务执行失败
    CANCELED = "CANCELED"  # 任务取消成功
    UNKNOWN = "UNKNOWN"  # 任务不存在或状态未知


class ShotType(str, Enum):
    """镜头类型（仅 wan2.6 系列支持）"""
    SINGLE = "single"  # 单镜头
    MULTI = "multi"  # 多镜头


class Resolution(str, Enum):
    """视频分辨率档位（图生视频使用）"""
    P480 = "480P"  # 480P 档位
    P720 = "720P"  # 720P 档位
    P1080 = "1080P"  # 1080P 档位


class VideoGenerationRequest(BaseModel):
    """视频生成请求模型"""
    model: str = Field(default=ModelType.WAN2_6_T2V, description="模型名称")

    # 输入内容
    prompt: Optional[str] = Field(None, description="正向提示词，描述视频内容")
    image_url: Optional[str] = Field(None, description="首帧图片 URL（图生视频时必填）")
    first_frame_url: Optional[str] = Field(None, description="首帧图片 URL（首尾帧生视频时使用）")
    # 注意：根据官方文档，若同时提供 first_frame_url、last_frame_url、template，将忽略 last_frame_url
    # 为保持 API 兼容性保留此字段，但实际使用中只需提供 first_frame_url
    last_frame_url: Optional[str] = Field(None, description="尾帧图片 URL（仅供 API 兼容，实际会被忽略）")
    audio_url: Optional[str] = Field(None, description="音频 URL（wan2.5/2.6 系列支持）")
    negative_prompt: Optional[str] = Field(None, description="反向提示词")
    template: Optional[str] = Field(None, description="视频特效模板名称")

    # 参数配置 - 文生视频使用 size，图生视频使用 resolution
    size: Optional[str] = Field(None, description="视频分辨率（文生视频使用，格式：宽*高）")
    resolution: Optional[str] = Field(None, description="视频分辨率档位（图生视频使用：480P/720P/1080P）")
    duration: int = Field(default=5, ge=1, le=15, description="视频时长（秒）")
    prompt_extend: bool = Field(default=True, description="是否开启 prompt 智能改写")
    watermark: bool = Field(default=False, description="是否添加水印标识")
    seed: Optional[int] = Field(None, description="随机数种子")

    # wan2.6-i2v-flash 特有参数
    audio: Optional[bool] = Field(None, description="是否生成有声视频（仅 wan2.6-i2v-flash 支持）")

    # wan2.6 系列特有参数
    shot_type: Optional[str] = Field(None, description="镜头类型：single/multi（仅 wan2.6 系列支持）")

    def validate_for_model(self) -> Dict[str, Any]:
        """根据模型验证参数"""
        errors = []

        # 检查 prompt 长度
        if self.model in ["wan2.6-t2v", "wan2.6-t2v-us", "wan2.5-t2v-preview",
                          "wan2.6-i2v-flash", "wan2.6-i2v", "wan2.6-i2v-us", "wan2.5-i2v-preview"]:
            if self.prompt and len(self.prompt) > 1500:
                errors.append(f"prompt 长度不能超过 1500 个字符，当前长度：{len(self.prompt)}")
        else:
            if self.prompt and len(self.prompt) > 800:
                errors.append(f"prompt 长度不能超过 800 个字符，当前长度：{len(self.prompt)}")

        # 文生视频模型验证
        t2v_models = ["wan2.6-t2v", "wan2.6-t2v-us", "wan2.5-t2v-preview",
                      ModelType.WAN2_2_T2V_PLUS, ModelType.WAN2_1_T2V_TURBO, ModelType.WAN2_1_T2V_PLUS]
        if self.model in t2v_models:
            if not self.prompt:
                errors.append("文生视频需要提供 prompt 参数")

        # 图生视频模型验证
        i2v_models = ["wan2.6-i2v-flash", "wan2.6-i2v", "wan2.6-i2v-us", "wan2.5-i2v-preview",
                      ModelType.WAN2_2_I2V_PLUS, ModelType.WAN2_2_I2V_FLASH,
                      ModelType.WAN2_1_I2V_TURBO, ModelType.WAN2_1_I2V_PLUS]
        if self.model in i2v_models:
            if not self.image_url:
                errors.append("图生视频需要提供 image_url 参数")
            # 使用特效模板时，prompt 可以不填
            if not self.prompt and not self.template:
                errors.append("图生视频需要提供 prompt 参数或 template 参数")

        # 首尾帧生视频验证
        kf2v_models = [ModelType.WAN2_1_KF2V_PLUS, "wan2.2-kf2v-flash"]
        if self.model in kf2v_models:
            if not self.first_frame_url:
                errors.append("首尾帧生视频需要提供 first_frame_url 参数")
            # 使用特效模板时，只需要 first_frame_url + template
            if self.template:
                # 特效模式：只需要首帧图像 + template
                pass
            else:
                # 普通模式：需要首帧图像 + 尾帧图像 + prompt
                if not self.last_frame_url:
                    errors.append("首尾帧生视频普通模式需要提供 last_frame_url 参数（或使用 template 指定特效）")
                if not self.prompt:
                    errors.append("首尾帧生视频需要提供 prompt 参数（或使用 template 指定特效）")

        # 时长验证（不同模型支持不同）
        # wan2.6 文生视频
        if self.model == "wan2.6-t2v":
            if not (2 <= self.duration <= 15):
                errors.append(f"wan2.6-t2v 时长必须在 2-15 秒之间，当前：{self.duration}")
        # wan2.6-i2v-flash
        elif self.model == "wan2.6-i2v-flash":
            if not (2 <= self.duration <= 15):
                errors.append(f"wan2.6-i2v-flash 时长必须在 2-15 秒之间，当前：{self.duration}")
        # wan2.6-i2v
        elif self.model == "wan2.6-i2v":
            if not (2 <= self.duration <= 15):
                errors.append(f"wan2.6-i2v 时长必须在 2-15 秒之间，当前：{self.duration}")
        # wan2.6-t2v-us / wan2.6-i2v-us
        elif self.model in ["wan2.6-t2v-us", "wan2.6-i2v-us"]:
            if self.duration not in [5, 10, 15]:
                errors.append(f"{self.model} 时长只能为 5、10 或 15 秒，当前：{self.duration}")
        # wan2.5 系列
        elif self.model in ["wan2.5-t2v-preview", "wan2.5-i2v-preview"]:
            if self.duration not in [5, 10]:
                errors.append(f"{self.model} 时长只能为 5 或 10 秒，当前：{self.duration}")
        # wan2.2 / wanx2.1 系列（固定 5 秒）
        elif self.model in [ModelType.WAN2_2_T2V_PLUS, ModelType.WAN2_2_I2V_PLUS,
                            ModelType.WAN2_2_I2V_FLASH, ModelType.WAN2_1_T2V_TURBO,
                            ModelType.WAN2_1_T2V_PLUS, ModelType.WAN2_1_I2V_TURBO,
                            ModelType.WAN2_1_I2V_PLUS]:
            if self.duration != 5:
                errors.append(f"{self.model} 时长固定为 5 秒，不支持修改")
        # wanx2.1-i2v-turbo 特殊
        elif self.model == ModelType.WAN2_1_I2V_TURBO:
            if self.duration not in [3, 4, 5]:
                errors.append(f"wanx2.1-i2v-turbo 时长只能为 3、4 或 5 秒，当前：{self.duration}")

        # 首尾帧生视频 - 时长固定为5秒
        elif self.model in [ModelType.WAN2_1_KF2V_PLUS, "wan2.2-kf2v-flash"]:
            if self.duration != 5:
                errors.append(f"{self.model} 时长固定为 5 秒，不支持修改")

        # shot_type 仅 wan2.6 系列支持
        if self.shot_type and not self.model.startswith("wan2.6"):
            errors.append("shot_type 参数仅 wan2.6 系列模型支持")

        # audio 参数仅 wan2.6-i2v-flash 支持
        if self.audio is not None and self.model != "wan2.6-i2v-flash":
            errors.append("audio 参数仅 wan2.6-i2v-flash 模型支持")

        # 图像 URL 验证
        if self.image_url and not self.image_url.startswith(("http://", "https://", "file://", "data:", "oss://")):
            errors.append("image_url 必须是有效的 URL（http/https/file/data/oss）")

        return {"valid": len(errors) == 0, "errors": errors}


class VideoResult(BaseModel):
    """视频结果模型"""
    url: str = Field(..., description="模型生成视频的 URL 地址，有效期为 24 小时")
    cover_url: Optional[str] = Field(None, description="视频封面图 URL")
    duration: Optional[float] = Field(None, description="视频时长（秒）")
    resolution: Optional[str] = Field(None, description="视频分辨率")
    orig_prompt: Optional[str] = Field(None, description="原始提示词")
    actual_prompt: Optional[str] = Field(None, description="智能改写后的提示词")
    code: Optional[str] = Field(None, description="错误码，部分任务执行失败时会返回该字段")
    message: Optional[str] = Field(None, description="错误信息，部分任务执行失败时会返回该字段")


class VideoGenerationResponse(BaseModel):
    """视频生成响应模型"""
    task_id: Optional[str] = Field(None, description="任务 ID")
    task_status: Optional[TaskStatus] = Field(None, description="任务状态")
    submit_time: Optional[str] = Field(None, description="任务提交时间")
    scheduled_time: Optional[str] = Field(None, description="任务执行时间")
    end_time: Optional[str] = Field(None, description="任务完成时间")
    video_url: Optional[str] = Field(None, description="视频 URL（成功时返回）")
    orig_prompt: Optional[str] = Field(None, description="原始提示词")
    actual_prompt: Optional[str] = Field(None, description="智能改写后的提示词")
    usage: Optional[Dict[str, Any]] = Field(None, description="使用量信息")
    request_id: str = Field(..., description="请求唯一标识")
    error_code: Optional[str] = Field(None, description="错误码（失败时返回）")
    error_message: Optional[str] = Field(None, description="错误信息（失败时返回）")


class TaskCreationResponse(BaseModel):
    """任务创建响应模型"""
    task_id: str = Field(..., description="任务 ID")
    task_status: TaskStatus = Field(..., description="初始任务状态")
    request_id: str = Field(..., description="请求唯一标识")


class VideoGenerationError(BaseModel):
    """错误响应模型"""
    code: str = Field(..., description="错误码")
    message: str = Field(..., description="错误信息")
    request_id: Optional[str] = Field(None, description="请求唯一标识")
