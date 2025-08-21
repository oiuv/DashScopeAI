"""
图像编辑模块
支持通义千问-图像编辑和通义万相-通用图像编辑
"""

from typing import Optional, Dict, Any
import httpx
import os
import time
from pathlib import Path
from urllib.parse import urlparse

from .models import (
    ImageEditRequest,
    ImageEditResponse,
    TaskCreationResponse,
    TaskStatus,
    ModelType,
    WanxEditFunction
)


class ImageEditor:
    """图像编辑器 - 支持千问和万相模型"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://dashscope.aliyuncs.com/api/v1",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        初始化图像编辑器
        
        Args:
            api_key: 阿里云百炼API密钥
            base_url: API基础URL
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
        """
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("API密钥不能为空，请设置api_key参数或环境变量DASHSCOPE_API_KEY")
            
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def edit_image_qwen(
        self,
        image_url: str,
        prompt: str,
        negative_prompt: Optional[str] = None,
        watermark: bool = False
    ) -> ImageEditResponse:
        """
        使用通义千问-图像编辑模型（同步接口）
        
        Args:
            image_url: 输入图像URL或Base64
            prompt: 编辑指令
            negative_prompt: 反向提示词
            watermark: 是否添加水印
            
        Returns:
            ImageEditResponse: 编辑结果
        """
        url = f"{self.base_url}/services/aigc/multimodal-generation/generation"
        
        payload = {
            "model": ModelType.QWEN_EDIT,
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"image": image_url},
                            {"text": prompt}
                        ]
                    }
                ]
            },
            "parameters": {
                "negative_prompt": negative_prompt or "",
                "watermark": watermark
            }
        }
        
        with httpx.Client(timeout=self.timeout) as client:
            for attempt in range(self.max_retries):
                try:
                    response = client.post(url, headers=self.headers, json=payload)
                    response.raise_for_status()
                    
                    data = response.json()
                    return ImageEditResponse(
                        choices=data["output"]["choices"],
                        url=data["output"]["choices"][0]["message"]["content"][0]["image"],
                        request_id=data["request_id"]
                    )
                    
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 429 and attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    raise
                except Exception as e:
                    if attempt < self.max_retries - 1:
                        time.sleep(1)
                        continue
                    raise
    
    def create_edit_task_wanx(
        self,
        function: str,
        prompt: str,
        base_image_url: str,
        mask_image_url: Optional[str] = None,
        n: int = 1,
        seed: Optional[int] = None,
        watermark: bool = False,
        strength: Optional[float] = None,
        top_scale: Optional[float] = None,
        bottom_scale: Optional[float] = None,
        left_scale: Optional[float] = None,
        right_scale: Optional[float] = None,
        upscale_factor: Optional[int] = None,
        is_sketch: Optional[bool] = None
    ) -> TaskCreationResponse:
        """
        创建万相图像编辑任务（异步接口）
        
        Args:
            function: 编辑功能类型
            prompt: 编辑提示词
            base_image_url: 基础图像URL
            mask_image_url: mask图像URL（局部重绘时需要）
            n: 生成数量
            seed: 随机种子
            watermark: 是否添加水印
            strength: 图像修改幅度，用于全局风格化和指令编辑
            top_scale: 向上扩展比例，用于扩图功能
            bottom_scale: 向下扩展比例，用于扩图功能
            left_scale: 向左扩展比例，用于扩图功能
            right_scale: 向右扩展比例，用于扩图功能
            upscale_factor: 放大倍数，用于超分辨率功能
            is_sketch: 输入是否为线稿，用于线稿生图功能
            
        Returns:
            TaskCreationResponse: 任务创建响应
        """
        url = f"{self.base_url}/services/aigc/image2image/image-synthesis"
        
        payload = {
            "model": ModelType.WANX_EDIT,
            "input": {
                "function": function,
                "prompt": prompt,
                "base_image_url": base_image_url
            },
            "parameters": {
                "n": n,
                "watermark": watermark
            }
        }
        
        if mask_image_url:
            payload["input"]["mask_image_url"] = mask_image_url
        if seed is not None:
            payload["parameters"]["seed"] = seed
        if strength is not None:
            payload["parameters"]["strength"] = strength
        if top_scale is not None and function == "expand":
            payload["parameters"]["top_scale"] = top_scale
        if bottom_scale is not None and function == "expand":
            payload["parameters"]["bottom_scale"] = bottom_scale
        if left_scale is not None and function == "expand":
            payload["parameters"]["left_scale"] = left_scale
        if right_scale is not None and function == "expand":
            payload["parameters"]["right_scale"] = right_scale
        if upscale_factor is not None and function == "super_resolution":
            payload["parameters"]["upscale_factor"] = upscale_factor
        if is_sketch is not None and function == "doodle":
            payload["parameters"]["is_sketch"] = is_sketch
        
        headers = self.headers.copy()
        headers["X-DashScope-Async"] = "enable"
        
        with httpx.Client(timeout=self.timeout) as client:
            for attempt in range(self.max_retries):
                try:
                    response = client.post(url, headers=headers, json=payload)
                    response.raise_for_status()
                    
                    data = response.json()
                    return TaskCreationResponse(
                        task_id=data["output"]["task_id"],
                        task_status=TaskStatus(data["output"]["task_status"]),
                        request_id=data["request_id"]
                    )
                    
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 429 and attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    raise
                except Exception as e:
                    if attempt < self.max_retries - 1:
                        time.sleep(1)
                        continue
                    raise
    
    def get_task_result(self, task_id: str) -> ImageEditResponse:
        """
        获取万相编辑任务结果
        
        Args:
            task_id: 任务ID
            
        Returns:
            ImageEditResponse: 任务结果
        """
        url = f"{self.base_url}/tasks/{task_id}"
        
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(url, headers={"Authorization": f"Bearer {self.api_key}"})
            response.raise_for_status()
            
            data = response.json()
            output = data["output"]
            
            results = None
            if "results" in output and output["results"]:
                from .models import ImageResult
                results = [
                    ImageResult(
                        orig_prompt="",
                        url=result["url"],
                        code=result.get("code"),
                        message=result.get("message")
                    )
                    for result in output["results"]
                ]
            
            return ImageEditResponse(
                task_id=output["task_id"],
                task_status=TaskStatus(output["task_status"]),
                results=results,
                request_id=data["request_id"]
            )
    
    def wait_for_completion(
        self,
        task_id: str,
        poll_interval: float = 3.0,
        timeout: float = 300.0
    ) -> ImageEditResponse:
        """
        等待万相编辑任务完成
        
        Args:
            task_id: 任务ID
            poll_interval: 轮询间隔（秒）
            timeout: 超时时间（秒）
            
        Returns:
            ImageEditResponse: 最终任务结果
        """
        start_time = time.time()
        
        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"任务 {task_id} 超时，等待时间超过 {timeout} 秒")
            
            result = self.get_task_result(task_id)
            
            if result.task_status == TaskStatus.SUCCEEDED:
                return result
            elif result.task_status == TaskStatus.FAILED:
                raise Exception(f"任务 {task_id} 执行失败")
            elif result.task_status == TaskStatus.CANCELED:
                raise Exception(f"任务 {task_id} 已取消")
            
            time.sleep(poll_interval)
    
    def edit_image(
        self,
        model: str,
        image_url: str,
        prompt: str,
        function: Optional[str] = None,
        mask_image_url: Optional[str] = None,
        negative_prompt: Optional[str] = None,
        n: int = 1,
        seed: Optional[int] = None,
        watermark: bool = False,
        strength: Optional[float] = None,
        top_scale: Optional[float] = None,
        bottom_scale: Optional[float] = None,
        left_scale: Optional[float] = None,
        right_scale: Optional[float] = None,
        upscale_factor: Optional[int] = None,
        is_sketch: Optional[bool] = None
    ) -> ImageEditResponse:
        """
        统一图像编辑接口
        
        Args:
            model: 模型名称 qwen-image-edit 或 wanx2.1-imageedit
            image_url: 输入图像URL
            prompt: 编辑提示词
            function: 万相编辑功能类型
            mask_image_url: mask图像URL（万相局部重绘）
            negative_prompt: 反向提示词
            n: 生成数量
            seed: 随机种子
            watermark: 是否添加水印
            strength: 图像修改幅度，用于全局风格化和指令编辑
            top_scale: 向上扩展比例，用于扩图功能
            bottom_scale: 向下扩展比例，用于扩图功能
            left_scale: 向左扩展比例，用于扩图功能
            right_scale: 向右扩展比例，用于扩图功能
            upscale_factor: 放大倍数，用于超分辨率功能
            is_sketch: 输入是否为线稿，用于线稿生图功能
            
        Returns:
            ImageEditResponse: 编辑结果
        """
        if model == ModelType.QWEN_EDIT:
            # 千问同步接口
            return self.edit_image_qwen(
                image_url=image_url,
                prompt=prompt,
                negative_prompt=negative_prompt,
                watermark=watermark
            )
        elif model == ModelType.WANX_EDIT:
            # 万相异步接口
            task = self.create_edit_task_wanx(
                function=function,
                prompt=prompt,
                base_image_url=image_url,
                mask_image_url=mask_image_url,
                n=n,
                seed=seed,
                watermark=watermark,
                strength=strength,
                top_scale=top_scale,
                bottom_scale=bottom_scale,
                left_scale=left_scale,
                right_scale=right_scale,
                upscale_factor=upscale_factor,
                is_sketch=is_sketch
            )
            return self.wait_for_completion(task.task_id)
        else:
            raise ValueError(f"不支持的编辑模型: {model}")
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """
        将本地图像编码为Base64
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            str: Base64编码的图像
        """
        import base64
        import mimetypes
        
        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type:
            mime_type = "image/jpeg"
        
        with open(image_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode('utf-8')
        
        return f"data:{mime_type};base64,{encoded}"
    
    def is_url(self, path: str) -> bool:
        """判断是否为URL"""
        try:
            result = urlparse(path)
            return bool(result.scheme and result.netloc)
        except:
            return False
    
    def download_image(
        self,
        url: str,
        save_path: str,
        filename: Optional[str] = None
    ) -> str:
        """
        下载编辑后的图像
        
        Args:
            url: 图像URL
            save_path: 保存目录
            filename: 文件名
            
        Returns:
            str: 保存的文件路径
        """
        if filename is None:
            from urllib.parse import unquote
            filename = unquote(urlparse(url).path.split('/')[-1])
        
        save_dir = Path(save_path)
        save_dir.mkdir(parents=True, exist_ok=True)
        file_path = save_dir / filename
        
        with httpx.Client() as client:
            response = client.get(url)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
        
        return str(file_path)


class QwenImageEditor:
    """通义千问图像编辑专用类"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.editor = ImageEditor(api_key=api_key)
    
    def edit(self, image_url: str, prompt: str, **kwargs) -> ImageEditResponse:
        """使用千问模型编辑图像"""
        return self.editor.edit_image_qwen(
            image_url=image_url,
            prompt=prompt,
            **kwargs
        )


class WanxImageEditor:
    """通义万相图像编辑专用类"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.editor = ImageEditor(api_key=api_key)
    
    def stylization_all(self, image_url: str, prompt: str, **kwargs) -> ImageEditResponse:
        """全局风格化"""
        return self.editor.edit_image(
            model=ModelType.WANX_EDIT,
            image_url=image_url,
            prompt=prompt,
            function=WanxEditFunction.STYLIZATION_ALL,
            **kwargs
        )
    
    def stylization_local(self, image_url: str, prompt: str, **kwargs) -> ImageEditResponse:
        """局部风格化"""
        return self.editor.edit_image(
            model=ModelType.WANX_EDIT,
            image_url=image_url,
            prompt=prompt,
            function=WanxEditFunction.STYLIZATION_LOCAL,
            **kwargs
        )
    
    def description_edit(self, image_url: str, prompt: str, **kwargs) -> ImageEditResponse:
        """指令编辑"""
        return self.editor.edit_image(
            model=ModelType.WANX_EDIT,
            image_url=image_url,
            prompt=prompt,
            function=WanxEditFunction.DESCRIPTION_EDIT,
            **kwargs
        )
    
    def description_edit_with_mask(
        self,
        image_url: str,
        mask_image_url: str,
        prompt: str,
        **kwargs
    ) -> ImageEditResponse:
        """局部重绘"""
        return self.editor.edit_image(
            model=ModelType.WANX_EDIT,
            image_url=image_url,
            prompt=prompt,
            function=WanxEditFunction.DESCRIPTION_EDIT_WITH_MASK,
            mask_image_url=mask_image_url,
            **kwargs
        )
    
    def remove_watermark(self, image_url: str, prompt: str = "去除水印", **kwargs) -> ImageEditResponse:
        """去水印"""
        return self.editor.edit_image(
            model=ModelType.WANX_EDIT,
            image_url=image_url,
            prompt=prompt,
            function=WanxEditFunction.REMOVE_WATERMARK,
            **kwargs
        )
    
    def expand(self, image_url: str, prompt: str, **kwargs) -> ImageEditResponse:
        """扩图"""
        return self.editor.edit_image(
            model=ModelType.WANX_EDIT,
            image_url=image_url,
            prompt=prompt,
            function=WanxEditFunction.EXPAND,
            **kwargs
        )
    
    def super_resolution(self, image_url: str, prompt: str = "高清放大", **kwargs) -> ImageEditResponse:
        """超分辨率"""
        return self.editor.edit_image(
            model=ModelType.WANX_EDIT,
            image_url=image_url,
            prompt=prompt,
            function=WanxEditFunction.SUPER_RESOLUTION,
            **kwargs
        )
    
    def colorization(self, image_url: str, prompt: str, **kwargs) -> ImageEditResponse:
        """上色"""
        return self.editor.edit_image(
            model=ModelType.WANX_EDIT,
            image_url=image_url,
            prompt=prompt,
            function=WanxEditFunction.COLORIZATION,
            **kwargs
        )
    
    def doodle(self, image_url: str, prompt: str, **kwargs) -> ImageEditResponse:
        """线稿生图"""
        return self.editor.edit_image(
            model=ModelType.WANX_EDIT,
            image_url=image_url,
            prompt=prompt,
            function=WanxEditFunction.DOODLE,
            **kwargs
        )
    
    def control_cartoon_feature(self, image_url: str, prompt: str, **kwargs) -> ImageEditResponse:
        """参考卡通生图"""
        return self.editor.edit_image(
            model=ModelType.WANX_EDIT,
            image_url=image_url,
            prompt=prompt,
            function=WanxEditFunction.CONTROL_CARTOON_FEATURE,
            **kwargs
        )