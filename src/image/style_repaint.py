"""
人像风格重绘功能
基于阿里云百炼人像风格重绘API
"""

from typing import Optional, Dict, Any
import httpx
import os
import time
from pathlib import Path

from .models import (
    StyleRepaintRequest,
    StyleRepaintResponse,
    ImageGenerationResponse,
    TaskStatus,
    ImageResult
)


class StyleRepaintGenerator:
    """人像风格重绘生成器"""
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        base_url: str = "https://dashscope.aliyuncs.com/api/v1",
        timeout: int = 30,
        max_retries: int = 3,
        poll_interval: float = 3.0
    ):
        """
        初始化人像风格重绘生成器
        
        Args:
            api_key: 阿里云百炼API密钥，如果为None则从环境变量DASHSCOPE_API_KEY获取
            base_url: API基础URL
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
            poll_interval: 轮询间隔时间（秒）
        """
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("API密钥不能为空，请设置api_key参数或环境变量DASHSCOPE_API_KEY")
            
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.poll_interval = poll_interval
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable"
        }
        
    def repaint_with_preset_style(
        self, 
        image_url: str, 
        style_index: int
    ) -> StyleRepaintResponse:
        """
        使用预置风格进行人像风格重绘
        
        Args:
            image_url: 输入人物图像URL或Base64字符串
            style_index: 预置风格编号（0-40之间的有效值）
            
        Returns:
            StyleRepaintResponse: 包含任务ID的响应对象
            
        Raises:
            ValueError: 参数验证失败
            httpx.HTTPError: API调用失败
        """
        request = StyleRepaintRequest(
            image_url=image_url,
            style_index=style_index
        )
        
        # 验证参数
        validation = request.validate_style_params()
        if not validation["valid"]:
            raise ValueError("; ".join(validation["errors"]))
            
        return self._create_task(request)
        
    def repaint_with_custom_style(
        self, 
        image_url: str, 
        style_ref_url: str
    ) -> StyleRepaintResponse:
        """
        使用自定义风格进行人像风格重绘
        
        Args:
            image_url: 输入人物图像URL或Base64字符串
            style_ref_url: 自定义风格参考图URL或Base64字符串
            
        Returns:
            StyleRepaintResponse: 包含任务ID的响应对象
            
        Raises:
            ValueError: 参数验证失败
            httpx.HTTPError: API调用失败
        """
        request = StyleRepaintRequest(
            image_url=image_url,
            style_index=-1,
            style_ref_url=style_ref_url
        )
        
        # 验证参数
        validation = request.validate_style_params()
        if not validation["valid"]:
            raise ValueError("; ".join(validation["errors"]))
            
        return self._create_task(request)
        
    def _create_task(self, request: StyleRepaintRequest) -> StyleRepaintResponse:
        """创建风格重绘任务"""
        url = f"{self.base_url}/services/aigc/image-generation/generation"
        
        # 构建请求体
        payload = {
            "model": request.model,
            "input": {
                "image_url": request.image_url
            }
        }
        
        # 根据风格模式设置参数
        if request.style_index == -1:
            # 自定义风格模式
            payload["input"]["style_ref_url"] = request.style_ref_url
            payload["input"]["style_index"] = -1
        else:
            # 预置风格模式
            payload["input"]["style_index"] = request.style_index
            
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, headers=self.headers, json=payload)
                response.raise_for_status()
                
                data = response.json()
                return StyleRepaintResponse(
                    task_id=data["output"]["task_id"],
                    task_status=TaskStatus(data["output"]["task_status"]),
                    request_id=data["request_id"]
                )
                
        except httpx.HTTPError as e:
            raise httpx.HTTPError(f"API调用失败: {str(e)}")
            
    def get_task_result(self, task_id: str) -> ImageGenerationResponse:
        """
        获取任务结果
        
        Args:
            task_id: 任务ID
            
        Returns:
            ImageGenerationResponse: 任务结果响应
        """
        url = f"{self.base_url}/tasks/{task_id}"
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers={"Authorization": f"Bearer {self.api_key}"})
                response.raise_for_status()
                
                data = response.json()
                # 适配不同的响应格式
                if "output" in data:
                    output = data["output"]
                    
                    # 处理results字段
                    results = None
                    if "results" in output:
                        results = []
                        for result in output["results"]:
                            if isinstance(result, dict):
                                results.append(ImageResult(url=result["url"]))
                            else:
                                # 直接是URL字符串的情况
                                results.append(ImageResult(url=str(result)))
                    
                    return ImageGenerationResponse(
                        task_id=output.get("task_id", task_id),
                        task_status=TaskStatus(output.get("task_status", "UNKNOWN")),
                        submit_time=output.get("submit_time"),
                        scheduled_time=output.get("scheduled_time"),
                        end_time=output.get("end_time"),
                        results=results,
                        image_count=output.get("usage", {}).get("image_count") if "usage" in output else None,
                        request_id=data.get("request_id", "")
                    )
                else:
                    # 直接返回数据格式
                    return ImageGenerationResponse(**data)
                
        except httpx.HTTPError as e:
            raise httpx.HTTPError(f"查询任务失败: {str(e)}")
            
    def wait_for_completion(
        self, 
        task_id: str, 
        timeout: int = 300
    ) -> ImageGenerationResponse:
        """
        等待任务完成
        
        Args:
            task_id: 任务ID
            timeout: 最大等待时间（秒）
            
        Returns:
            ImageGenerationResponse: 最终任务结果
            
        Raises:
            TimeoutError: 等待超时
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            result = self.get_task_result(task_id)
            
            if result.task_status == TaskStatus.SUCCEEDED:
                return result
            elif result.task_status == TaskStatus.FAILED:
                raise RuntimeError(f"任务执行失败: {result.request_id}")
            elif result.task_status == TaskStatus.CANCELED:
                raise RuntimeError("任务已被取消")
                
            time.sleep(self.poll_interval)
            
        raise TimeoutError(f"任务等待超时: {timeout}秒")
        
    def repaint_and_wait(
        self,
        image_url: str,
        style_index: Optional[int] = None,
        style_ref_url: Optional[str] = None,
        timeout: int = 300
    ) -> ImageGenerationResponse:
        """
        一站式风格重绘，创建任务并等待完成
        
        Args:
            image_url: 输入人物图像URL
            style_index: 预置风格编号（与style_ref_url二选一）
            style_ref_url: 自定义风格参考图URL（与style_index二选一）
            timeout: 最大等待时间
            
        Returns:
            ImageGenerationResponse: 最终任务结果
        """
        if style_index is not None and style_ref_url is not None:
            raise ValueError("不能同时指定style_index和style_ref_url")
            
        if style_index is not None:
            response = self.repaint_with_preset_style(image_url, style_index)
        elif style_ref_url is not None:
            response = self.repaint_with_custom_style(image_url, style_ref_url)
        else:
            raise ValueError("必须指定style_index或style_ref_url参数之一")
            
        return self.wait_for_completion(response.task_id, timeout)


# 便捷函数
async def style_repaint_preset(
    image_path: str,
    style_index: int,
    output_dir: str = "./repainted_images",
    api_key: Optional[str] = None
) -> str:
    """
    便捷函数：使用预置风格重绘
    
    Args:
        image_path: 本地图像文件路径
        style_index: 预置风格编号
        output_dir: 输出目录
        api_key: API密钥
        
    Returns:
        str: 生成图像的URL
    """
    generator = StyleRepaintGenerator(api_key=api_key)
    
    # 处理本地文件路径
    if os.path.exists(image_path):
        from ..utils.file_utils import encode_file_to_base64
        image_url = encode_file_to_base64(image_path)
    else:
        image_url = image_path
        
    result = generator.repaint_and_wait(
        image_url=image_url,
        style_index=style_index
    )
    
    if result.results and result.results[0].url:
        return result.results[0].url
    else:
        raise RuntimeError("未能获取生成图像URL")


async def style_repaint_custom(
    image_path: str,
    style_ref_path: str,
    output_dir: str = "./repainted_images",
    api_key: Optional[str] = None
) -> str:
    """
    便捷函数：使用自定义风格重绘
    
    Args:
        image_path: 本地人物图像文件路径
        style_ref_path: 本地风格参考图文件路径
        output_dir: 输出目录
        api_key: API密钥
        
    Returns:
        str: 生成图像的URL
    """
    generator = StyleRepaintGenerator(api_key=api_key)
    
    # 处理本地文件路径
    from ..utils.file_utils import encode_file_to_base64
    
    image_url = encode_file_to_base64(image_path)
    style_ref_url = encode_file_to_base64(style_ref_path)
        
    result = generator.repaint_and_wait(
        image_url=image_url,
        style_ref_url=style_ref_url
    )
    
    if result.results and result.results[0].url:
        return result.results[0].url
    else:
        raise RuntimeError("未能获取生成图像URL")