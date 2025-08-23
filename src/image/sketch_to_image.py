"""
通义万相-涂鸦作画功能实现
基于wanx-sketch-to-image-lite模型的涂鸦绘画功能
"""

import base64
import json
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
import requests
from pydantic import BaseModel, Field


class SketchToImageRequest(BaseModel):
    """涂鸦绘画请求模型"""
    prompt: str = Field(..., description="提示词，≤75字符", max_length=75)
    sketch_image_url: Optional[str] = Field(None, description="草图URL地址")
    sketch_image_base64: Optional[str] = Field(None, description="草图base64编码")
    size: str = Field("768*768", description="输出图像分辨率，目前仅支持768*768")
    n: int = Field(1, description="生成图片数量，1-4张", ge=1, le=4)
    style: str = Field("<auto>", description="输出图像风格，默认自动随机选择")
    sketch_weight: int = Field(3, description="草图约束程度，0-10", ge=0, le=10)
    sketch_extraction: bool = Field(False, description="是否提取sketch边缘")
    sketch_color: List[int] = Field(default_factory=list, description="画笔色RGB数值")


class SketchToImageResponse(BaseModel):
    """涂鸦绘画响应模型"""
    task_id: str
    task_status: str
    image_urls: List[str] = Field(default_factory=list)
    error_message: Optional[str] = None


class SketchToImageGenerator:
    """涂鸦绘画生成器"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://dashscope.aliyuncs.com/api/v1"
        
    def generate_from_url(self, 
                         sketch_url: str, 
                         prompt: str,
                         **kwargs) -> SketchToImageResponse:
        """通过URL上传草图生成图像"""
        request_data = SketchToImageRequest(
            prompt=prompt,
            sketch_image_url=sketch_url,
            **kwargs
        )
        return self._create_task(request_data)
    
    def generate_from_file(self, 
                          sketch_path: str, 
                          prompt: str,
                          **kwargs) -> SketchToImageResponse:
        """通过本地文件上传草图生成图像"""
        # 将本地文件转换为base64
        sketch_base64 = self._file_to_base64(sketch_path)
        request_data = SketchToImageRequest(
            prompt=prompt,
            sketch_image_base64=sketch_base64,
            **kwargs
        )
        return self._create_task(request_data)
    
    def generate_from_base64(self, 
                           sketch_base64: str, 
                           prompt: str,
                           **kwargs) -> SketchToImageResponse:
        """通过base64编码草图生成图像"""
        request_data = SketchToImageRequest(
            prompt=prompt,
            sketch_image_base64=sketch_base64,
            **kwargs
        )
        return self._create_task(request_data)
    
    def _file_to_base64(self, file_path: str) -> str:
        """将文件转换为base64编码"""
        with open(file_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    
    def _create_task(self, request: SketchToImageRequest) -> SketchToImageResponse:
        """创建异步任务"""
        # 构建请求数据
        data = {
            "model": "wanx-sketch-to-image-lite",
            "input": {
                "prompt": request.prompt
            },
            "parameters": {
                "size": request.size,
                "n": request.n,
                "style": request.style,
                "sketch_weight": request.sketch_weight,
                "sketch_extraction": request.sketch_extraction,
                "sketch_color": request.sketch_color
            }
        }
        
        # 添加草图数据
        if request.sketch_image_url:
            data["input"]["sketch_image_url"] = request.sketch_image_url
        elif request.sketch_image_base64:
            # 构建data URL
            mime_type = "image/png"  # 默认为PNG
            data_url = f"data:{mime_type};base64,{request.sketch_image_base64}"
            data["input"]["sketch_image_url"] = data_url
        
        # 发送创建任务请求
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/services/aigc/image2image/image-synthesis",
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            task_id = result["output"]["task_id"]
            
            return SketchToImageResponse(
                task_id=task_id,
                task_status="PENDING"
            )
            
        except Exception as e:
            return SketchToImageResponse(
                task_id="",
                task_status="FAILED",
                error_message=str(e)
            )
    
    def get_task_result(self, task_id: str) -> SketchToImageResponse:
        """获取任务结果"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            response = requests.get(
                f"{self.base_url}/tasks/{task_id}",
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            output = result.get("output", {})
            
            image_urls = []
            if output.get("task_status") == "SUCCEEDED":
                for item in output.get("results", []):
                    if "url" in item:
                        image_urls.append(item["url"])
            
            return SketchToImageResponse(
                task_id=task_id,
                task_status=output.get("task_status", "UNKNOWN"),
                image_urls=image_urls,
                error_message=output.get("message")
            )
            
        except Exception as e:
            return SketchToImageResponse(
                task_id=task_id,
                task_status="FAILED",
                error_message=str(e)
            )
    
    def generate_and_wait(self, 
                         sketch_path: str, 
                         prompt: str,
                         max_wait_time: int = 120,
                         **kwargs) -> SketchToImageResponse:
        """创建任务并等待结果"""
        # 创建任务
        task_response = self.generate_from_file(sketch_path, prompt, **kwargs)
        
        if task_response.task_status == "FAILED":
            return task_response
        
        # 轮询等待结果
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            result = self.get_task_result(task_response.task_id)
            
            if result.task_status in ["SUCCEEDED", "FAILED"]:
                return result
            
            time.sleep(3)  # 每3秒查询一次
        
        return SketchToImageResponse(
            task_id=task_response.task_id,
            task_status="TIMEOUT",
            error_message=f"任务超时，等待时间超过{max_wait_time}秒"
        )


# 使用示例
if __name__ == "__main__":
    import os
    
    # 初始化生成器
    api_key = os.getenv("DASHSCOPE_API_KEY", "your-api-key")
    generator = SketchToImageGenerator(api_key)
    
    # 示例：从URL生成
    sketch_url = "https://example.com/sketch.png"
    result = generator.generate_from_url(
        sketch_url=sketch_url,
        prompt="美丽的花朵",
        style="<watercolor>",
        n=2
    )
    
    print(f"任务ID: {result.task_id}")
    print(f"状态: {result.task_status}")
    
    # 等待并获取结果
    if result.task_id:
        final_result = generator.get_task_result(result.task_id)
        print(f"最终状态: {final_result.task_status}")
        print(f"图片URL: {final_result.image_urls}")