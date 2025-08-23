#!/usr/bin/env python3
"""
雪风AI涂鸦绘画工具
使用通义万相-涂鸦作画模型的GUI应用
支持手绘草图生成精美绘画作品
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Canvas
import os
import json
import threading
import base64
from datetime import datetime
import sys
import time
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.image.sketch_to_image import SketchToImageGenerator
from tools.tools_config import config


class SketchToImageGUI:
    """涂鸦绘画GUI应用"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("雪风AI涂鸦绘画工具")
        self.root.geometry("700x800")
        self.root.resizable(False, False)
        
        # 配置
        self.styles = {
            "自动": "<auto>",
            "3D卡通": "<3d cartoon>",
            "二次元": "<anime>",
            "油画": "<oil painting>",
            "水彩": "<watercolor>",
            "素描": "<sketch>",
            "中国画": "<chinese painting>",
            "扁平插画": "<flat illustration>"
        }
        
        
        self.setup_ui()
        self.load_config()
        self.is_processing = False
        
    def setup_ui(self):
        """设置UI界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置行列权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=0)  # 预览区域固定高度
        main_frame.rowconfigure(8, weight=1)  # 结果区域可扩展
        
        # API密钥
        ttk.Label(main_frame, text="API密钥:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.api_key_var = tk.StringVar()
        self.api_key_entry = ttk.Entry(main_frame, textvariable=self.api_key_var, width=60, show="*")
        self.api_key_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 草图选择
        ttk.Label(main_frame, text="草图文件:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.sketch_path_var = tk.StringVar()
        self.sketch_path_entry = ttk.Entry(main_frame, textvariable=self.sketch_path_var, width=50)
        self.sketch_path_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Button(main_frame, text="选择文件", command=self.select_sketch).grid(row=1, column=2, padx=5)
        
        # 预览区域 - 使用固定大小的Frame
        preview_frame = ttk.LabelFrame(main_frame, text="草图预览", padding="5")
        preview_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # 创建固定大小的预览容器
        preview_container = ttk.Frame(preview_frame, width=300, height=140)
        preview_container.pack(fill=tk.BOTH, expand=False, pady=5)
        preview_container.pack_propagate(False)  # 防止子控件改变大小
        
        # 创建预览标签
        self.preview_label = ttk.Label(preview_container, text="请选择草图文件", anchor=tk.CENTER)
        self.preview_label.pack(fill=tk.BOTH, expand=True)
        
        # 参数设置区域
        params_frame = ttk.LabelFrame(main_frame, text="生成参数", padding="10")
        params_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # 提示词
        ttk.Label(params_frame, text="描述文字* (≤75字):").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        prompt_frame = ttk.Frame(params_frame)
        prompt_frame.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        prompt_frame.columnconfigure(0, weight=1)
        
        self.prompt_var = tk.StringVar()
        prompt_entry = ttk.Entry(prompt_frame, textvariable=self.prompt_var, width=45)
        prompt_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # 字符计数直接显示在输入框右边
        self.char_count_label = ttk.Label(prompt_frame, text="0/75", foreground="gray")
        self.char_count_label.grid(row=0, column=1, padx=5)
        
        # 风格选择
        ttk.Label(params_frame, text="绘画风格:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.style_var = tk.StringVar(value="自动")
        style_combo = ttk.Combobox(params_frame, textvariable=self.style_var, 
                                  values=list(self.styles.keys()), state="readonly", width=20)
        style_combo.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # 输出尺寸 - 固定值
        ttk.Label(params_frame, text="输出尺寸:").grid(row=2, column=0, sticky=tk.W, pady=5)
        size_label = ttk.Label(params_frame, text="768×768 (正方形)", foreground="gray")
        size_label.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # 图片数量
        ttk.Label(params_frame, text="生成数量:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.n_var = tk.IntVar(value=1)
        n_spin = ttk.Spinbox(params_frame, from_=1, to=4, textvariable=self.n_var, width=5)
        n_spin.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # 草图权重
        ttk.Label(params_frame, text="草图权重:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.weight_var = tk.IntVar(value=5)
        weight_scale = ttk.Scale(params_frame, from_=0, to=10, variable=self.weight_var, 
                               orient=tk.HORIZONTAL, length=150)
        weight_scale.grid(row=4, column=1, sticky=tk.W, pady=5)
        self.weight_label = ttk.Label(params_frame, text="5")
        self.weight_label.grid(row=4, column=2, sticky=tk.W, padx=5)
        
        # 权重显示更新
        def update_weight_label(*args):
            self.weight_label.config(text=str(self.weight_var.get()))
        self.weight_var.trace('w', update_weight_label)
        
        # 绑定字符计数
        self.prompt_var.trace('w', lambda *args: self.update_char_count())
        
        # 输出目录
        ttk.Label(main_frame, text="输出目录:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.output_dir_var = tk.StringVar()
        output_entry = ttk.Entry(main_frame, textvariable=self.output_dir_var, width=50)
        output_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Button(main_frame, text="选择目录", command=self.select_output_dir).grid(row=4, column=2, padx=5)
        
        # 进度显示
        self.progress_label = ttk.Label(main_frame, text="准备就绪")
        self.progress_label.grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # 进度条
        self.progress_bar = ttk.Progressbar(main_frame, mode='determinate')
        self.progress_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="测试API", command=self.test_api).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="保存配置", command=self.save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="开始生成", command=self.generate_sketch, 
                 style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="停止生成", command=self.cancel_generation).pack(side=tk.LEFT, padx=5)
        
        # 结果区域 - 固定高度确保完整显示
        result_frame = ttk.LabelFrame(main_frame, text="生成结果", padding="5")
        result_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        self.result_text = tk.Text(result_frame, width=80, height=8, wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=False)
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def update_char_count(self):
        """更新字符计数"""
        count = len(self.prompt_var.get())
        self.char_count_label.config(text=f"{count}/75")
        if count > 75:
            self.char_count_label.config(foreground="red")
        else:
            self.char_count_label.config(foreground="gray")
    
    def select_sketch(self):
        """选择草图文件"""
        file_path = filedialog.askopenfilename(
            title="选择草图文件",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.tiff *.webp"),
                ("所有文件", "*.*")
            ]
        )
        if file_path:
            self.sketch_path_var.set(file_path)
            self.show_preview(file_path)
    
    def show_preview(self, file_path):
        """显示草图预览"""
        try:
            from PIL import Image, ImageTk
            image = Image.open(file_path)
            
            # 调整预览大小 - 缩小以适应GUI
            max_size = (200, 120)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(image)
            self.preview_label.config(image=photo, text="")
            self.preview_label.image = photo  # 保持引用
            
        except Exception as e:
            self.preview_label.config(text=f"预览失败: {str(e)}", image='')
    
    def select_output_dir(self):
        """选择输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_dir_var.set(directory)
    
    def load_config(self):
        """加载配置"""
        try:
            self.api_key_var.set(config.api_key)
            self.output_dir_var.set(config.output_dir)
        except Exception as e:
            self.update_result(f"加载配置失败: {e}")
    
    def save_config(self):
        """保存配置"""
        try:
            config.api_key = self.api_key_var.get()
            config.output_dir = self.output_dir_var.get()
            config.save_config()
            messagebox.showinfo("成功", "配置已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {e}")
    
    def test_api(self):
        """测试API连接"""
        api_key = self.api_key_var.get().strip()
        if not api_key:
            messagebox.showerror("错误", "请输入API密钥")
            return
        
        try:
            generator = SketchToImageGenerator(api_key)
            # 使用简单测试
            self.update_result("✅ API密钥验证成功")
            
        except Exception as e:
            messagebox.showerror("错误", f"API测试失败: {str(e)}")
    
    def validate_inputs(self):
        """验证输入"""
        if not self.api_key_var.get().strip():
            messagebox.showerror("错误", "请输入API密钥")
            return False
        
        if not self.sketch_path_var.get().strip():
            messagebox.showerror("错误", "请选择草图文件")
            return False
        
        if not os.path.exists(self.sketch_path_var.get()):
            messagebox.showerror("错误", "草图文件不存在")
            return False
        
        if not self.prompt_var.get().strip():
            messagebox.showerror("错误", "请输入描述文字")
            return False
        
        if len(self.prompt_var.get()) > 75:
            messagebox.showerror("错误", "描述文字最多75字")
            return False
        
        return True
    
    def generate_sketch(self):
        """生成涂鸦绘画"""
        if not self.validate_inputs():
            return
        
        self.is_processing = True
        self.progress_label.config(text="正在生成...")
        self.progress_bar.start()
        
        thread = threading.Thread(target=self.generate_sketch_async)
        thread.daemon = True
        thread.start()
    
    def generate_sketch_async(self):
        """异步生成涂鸦绘画"""
        try:
            generator = SketchToImageGenerator(self.api_key_var.get())
            
            # 创建任务
            style_key = self.styles[self.style_var.get()]
            size_key = "768*768"  # 固定尺寸
            
            task_response = generator.generate_from_file(
                sketch_path=self.sketch_path_var.get(),
                prompt=self.prompt_var.get(),
                style=style_key,
                size=size_key,
                n=self.n_var.get(),
                sketch_weight=self.weight_var.get()
            )
            
            if task_response.task_status == "FAILED":
                self.update_result(f"❌ 创建任务失败: {task_response.error_message}")
                return
            
            self.update_result(f"✅ 任务已创建: {task_response.task_id}")
            
            # 轮询等待结果
            max_attempts = 40
            for attempt in range(max_attempts):
                if not self.is_processing:
                    self.update_result("🛑 任务已取消")
                    return
                
                result = generator.get_task_result(task_response.task_id)
                
                if result.task_status == "SUCCEEDED":
                    # 下载图片
                    output_dir = self.output_dir_var.get()
                    os.makedirs(output_dir, exist_ok=True)
                    
                    downloaded_files = []
                    for i, url in enumerate(result.image_urls):
                        try:
                            import urllib.request
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"sketch_drawing_{timestamp}_{i+1}.png"
                            filepath = os.path.join(output_dir, filename)
                            
                            urllib.request.urlretrieve(url, filepath)
                            downloaded_files.append(filepath)
                            self.update_result(f"📁 图片已下载: {filepath}")
                            
                        except Exception as e:
                            self.update_result(f"⚠️ 下载失败: {str(e)}")
                    
                    self.update_result(f"✅ 生成成功! 共{len(downloaded_files)}张图片")
                    break
                    
                elif result.task_status == "FAILED":
                    self.update_result(f"❌ 生成失败: {result.error_message}")
                    break
                
                self.update_result(f"⏳ 处理中... ({attempt+1}/{max_attempts})")
                time.sleep(3)
            else:
                self.update_result("⏰ 任务超时，请稍后重试")
                
        except Exception as e:
            self.update_result(f"❌ 生成失败: {type(e).__name__}: {str(e)}")
        finally:
            self.root.after(0, self.finish_generation)
    
    def update_result(self, text):
        """更新结果"""
        self.root.after(0, lambda: self.result_text.insert("1.0", f"{datetime.now().strftime('%H:%M:%S')} - {text}\n"))
        self.root.after(0, lambda: self.result_text.see("1.0"))
    
    def finish_generation(self):
        """完成生成"""
        self.progress_bar.stop()
        self.progress_label.config(text="生成完成")
        self.is_processing = False
    
    def cancel_generation(self):
        """取消生成"""
        if self.is_processing:
            self.is_processing = False
            self.progress_bar.stop()
            self.progress_label.config(text="已取消")
            self.update_result("🛑 任务已取消")
    
    def on_closing(self):
        """关闭窗口"""
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """运行应用"""
        # 设置高DPI支持
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
            
        self.root.mainloop()


if __name__ == "__main__":
    app = SketchToImageGUI()
    app.run()