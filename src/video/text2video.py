"""
视频生成器
支持文生视频、图生视频等功能
"""

from typing import Optional, Dict, Any
import httpx
import os
from urllib.parse import urlparse, unquote
from pathlib import Path
import time

from .models import (
    VideoGenerationRequest,
    VideoGenerationResponse,
    TaskCreationResponse,
    TaskStatus,
    VideoResult,
)


class VideoGenerator:
    """视频生成器（支持文生视频和图生视频）"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://dashscope.aliyuncs.com/api/v1",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        初始化视频生成器

        Args:
            api_key: 阿里云百炼 API 密钥，如果为 None 则从环境变量 DASHSCOPE_API_KEY 获取
            base_url: API 基础 URL（北京地域默认）
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
        """
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("API 密钥不能为空，请设置 api_key 参数或环境变量 DASHSCOPE_API_KEY")

        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable"
        }

    def create_task(self, request: VideoGenerationRequest) -> TaskCreationResponse:
        """
        创建视频生成任务

        Args:
            request: 视频生成请求参数

        Returns:
            TaskCreationResponse: 任务创建响应

        Raises:
            httpx.HTTPError: 网络请求错误
            ValueError: 参数验证错误
        """
        # 根据模型选择不同的 API endpoint
        if request.model == "wanx2.1-kf2v-plus":
            # 首尾帧生视频 API
            url = f"{self.base_url}/services/aigc/image2video/video-synthesis"
        else:
            # 文生视频/图生视频 API
            url = f"{self.base_url}/services/aigc/video-generation/video-synthesis"

        validation = request.validate_for_model()
        if not validation["valid"]:
            raise ValueError("; ".join(validation["errors"]))

        # 构建请求体
        payload = {
            "model": request.model,
            "input": {},
            "parameters": {}
        }

        # input 参数
        if request.prompt:
            payload["input"]["prompt"] = request.prompt
        if request.image_url:
            payload["input"]["img_url"] = request.image_url
        if request.first_frame_url:
            payload["input"]["first_frame_url"] = request.first_frame_url
        if request.last_frame_url:
            # 根据文档：若同时提供 first_frame_url、last_frame_url、template，将忽略 last_frame_url
            # 为了兼容性，仍然传入该参数
            payload["input"]["last_frame_url"] = request.last_frame_url
        if request.audio_url:
            payload["input"]["audio_url"] = request.audio_url
        if request.negative_prompt:
            payload["input"]["negative_prompt"] = request.negative_prompt
        if request.template:
            payload["input"]["template"] = request.template

        # parameters 参数
        if request.resolution:
            # 图生视频使用 resolution
            payload["parameters"]["resolution"] = request.resolution
        elif request.size:
            # 文生视频使用 size
            payload["parameters"]["size"] = request.size

        payload["parameters"]["duration"] = request.duration
        payload["parameters"]["prompt_extend"] = request.prompt_extend
        payload["parameters"]["watermark"] = request.watermark

        if request.seed is not None:
            payload["parameters"]["seed"] = request.seed
        if request.shot_type and request.model.startswith("wan2.6"):
            payload["parameters"]["shot_type"] = request.shot_type
        if request.audio is not None and request.model == "wan2.6-i2v-flash":
            payload["parameters"]["audio"] = request.audio

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

    def get_task_result(self, task_id: str) -> VideoGenerationResponse:
        """
        获取任务结果

        Args:
            task_id: 任务 ID

        Returns:
            VideoGenerationResponse: 任务结果

        Raises:
            httpx.HTTPError: 网络请求错误
        """
        url = f"{self.base_url}/tasks/{task_id}"

        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(url, headers={"Authorization": f"Bearer {self.api_key}"})
            response.raise_for_status()

            data = response.json()
            output = data["output"]

            # 构建响应
            return VideoGenerationResponse(
                task_id=output["task_id"],
                task_status=TaskStatus(output["task_status"]),
                submit_time=output.get("submit_time"),
                scheduled_time=output.get("scheduled_time"),
                end_time=output.get("end_time"),
                video_url=output.get("video_url"),
                orig_prompt=output.get("orig_prompt"),
                actual_prompt=output.get("actual_prompt"),
                usage=data.get("usage"),
                request_id=data["request_id"],
                error_code=output.get("code"),
                error_message=output.get("message")
            )

    def wait_for_completion(
        self,
        task_id: str,
        poll_interval: float = 15.0,
        timeout: float = 600.0
    ) -> VideoGenerationResponse:
        """
        等待任务完成

        Args:
            task_id: 任务 ID
            poll_interval: 轮询间隔（秒），建议 15 秒
            timeout: 超时时间（秒）

        Returns:
            VideoGenerationResponse: 最终任务结果

        Raises:
            TimeoutError: 任务超时
            Exception: 任务失败
        """
        start_time = time.time()
        print("正在生成视频，请耐心等待...")

        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"任务 {task_id} 超时，等待时间超过 {timeout} 秒")

            result = self.get_task_result(task_id)

            if result.task_status == TaskStatus.SUCCEEDED:
                print("视频生成成功！")
                return result
            elif result.task_status == TaskStatus.FAILED:
                raise Exception(f"任务 {task_id} 执行失败：{result.error_message}")
            elif result.task_status == TaskStatus.CANCELED:
                raise Exception(f"任务 {task_id} 已取消")
            elif result.task_status == TaskStatus.UNKNOWN:
                raise Exception(f"任务 {task_id} 不存在或已过期（task_id 有效期 24 小时）")

            # 显示当前状态
            if result.task_status == TaskStatus.PENDING:
                print("任务排队中...")
            elif result.task_status == TaskStatus.RUNNING:
                print("任务处理中...")

            time.sleep(poll_interval)

    def generate_video(
        self,
        prompt: str,
        size: Optional[str] = None,
        resolution: Optional[str] = None,
        duration: int = 5,
        prompt_extend: bool = True,
        watermark: bool = False,
        seed: Optional[int] = None,
        negative_prompt: Optional[str] = None,
        audio_url: Optional[str] = None,
        shot_type: Optional[str] = None,
        model: str = "wan2.6-t2v",
        **kwargs
    ) -> VideoGenerationResponse:
        """
        生成视频（同步方法）- 文生视频

        Args:
            prompt: 正向提示词
            size: 视频分辨率（文生视频使用，格式：宽*高）
            resolution: 视频分辨率档位（图生视频使用：480P/720P/1080P）
            duration: 视频时长（秒）
            prompt_extend: 是否开启智能改写
            watermark: 是否添加水印
            seed: 随机种子
            negative_prompt: 反向提示词
            audio_url: 音频 URL（wan2.5/2.6 系列支持）
            shot_type: 镜头类型 single/multi（仅 wan2.6 系列支持）
            model: 模型名称
            **kwargs: 其他参数

        Returns:
            VideoGenerationResponse: 生成结果
        """
        request = VideoGenerationRequest(
            prompt=prompt,
            size=size,
            resolution=resolution,
            duration=duration,
            prompt_extend=prompt_extend,
            watermark=watermark,
            seed=seed,
            negative_prompt=negative_prompt,
            audio_url=audio_url,
            shot_type=shot_type,
            model=model,
            **kwargs
        )

        # 创建任务
        task = self.create_task(request)

        # 等待完成
        return self.wait_for_completion(task.task_id)

    def generate_image2video(
        self,
        image_url: str,
        prompt: Optional[str] = None,
        resolution: str = "1080P",
        duration: int = 5,
        prompt_extend: bool = True,
        watermark: bool = False,
        seed: Optional[int] = None,
        negative_prompt: Optional[str] = None,
        audio_url: Optional[str] = None,
        shot_type: Optional[str] = None,
        audio: Optional[bool] = None,
        model: str = "wan2.6-i2v-flash",
        template: Optional[str] = None,
        **kwargs
    ) -> VideoGenerationResponse:
        """
        生成视频（同步方法）- 图生视频

        Args:
            image_url: 首帧图片 URL（支持 http/https/file/data/oss 协议）
            prompt: 正向提示词（使用 template 时可不填）
            resolution: 视频分辨率档位（480P/720P/1080P）
            duration: 视频时长（秒）
            prompt_extend: 是否开启智能改写
            watermark: 是否添加水印
            seed: 随机种子
            negative_prompt: 反向提示词
            audio_url: 音频 URL（wan2.5/2.6 系列支持）
            shot_type: 镜头类型 single/multi（仅 wan2.6 系列支持）
            audio: 是否生成有声视频（仅 wan2.6-i2v-flash 支持）
            model: 模型名称
            template: 视频特效模板名称
            **kwargs: 其他参数

        Returns:
            VideoGenerationResponse: 生成结果
        """
        request = VideoGenerationRequest(
            model=model,
            image_url=image_url,
            prompt=prompt,
            resolution=resolution,
            duration=duration,
            prompt_extend=prompt_extend,
            watermark=watermark,
            seed=seed,
            negative_prompt=negative_prompt,
            audio_url=audio_url,
            shot_type=shot_type,
            audio=audio,
            template=template,
            **kwargs
        )

        # 创建任务
        task = self.create_task(request)

        # 等待完成
        return self.wait_for_completion(task.task_id)

    def generate_first_last_frame(
        self,
        first_frame_url: str,
        prompt: Optional[str] = None,
        resolution: str = "1080P",
        duration: int = 5,
        prompt_extend: bool = True,
        watermark: bool = False,
        seed: Optional[int] = None,
        model: str = "wanx2.1-kf2v-plus",
        template: Optional[str] = None,
        **kwargs
    ) -> VideoGenerationResponse:
        """
        生成视频（同步方法）- 首尾帧生视频（基于首帧的视频特效）

        Args:
            first_frame_url: 首帧图片 URL（支持 http/https/file/data/oss 协议，必填）
            prompt: 正向提示词（使用 template 时可不填）
            resolution: 视频分辨率档位（480P/720P/1080P）
            duration: 视频时长（秒）
            prompt_extend: 是否开启智能改写
            watermark: 是否添加水印
            seed: 随机种子
            model: 模型名称（默认：wanx2.1-kf2v-plus）
            template: 视频特效模板名称（使用特效时 prompt 可留空）
            **kwargs: 其他参数

        Returns:
            VideoGenerationResponse: 生成结果

        Note:
            根据官方文档，首尾帧生视频的特效功能仅需提供首帧图像即可生成，
            无需提供尾帧图像。若同时提供 first_frame_url、last_frame_url、template，
            将忽略 last_frame_url。
        """
        request = VideoGenerationRequest(
            model=model,
            first_frame_url=first_frame_url,
            prompt=prompt,
            resolution=resolution,
            duration=duration,
            prompt_extend=prompt_extend,
            watermark=watermark,
            seed=seed,
            template=template,
            **kwargs
        )

        # 创建任务
        task = self.create_task(request)

        # 等待完成
        return self.wait_for_completion(task.task_id)

    def download_video(
        self,
        url: str,
        save_path: str,
        filename: Optional[str] = None
    ) -> str:
        """
        下载生成的视频

        Args:
            url: 视频 URL
            save_path: 保存目录
            filename: 文件名，如果为 None 则从 URL 中提取

        Returns:
            str: 保存的文件路径
        """
        if filename is None:
            filename = unquote(urlparse(url).path.split('/')[-1]) or "video.mp4"

        save_dir = Path(save_path)
        save_dir.mkdir(parents=True, exist_ok=True)
        file_path = save_dir / filename

        print(f"正在下载视频：{filename}")
        with httpx.Client(timeout=300) as client:
            response = client.get(url)
            response.raise_for_status()

            with open(file_path, 'wb') as f:
                f.write(response.content)

        return str(file_path)
