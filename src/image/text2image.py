from typing import Optional, Dict, Any
import httpx
import os
from urllib.parse import urlparse, unquote
from pathlib import Path
import time

from .models import (
    ImageGenerationRequest, 
    ImageGenerationResponse, 
    TaskCreationResponse,
    TaskStatus,
    ImageResult
)


class Text2ImageGenerator:
    """文生图生成器"""
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        base_url: str = "https://dashscope.aliyuncs.com/api/v1",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        初始化文生图生成器
        
        Args:
            api_key: 阿里云百炼API密钥，如果为None则从环境变量DASHSCOPE_API_KEY获取
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
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable"
        }
        
    def create_task(self, request: ImageGenerationRequest) -> TaskCreationResponse:
        """
        创建图像生成任务
        
        Args:
            request: 图像生成请求参数
            
        Returns:
            TaskCreationResponse: 任务创建响应
            
        Raises:
            httpx.HTTPError: 网络请求错误
            ValueError: 参数验证错误
        """
        url = f"{self.base_url}/services/aigc/text2image/image-synthesis"
        
        payload = {
            "model": request.model,
            "input": {
                "prompt": request.prompt
            },
            "parameters": {
                "size": request.size.value,
                "n": request.n,
                "prompt_extend": request.prompt_extend,
                "watermark": request.watermark
            }
        }
        
        if request.negative_prompt:
            payload["input"]["negative_prompt"] = request.negative_prompt
            
        with httpx.Client(timeout=self.timeout) as client:
            for attempt in range(self.max_retries):
                try:
                    response = client.post(url, headers=self.headers, json=payload)
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
                    
    def get_task_result(self, task_id: str) -> ImageGenerationResponse:
        """
        获取任务结果
        
        Args:
            task_id: 任务ID
            
        Returns:
            ImageGenerationResponse: 任务结果
            
        Raises:
            httpx.HTTPError: 网络请求错误
        """
        url = f"{self.base_url}/tasks/{task_id}"
        
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(url, headers={"Authorization": f"Bearer {self.api_key}"})
            response.raise_for_status()
            
            data = response.json()
            output = data["output"]
            
            results = None
            if "results" in output and output["results"]:
                results = [
                    ImageResult(
                        orig_prompt=result["orig_prompt"],
                        actual_prompt=result.get("actual_prompt"),
                        url=result["url"],
                        code=result.get("code"),
                        message=result.get("message")
                    )
                    for result in output["results"]
                ]
            
            return ImageGenerationResponse(
                task_id=output["task_id"],
                task_status=TaskStatus(output["task_status"]),
                submit_time=output.get("submit_time"),
                scheduled_time=output.get("scheduled_time"),
                end_time=output.get("end_time"),
                results=results,
                image_count=output.get("usage", {}).get("image_count"),
                request_id=data["request_id"]
            )
    
    def wait_for_completion(
        self, 
        task_id: str, 
        poll_interval: float = 3.0,
        timeout: float = 300.0
    ) -> ImageGenerationResponse:
        """
        等待任务完成
        
        Args:
            task_id: 任务ID
            poll_interval: 轮询间隔（秒）
            timeout: 超时时间（秒）
            
        Returns:
            ImageGenerationResponse: 最终任务结果
            
        Raises:
            TimeoutError: 任务超时
            Exception: 任务失败
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
    
    def generate_image(
        self, 
        prompt: str,
        negative_prompt: Optional[str] = None,
        size: str = "1328*1328",
        prompt_extend: bool = True,
        watermark: bool = False,
        **kwargs
    ) -> ImageGenerationResponse:
        """
        生成图像（同步方法）
        
        Args:
            prompt: 正向提示词
            negative_prompt: 反向提示词
            size: 图像尺寸
            prompt_extend: 是否开启智能改写
            watermark: 是否添加水印
            **kwargs: 其他参数
            
        Returns:
            ImageGenerationResponse: 生成结果
        """
        from .models import ImageGenerationRequest, ImageSize
        
        # 映射字符串到枚举
        size_map = {
            "1328*1328": ImageSize.SQUARE_1328,
            "1664*928": ImageSize.WIDESCREEN_1664,
            "1472*1140": ImageSize.LANDSCAPE_1472,
            "1140*1472": ImageSize.PORTRAIT_1140,
            "928*1664": ImageSize.TALL_928
        }
        
        request = ImageGenerationRequest(
            prompt=prompt,
            negative_prompt=negative_prompt,
            size=size_map.get(size, ImageSize.SQUARE_1328),
            prompt_extend=prompt_extend,
            watermark=watermark,
            **kwargs
        )
        
        # 创建任务
        task = self.create_task(request)
        
        # 等待完成
        return self.wait_for_completion(task.task_id)
    
    def download_image(
        self,
        url: str,
        save_path: str,
        filename: Optional[str] = None
    ) -> str:
        """
        下载生成的图像
        
        Args:
            url: 图像URL
            save_path: 保存目录
            filename: 文件名，如果为None则从URL中提取
            
        Returns:
            str: 保存的文件路径
        """
        if filename is None:
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
    
    def download_image_sync(
        self, url: str, save_path: str, filename: Optional[str] = None) -> str:
        """同步下载方法的别名"""
        return self.download_image(url, save_path, filename)