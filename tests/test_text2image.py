"""
文生图功能测试
"""

import pytest
import os
from pathlib import Path
from src.image import Text2ImageGenerator
from src.image.models import ImageGenerationRequest, ImageSize


class TestText2ImageGenerator:
    """文生图生成器测试类"""
    
    @pytest.fixture
    def generator(self):
        """创建生成器实例"""
        api_key = os.getenv("DASHSCOPE_API_KEY", "test_key")
        return Text2ImageGenerator(api_key=api_key)
    
    def test_init_without_api_key(self):
        """测试没有API密钥时的初始化"""
        with pytest.raises(ValueError):
            Text2ImageGenerator(api_key=None)
    
    def test_init_with_api_key(self):
        """测试使用API密钥初始化"""
        generator = Text2ImageGenerator(api_key="test_key")
        assert generator.api_key == "test_key"
        assert generator.base_url == "https://dashscope.aliyuncs.com/api/v1"
    
    def test_create_request_model(self):
        """测试创建请求模型"""
        request = ImageGenerationRequest(
            prompt="test prompt",
            negative_prompt="test negative",
            size=ImageSize.SQUARE_1328,
            n=1,
            prompt_extend=True,
            watermark=False
        )
        
        assert request.prompt == "test prompt"
        assert request.negative_prompt == "test negative"
        assert request.size == ImageSize.SQUARE_1328
        assert request.n == 1
        assert request.prompt_extend is True
        assert request.watermark is False
    
    def test_image_sizes(self):
        """测试图像尺寸枚举"""
        assert ImageSize.SQUARE_1328.value == "1328*1328"
        assert ImageSize.WIDESCREEN_1664.value == "1664*928"
        assert ImageSize.LANDSCAPE_1472.value == "1472*1140"
        assert ImageSize.PORTRAIT_1140.value == "1140*1472"
        assert ImageSize.TALL_928.value == "928*1664"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])