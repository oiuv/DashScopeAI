#!/usr/bin/env python3
"""
雪风AI水印去除工具
使用万相和通义千问图像编辑模型去除图片水印
支持批量处理和实时预览
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import sys
import threading
import requests
import base64
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from tools_config import ToolsConfig

class WatermarkRemoverGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("雪风AI水印去除工具")
        self.root.geometry("600x600")
        self.root.resizable(True, True)
        
        # 配置
        self.config = ToolsConfig()
        self.api_key = tk.StringVar(value=self.config.api_key)
        self.selected_files = []
        self.output_dir = tk.StringVar(value=self.config.output_dir)
        self.is_processing = False
        
        self.setup_ui()
        self.load_config()
    
    def setup_ui(self):
        """设置UI界面"""
        # 顶部框架
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)
        
        # API密钥输入
        ttk.Label(top_frame, text="API密钥:").pack(side=tk.LEFT, padx=5)
        api_entry = ttk.Entry(top_frame, textvariable=self.api_key, width=40, show="*")
        api_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="保存配置", command=self.save_config).pack(side=tk.LEFT, padx=5)
        
        # 中间框架
        middle_frame = ttk.Frame(self.root, padding="5")
        middle_frame.pack(fill=tk.BOTH, expand=True)
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(middle_frame, text="文件选择", padding="10")
        file_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 文件列表
        self.file_listbox = tk.Listbox(file_frame, selectmode=tk.MULTIPLE, height=4)
        self.file_listbox.pack(fill=tk.BOTH, expand=True, pady=2)
        
        # 文件操作按钮
        button_frame = ttk.Frame(file_frame)
        button_frame.pack(fill=tk.X, pady=2)
        
        ttk.Button(button_frame, text="选择文件", command=self.select_files).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="选择目录", command=self.select_directory).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="清空列表", command=self.clear_files).pack(side=tk.LEFT, padx=2)
        
        # 输出目录
        output_frame = ttk.LabelFrame(middle_frame, text="输出设置", padding="5")
        output_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(output_frame, text="输出目录:").pack(side=tk.LEFT, padx=2)
        ttk.Entry(output_frame, textvariable=self.output_dir, width=40).pack(side=tk.LEFT, padx=2)
        ttk.Button(output_frame, text="选择目录", command=self.select_output_dir).pack(side=tk.LEFT, padx=2)
        
        # 进度区域
        progress_frame = ttk.LabelFrame(middle_frame, text="处理进度", padding="5")
        progress_frame.pack(fill=tk.X, pady=5)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=2)
        
        self.status_label = ttk.Label(progress_frame, text="就绪")
        self.status_label.pack()
        
        # 底部按钮
        bottom_frame = ttk.Frame(self.root, padding="5")
        bottom_frame.pack(fill=tk.X)
        
        ttk.Button(bottom_frame, text="开始处理", command=self.start_processing).pack(side=tk.LEFT, padx=2)
        ttk.Button(bottom_frame, text="停止处理", command=self.stop_processing).pack(side=tk.LEFT, padx=2)
        ttk.Button(bottom_frame, text="退出", command=self.root.quit).pack(side=tk.RIGHT, padx=2)
    
    def load_config(self):
        """加载配置"""
        try:
            if not self.config.api_key:
                messagebox.showwarning("警告", "请先设置API密钥")
        except Exception as e:
            messagebox.showerror("错误", f"加载配置失败: {e}")
    
    def save_config(self):
        """保存配置"""
        try:
            # 保存API密钥
            api_key = self.api_key.get().strip()
            if api_key:
                self.config.api_key = api_key
            
            # 保存输出目录
            self.config.output_dir = self.output_dir.get()
            
            # 保存到文件
            self.config.save_config()
            
            messagebox.showinfo("成功", "配置已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {e}")
    
    def select_files(self):
        """选择文件"""
        files = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp"),
                ("所有文件", "*.*")
            ]
        )
        for file in files:
            if file not in self.selected_files:
                self.selected_files.append(file)
                self.file_listbox.insert(tk.END, os.path.basename(file))
    
    def select_directory(self):
        """选择目录"""
        directory = filedialog.askdirectory(title="选择图片目录")
        if directory:
            image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
            for file_path in Path(directory).glob("*"):
                if file_path.suffix.lower() in image_extensions:
                    str_path = str(file_path)
                    if str_path not in self.selected_files:
                        self.selected_files.append(str_path)
                        self.file_listbox.insert(tk.END, file_path.name)
    
    def select_output_dir(self):
        """选择输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_dir.set(directory)
    
    def clear_files(self):
        """清空文件列表"""
        self.selected_files.clear()
        self.file_listbox.delete(0, tk.END)
    
    def validate_inputs(self):
        """验证输入"""
        if not self.api_key.get().strip():
            messagebox.showerror("错误", "请输入API密钥")
            return False
        
        if not self.selected_files:
            messagebox.showerror("错误", "请选择图片文件")
            return False
        
        if not self.output_dir.get().strip():
            messagebox.showerror("错误", "请选择输出目录")
            return False
        
        return True
    
    def start_processing(self):
        """开始处理"""
        if not self.validate_inputs():
            return
        
        if self.is_processing:
            messagebox.showwarning("警告", "正在处理中...")
            return
        
        self.is_processing = True
        self.progress_bar['maximum'] = len(self.selected_files)
        self.progress_bar['value'] = 0
        
        # 创建输出目录
        Path(self.output_dir.get()).mkdir(parents=True, exist_ok=True)
        
        # 启动处理线程
        thread = threading.Thread(target=self.process_files)
        thread.daemon = True
        thread.start()
    
    def stop_processing(self):
        """停止处理"""
        self.is_processing = False
        self.status_label.config(text="已停止")
    
    def process_files(self):
        """处理文件"""
        total_files = len(self.selected_files)
        processed = 0
        
        for i, file_path in enumerate(self.selected_files):
            if not self.is_processing:
                break
            
            try:
                self.status_label.config(text=f"处理中: {os.path.basename(file_path)} ({i+1}/{total_files})")
                self.root.update_idletasks()
                
                self.process_single_file(file_path)
                
                processed += 1
                self.progress_bar['value'] = processed
                self.root.update_idletasks()
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("错误", f"处理 {os.path.basename(file_path)} 失败: {str(e)}"))
        
        self.is_processing = False
        if processed == total_files:
            self.root.after(0, lambda: messagebox.showinfo("完成", f"成功处理 {processed} 张图片"))
        else:
            self.root.after(0, lambda: messagebox.showinfo("完成", f"处理了 {processed} 张图片"))
        
        self.status_label.config(text="就绪")
    
    def encode_image_to_base64(self, image_path):
        """将图片编码为base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def process_single_file(self, file_path):
        """处理单个文件"""
        # 将图片编码为base64
        image_data = self.encode_image_to_base64(file_path)
        mime_type = "image/jpeg" if file_path.lower().endswith(('.jpg', '.jpeg')) else "image/png"
        image_url = f"data:{mime_type};base64,{image_data}"
        
        # 调用千问API
        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
        
        headers = {
            "Authorization": f"Bearer {self.api_key.get()}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "qwen-image-edit",
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"image": image_url},
                            {"text": "只去除图片中的水印文字，保持图片原始质量和细节，不要改变图片原始内容"}
                        ]
                    }
                ]
            },
            "parameters": {
                "negative_prompt": "低分辨率、错误、最差质量、低质量、残缺",
                "watermark": False
            }
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        edited_url = result["output"]["choices"][0]["message"]["content"][0]["image"]
        
        # 下载处理后的图片
        output_path = Path(self.output_dir.get()) / f"watermark_removed_{Path(file_path).stem}.png"
        
        if edited_url.startswith("data:image"):
            # 处理base64数据
            header, data = edited_url.split(",", 1)
            image_data = base64.b64decode(data)
            with open(output_path, "wb") as f:
                f.write(image_data)
        else:
            # 处理URL
            img_response = requests.get(edited_url)
            img_response.raise_for_status()
            with open(output_path, "wb") as f:
                f.write(img_response.content)


def main():
    """主函数"""
    root = tk.Tk()
    app = WatermarkRemoverGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()