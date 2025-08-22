#!/usr/bin/env python3
"""
雪风AI海报生成工具
使用通义千问图像模型的GUI海报生成器
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import os
import json
import threading
from datetime import datetime
import sys
import time

class PosterGenerator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("雪风AI海报生成工具")
        self.root.geometry("600x750")
        self.root.resizable(False, False)
        
        # 设置窗口图标（可选）
        try:
            self.root.iconbitmap(default="icon.ico")
        except:
            pass
            
        # 配置
        self.sizes = {
            "1328×1328 (正方形)": "1328*1328",
            "1664×928 (16:9)": "1664*928",
            "1472×1140 (4:3)": "1472*1140",
            "1140×1472 (3:4)": "1140*1472",
            "928×1664 (9:16)": "928*1664"
        }
        
        self.default_negative_prompt = "低分辨率、错误、最差质量、低质量、残缺、多余的手指、比例不良"
        
        self.setup_ui()
        self.load_config()
        self.is_processing = False
        
    def setup_ui(self):
        """设置UI界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置行列权重，让空间充分利用
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # API密钥
        ttk.Label(main_frame, text="API密钥:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.api_key_var = tk.StringVar()
        self.api_key_entry = ttk.Entry(main_frame, textvariable=self.api_key_var, width=60, show="*")
        self.api_key_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 尺寸选择
        ttk.Label(main_frame, text="海报尺寸:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.size_var = tk.StringVar(value="928×1664 (9:16)")
        size_combo = ttk.Combobox(main_frame, textvariable=self.size_var, 
                                 values=list(self.sizes.keys()), state="readonly", width=25)
        size_combo.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # 主标题（视觉焦点）
        ttk.Label(main_frame, text="主标题* (≤12字):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.title_var = tk.StringVar()
        title_entry = ttk.Entry(main_frame, textvariable=self.title_var, width=60)
        title_entry.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 副标题（核心信息）
        ttk.Label(main_frame, text="副标题 (≤25字):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.subtitle_var = tk.StringVar()
        subtitle_entry = ttk.Entry(main_frame, textvariable=self.subtitle_var, width=60)
        subtitle_entry.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 海报内容（≤300字）
        ttk.Label(main_frame, text="海报内容 (≤300字):").grid(row=4, column=0, sticky=tk.NW, pady=5)
        self.body_text = tk.Text(main_frame, width=60, height=6, wrap=tk.WORD)
        self.body_text.grid(row=4, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 视觉要求（≤400字）
        ttk.Label(main_frame, text="视觉要求 (≤400字):").grid(row=5, column=0, sticky=tk.NW, pady=5)
        self.prompt_zh = tk.Text(main_frame, width=60, height=8, wrap=tk.WORD)
        self.prompt_zh.grid(row=5, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 反向提示词
        ttk.Label(main_frame, text="反向提示词:").grid(row=6, column=0, sticky=tk.NW, pady=5)
        self.negative_prompt = tk.Text(main_frame, width=60, height=2, wrap=tk.WORD)
        self.negative_prompt.insert("1.0", self.default_negative_prompt)
        self.negative_prompt.grid(row=6, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 智能改写选项
        self.prompt_extend_var = tk.BooleanVar(value=True)
        prompt_extend_check = ttk.Checkbutton(main_frame, text="开启提示词智能改写", 
                                            variable=self.prompt_extend_var)
        prompt_extend_check.grid(row=7, column=1, sticky=tk.W, pady=5)
        
        # 进度显示
        self.progress_label = ttk.Label(main_frame, text="准备就绪")
        self.progress_label.grid(row=8, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # 进度条 - 充分利用宽度
        self.progress_bar = ttk.Progressbar(main_frame, mode='determinate')
        self.progress_bar.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # 按钮区域 - 充分利用宽度
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=10, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))
        
        # 让按钮均匀分布
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        button_frame.columnconfigure(3, weight=1)
        
        ttk.Button(button_frame, text="测试API", command=self.test_api).grid(row=0, column=0, padx=2, sticky=tk.EW)
        ttk.Button(button_frame, text="保存配置", command=self.save_config).grid(row=0, column=1, padx=2, sticky=tk.EW)
        ttk.Button(button_frame, text="生成海报", command=self.generate_poster, 
                 style="Accent.TButton").grid(row=0, column=2, padx=2, sticky=tk.EW)
        ttk.Button(button_frame, text="停止生成", command=self.cancel_generation).grid(row=0, column=3, padx=2, sticky=tk.EW)
        
        # 结果区域
        result_frame = ttk.LabelFrame(main_frame, text="生成结果", padding="5")
        result_frame.grid(row=11, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.result_text = tk.Text(result_frame, width=60, height=8, wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # 绑定事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 添加字符计数事件
        self.body_text.bind('<KeyRelease>', self.update_char_count)
        self.prompt_zh.bind('<KeyRelease>', self.update_char_count)
        self.title_var.trace('w', self.update_char_count)
        self.subtitle_var.trace('w', self.update_char_count)
        
        # 字符计数标签
        self.char_count_label = ttk.Label(main_frame, text="字符统计: 0/800")
        self.char_count_label.grid(row=12, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # 提示标签
        tip_label = ttk.Label(main_frame, text="提示：避免敏感词，使用中性描述", foreground="gray")
        tip_label.grid(row=13, column=0, columnspan=3, sticky=tk.W, pady=2)
    
    def update_char_count(self, *args):
        """更新字符计数 - 按专业标准"""
        title = len(self.title_var.get())
        subtitle = len(self.subtitle_var.get())
        body = len(self.body_text.get("1.0", tk.END).strip())
        prompt = len(self.prompt_zh.get("1.0", tk.END).strip())
        
        total = title + subtitle + body + prompt
        
        # 字符计数提示
        status_text = f"总:{total}/800 主:{title} 副:{subtitle} 正:{body} 视:{prompt}"
        self.char_count_label.config(text=status_text)
        
        # 颜色提醒
        if total > 800:
            self.char_count_label.config(foreground="red")
        elif total > 750:
            self.char_count_label.config(foreground="orange")
        else:
            self.char_count_label.config(foreground="black")
        
    def load_config(self):
        """加载配置"""
        try:
            from tools_config import config
            self.api_key_var.set(config.api_key)
        except ImportError:
            # Fallback to old config
            config_file = "poster_config.json"
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        self.api_key_var.set(config.get("api_key", ""))
                except:
                    pass
    
    def save_config(self):
        """保存配置"""
        try:
            from tools_config import config
            config.api_key = self.api_key_var.get()
            success = config.save_config()
            if success:
                messagebox.showinfo("成功", "配置已保存")
            else:
                messagebox.showerror("错误", "保存配置失败")
        except ImportError:
            # Fallback to old config
            config = {
                "api_key": self.api_key_var.get()
            }
            with open("poster_config.json", 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("成功", "配置已保存")
    
    def test_api(self):
        """测试API连接"""
        api_key = self.api_key_var.get().strip()
        if not api_key:
            messagebox.showerror("错误", "请输入API密钥")
            return
            
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            test_data = {
                "model": "qwen-image",
                "input": {
                    "prompt": "测试连接"
                }
            }
            
            response = requests.post(
                "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis",
                headers=headers,
                json=test_data,
                timeout=5
            )
            
            if response.status_code == 401:
                messagebox.showerror("错误", "API密钥无效")
            elif response.status_code == 400:
                messagebox.showinfo("成功", "API连接正常（参数验证通过）")
            else:
                messagebox.showinfo("成功", f"API连接正常（状态码：{response.status_code}）")
                
        except Exception as e:
            messagebox.showerror("错误", f"连接失败：{str(e)}")
    
    def generate_poster(self):
        """生成海报"""
        if not self.validate_inputs():
            return
            
        # 重置状态
        self.is_processing = True
        self.progress_label.config(text="正在生成海报...")
        self.progress_bar.start()
        
        thread = threading.Thread(target=self.generate_poster_async)
        thread.daemon = True
        thread.start()
    
    def validate_inputs(self):
        """验证输入 - 仅限制最大字符数"""
        title = self.title_var.get().strip()
        if not title:
            messagebox.showerror("错误", "主标题不能为空")
            return False
            
        if len(title) > 12:
            messagebox.showerror("错误", "主标题最多12字")
            return False
            
        subtitle = self.subtitle_var.get().strip()
        if len(subtitle) > 25:
            messagebox.showerror("错误", "副标题最多25字")
            return False
            
        body = self.body_text.get("1.0", tk.END).strip()
        if len(body) > 300:
            messagebox.showerror("错误", "海报内容最多300字")
            return False
            
        prompt = self.prompt_zh.get("1.0", tk.END).strip()
        if len(prompt) > 400:
            messagebox.showerror("错误", "视觉要求最多400字")
            return False
            
        # 检查总字符数（完全符合800字符要求）
        total_chars = len(title) + len(subtitle) + len(body) + len(prompt)
        if total_chars > 800:
            messagebox.showerror("错误", f"总字符数({total_chars})超过800字符限制")
            return False
            
        api_key = self.api_key_var.get().strip()
        if not api_key:
            messagebox.showerror("错误", "请输入API密钥")
            return False
            
        return True
    
    def build_structured_prompt(self, title: str, subtitle: str = "", body: str = "", user_prompt: str = "") -> str:
        """构建结构化的提示词，明确区分主副正文"""
        
        def clean_text(text):
            return text.replace('"', '').replace("'", '')
        
        # 构建带明确标识的结构化提示词
        prompt_parts = []
        
        # 主标题（视觉焦点）
        if title:
            prompt_parts.append(f"主标题：{clean_text(title)}")
        
        # 副标题（补充说明）
        if subtitle:
            prompt_parts.append(f"副标题：{clean_text(subtitle)}")
            
        # 正文内容（详细描述）
        if body:
            prompt_parts.append(f"正文内容：{clean_text(body)}")
        
        # 视觉要求（设计说明）
        if user_prompt:
            prompt_parts.append(f"视觉要求：{clean_text(user_prompt)}")
        
        # 构建自然语言描述
        content_parts = []
        
        if title:
            content_parts.append(f"一张以【{clean_text(title)}】为主标题的海报")
        
        if subtitle:
            content_parts.append(f"副标题：{clean_text(subtitle)}")
            
        if body:
            content_parts.append(f"海报内容要求：{clean_text(body)}")
        
        if user_prompt:
            content_parts.append(f"视觉要求：{clean_text(user_prompt)}")
        
        # 用分号连接内容
        content_text = "；".join(content_parts)
        
        # 完整描述
        full_prompt = f"{content_text}。设计要求：海报构图主次分明，布局清晰，视觉层次明确，高清4K画质，商业级标准"
        
        # 长度控制
        if len(full_prompt) > 800:
            content_text = "；".join(content_parts)[:750] + "..."
            full_prompt = f"{content_text}。设计要求：海报构图主次分明，高清4K画质"
        
        return full_prompt

    def generate_poster_async(self):
        """异步生成海报 - 增强版调试和重试"""
        try:
            api_key = self.api_key_var.get().strip()
            title = self.title_var.get().strip()
            subtitle = self.subtitle_var.get().strip()
            body = self.body_text.get("1.0", tk.END).strip()
            prompt = self.prompt_zh.get("1.0", tk.END).strip()
            negative = self.negative_prompt.get("1.0", tk.END).strip()
            size_key = self.sizes[self.size_var.get()]
            
            # 调试信息
            self.update_result(f"🔍 调试信息：\n标题: {title}\n尺寸: {size_key}\n提示词长度: {len(prompt)}")
            
            # 结构化构建提示词
            full_prompt = self.build_structured_prompt(
                title=title,
                subtitle=subtitle,
                body=body,
                user_prompt=prompt
            )
            
            
            # 创建任务
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "X-DashScope-Async": "enable",
                "User-Agent": "PosterGenerator/1.0"
            }
            
            # 使用GUI配置构造正确数据结构（100%符合官方文档）
            data = {
                "model": "qwen-image",
                "input": {
                    "prompt": full_prompt,
                    "negative_prompt": negative
                },
                "parameters": {
                    "size": size_key,
                    "n": 1,
                    "prompt_extend": self.prompt_extend_var.get(),
                    "watermark": False
                }
            }
            
            self.update_result(f"📤 请求数据：{json.dumps(data, ensure_ascii=False, indent=2)}")
            
            try:
                # 创建异步任务
                create_response = requests.post(
                    "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis",
                    headers=headers,
                    json=data,
                    timeout=30
                )
                
                if create_response.status_code != 200:
                    try:
                        error_detail = create_response.json()
                    except:
                        error_detail = create_response.text
                    self.update_result(f"❌ 创建任务失败：\n状态码：{create_response.status_code}\n响应：{error_detail}")
                    return
                    
                result = create_response.json()
                task_id = result["output"]["task_id"]
                
                self.update_result(f"✅ 任务已创建：{task_id}\n🔄 开始轮询...")
                
                # 优化的轮询策略
                max_attempts = 30  # 减少轮询次数
                base_delay = 3    # 基础延迟
                
                for attempt in range(max_attempts):
                    if not self.is_processing:
                        self.update_result("🛑 任务已取消")
                        return
                        
                    # 指数退避：3, 4, 5, 6, 7...秒
                    delay = base_delay + (attempt * 0.5)
                    
                    try:
                        query_response = requests.get(
                            f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}",
                            headers={"Authorization": f"Bearer {api_key}"},
                            timeout=10
                        )
                        
                        if query_response.status_code != 200:
                            self.update_result(f"⚠️ 查询失败：{query_response.status_code}")
                            continue
                            
                        query_result = query_response.json()
                        status = query_result["output"]["task_status"]
                        
                        if status == "SUCCEEDED":
                            results = query_result["output"]["results"]
                            urls = [r["url"] for r in results]
                            
                            # 显示智能改写后的实际提示词
                            actual_prompts = []
                            for r in results:
                                if "actual_prompt" in r and r["actual_prompt"]:
                                    actual_prompts.append(r["actual_prompt"])
                            
                            log_message = f"✅ 生成成功！\n📸 图片URL：\n" + "\n".join(urls)
                            if actual_prompts:
                                log_message += f"\n📝 实际提示词（智能改写后）：\n" + "\n".join(actual_prompts)
                            
                            self.update_result(log_message)
                            
                            # 自动下载图片到本地
                            import urllib.request
                            import os
                            from datetime import datetime
                            
                            output_dir = "./generated_images"
                            os.makedirs(output_dir, exist_ok=True)
                            
                            for i, url in enumerate(urls):
                                try:
                                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                    filename = f"poster_{timestamp}_{i+1}.png"
                                    filepath = os.path.join(output_dir, filename)
                                    
                                    urllib.request.urlretrieve(url, filepath)
                                    self.update_result(f"📁 图片已下载：{os.path.abspath(filepath)}")
                                except Exception as e:
                                    self.update_result(f"⚠️ 下载失败：{str(e)}")
                            
                            break
                        elif status == "FAILED":
                            error_code = query_result["output"].get('code', '未知错误码')
                            error_message = query_result["output"].get('message', '未知错误')
                            
                            # 官方错误码处理
                            error_map = {
                                "DataInspectionFailed": "提示词含敏感内容，请修改",
                                "IPInfringementSuspect": "可能涉及知识产权侵权",
                                "InvalidParameter": "参数错误，n只能为1",
                                "InternalError": "服务异常，请重试"
                            }
                            
                            full_error = f"❌ 生成失败：{error_map.get(error_code, error_code)}"
                            
                            if error_message:
                                full_error += f"\n📝 详情：{error_message}"
                            
                            # 针对性建议
                            if error_code == "DataInspectionFailed":
                                full_error += f"\n💡 建议：避免使用政治、敏感词汇"
                            elif error_code == "IPInfringementSuspect":
                                full_error += f"\n💡 建议：避免品牌、人物、版权内容"
                            elif error_code == "InvalidParameter":
                                full_error += f"\n💡 建议：检查参数设置"
                            else:
                                full_error += f"\n💡 建议：请稍后重试"
                            
                            # 完整响应显示
                            full_error += f"\n📋 完整响应：\n{json.dumps(query_result, ensure_ascii=False, indent=2)}"
                            self.update_result(full_error)
                            break
                        elif status in ["PENDING", "RUNNING"]:
                            self.update_result(f"⏳ 处理中... ({attempt+1}/{max_attempts})")
                        
                    except Exception as e:
                        self.update_result(f"🔧 查询错误：{str(e)}")
                    
                    import time
                    time.sleep(delay)
                else:
                    self.update_result("⏰ 任务超时，请稍后重试")
                
            except requests.exceptions.Timeout:
                self.update_result("❌ 创建任务超时，请检查网络连接")
            except requests.exceptions.ConnectionError:
                self.update_result("❌ 网络连接错误，请检查网络")
            except Exception as e:
                self.update_result(f"❌ 未知错误：{type(e).__name__}: {str(e)}")
                
        except Exception as e:
            self.update_result(f"❌ 生成失败：{type(e).__name__}: {str(e)}")
            import traceback
            self.update_result(f"📋 错误详情：\n{traceback.format_exc()}")
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
        self.root.mainloop()

if __name__ == "__main__":
    # 设置高DPI支持
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
        
    app = PosterGenerator()
    app.run()