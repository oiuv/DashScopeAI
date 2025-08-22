"""
图像生成数据模型
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class ModelType(str, Enum):
    """支持的模型类型"""
    QWEN = "qwen-image"  # 通义千问文生图
    QWEN_EDIT = "qwen-image-edit"  # 通义千问图像编辑
    WAN2_2_FLASH = "wan2.2-t2i-flash"  # 万相2.2极速版
    WAN2_2_PLUS = "wan2.2-t2i-plus"  # 万相2.2专业版
    WAN2_1_TURBO = "wanx2.1-t2i-turbo"  # 万相2.1极速版
    WAN2_1_PLUS = "wanx2.1-t2i-plus"  # 万相2.1专业版
    WAN2_0_TURBO = "wanx2.0-t2i-turbo"  # 万相2.0极速版
    WANX_EDIT = "wanx2.1-imageedit"  # 万相通用图像编辑


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


class WanxEditFunction(str, Enum):
    """万相图像编辑功能类型"""
    STYLIZATION_ALL = "stylization_all"  # 全局风格化
    STYLIZATION_LOCAL = "stylization_local"  # 局部风格化
    DESCRIPTION_EDIT = "description_edit"  # 指令编辑
    DESCRIPTION_EDIT_WITH_MASK = "description_edit_with_mask"  # 局部重绘
    REMOVE_WATERMARK = "remove_watermark"  # 去水印
    EXPAND = "expand"  # 扩图
    SUPER_RESOLUTION = "super_resolution"  # 超分
    COLORIZATION = "colorization"  # 上色
    DOODLE = "doodle"  # 线稿生图
    CONTROL_CARTOON_FEATURE = "control_cartoon_feature"  # 参考卡通生图


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
        elif self.model.startswith("wan") and self.model != ModelType.WANX_EDIT:
            try:
                width, height = map(int, self.size.split("*"))
                if not (512 <= width <= 1440 and 512 <= height <= 1440):
                    errors.append("万相模型尺寸范围：512-1440像素")
                if width * height > 2000000:
                    errors.append("万相模型分辨率不超过200万像素")
            except ValueError:
                errors.append("尺寸格式错误，应为 宽*高")
        
        return {"valid": len(errors) == 0, "errors": errors}


class ImageEditRequest(BaseModel):
    """图像编辑请求模型"""
    model: str = Field(..., description="模型名称")
    prompt: str = Field(..., description="编辑提示词，≤800字符")
    image_url: str = Field(..., description="输入图像URL或Base64")
    negative_prompt: Optional[str] = Field(None, description="反向提示词，≤500字符")
    watermark: bool = Field(default=False, description="是否添加水印")
    
    # 千问模型专用
    messages: Optional[List[Dict[str, Any]]] = Field(None, description="千问模型的对话格式")
    
    # 万相模型专用
    function: Optional[str] = Field(None, description="万相编辑功能类型")
    mask_image_url: Optional[str] = Field(None, description="局部重绘的mask图像")
    n: int = Field(default=1, ge=1, le=4, description="生成数量")
    seed: Optional[int] = Field(None, description="随机种子")

    def validate_for_model(self) -> Dict[str, Any]:
        """根据模型验证参数"""
        errors = []
        
        if self.model == ModelType.QWEN_EDIT:
            # 千问编辑模型验证
            if not self.messages and not (self.image_url and self.prompt):
                errors.append("千问编辑需要提供messages或image_url+prompt")
        
        elif self.model == ModelType.WANX_EDIT:
            # 万相编辑模型验证
            if not self.function:
                errors.append("万相编辑需要指定function参数")
            if self.function == WanxEditFunction.DESCRIPTION_EDIT_WITH_MASK and not self.mask_image_url:
                errors.append("局部重绘功能需要提供mask_image_url")
        
        return {"valid": len(errors) == 0, "errors": errors}


class ImageResult(BaseModel):
    """图像结果模型"""
    url: str = Field(..., description="模型生成图片的URL地址，有效期为24小时")
    orig_prompt: Optional[str] = Field(None, description="原始的输入prompt")
    actual_prompt: Optional[str] = Field(None, description="开启prompt智能改写后，实际使用的prompt")
    code: Optional[str] = Field(None, description="错误码，部分任务执行失败时会返回该字段")
    message: Optional[str] = Field(None, description="错误信息，部分任务执行失败时会返回该字段")


class ImageGenerationResponse(BaseModel):
    """图像生成响应模型"""
    task_id: Optional[str] = Field(None, description="任务ID")
    task_status: Optional[TaskStatus] = Field(None, description="任务状态")
    submit_time: Optional[str] = Field(None, description="任务提交时间")
    scheduled_time: Optional[str] = Field(None, description="任务执行时间")
    end_time: Optional[str] = Field(None, description="任务完成时间")
    results: Optional[List[ImageResult]] = Field(None, description="任务结果列表")
    image_count: Optional[int] = Field(None, description="模型生成图片的数量")
    request_id: str = Field(..., description="请求唯一标识")


class ImageEditResponse(BaseModel):
    """图像编辑响应模型"""
    task_id: Optional[str] = Field(None, description="任务ID（万相模型）")
    task_status: Optional[TaskStatus] = Field(None, description="任务状态")
    choices: Optional[List[Dict[str, Any]]] = Field(None, description="千问模型的选择结果")
    results: Optional[List[ImageResult]] = Field(None, description="任务结果列表")
    url: Optional[str] = Field(None, description="编辑后图像URL（千问模型）")
    request_id: str = Field(..., description="请求唯一标识")
    error: Optional[Dict[str, str]] = Field(None, description="错误信息")


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


class StyleRepaintRequest(BaseModel):
    """人像风格重绘请求模型"""
    model: str = Field(default="wanx-style-repaint-v1", description="模型名称")
    image_url: str = Field(..., description="输入人物图像URL或Base64")
    style_index: int = Field(..., description="风格选择：-1为自定义风格，其他为预置风格编号")
    style_ref_url: Optional[str] = Field(None, description="自定义风格参考图URL，仅style_index=-1时必填")
    
    def validate_style_params(self) -> Dict[str, Any]:
        """验证风格参数"""
        errors = []
        
        # 预置风格验证
        valid_style_indices = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 14, 15, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40]
        
        if self.style_index == -1:
            # 自定义风格模式
            if not self.style_ref_url:
                errors.append("自定义风格模式(style_index=-1)必须提供style_ref_url参数")
        else:
            # 预置风格模式
            if self.style_index not in valid_style_indices:
                errors.append(f"无效的风格编号: {self.style_index}，有效值为: {valid_style_indices}")
            if self.style_ref_url:
                errors.append("预置风格模式下不应提供style_ref_url参数")
        
        return {"valid": len(errors) == 0, "errors": errors}


class StyleRepaintResponse(BaseModel):
    """人像风格重绘响应模型"""
    task_id: str = Field(..., description="任务ID")
    task_status: TaskStatus = Field(..., description="初始任务状态")
    request_id: str = Field(..., description="请求唯一标识")