from flask import Flask, request, jsonify
import requests
import tkinter as tk
from tkinter import messagebox
import configparser
import json
import os

api_url = None
field_mapping = None
app = Flask(__name__)


@app.route('/proxy', methods=['GET', 'POST'])
def get_proxy():
    global api_url, field_mapping
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        proxy_data = response.json()

        def get_nested_value(data, path):
            """获取嵌套字典中的值
            path 可以是以下格式：
            - 字符串: "key"
            - 列表: ["data", 0, "ip"]
            - 逗号分隔的字符串: "data,0,ip"
            """
            try:
                if isinstance(path, str):
                    # 检查是否包含逗号，如果包含则按逗号分割
                    if ',' in path:
                        path = [p.strip() for p in path.split(',')]
                        # 将数字字符串转换为整数
                        path = [int(p) if p.isdigit() else p for p in path]
                    elif '' == path:
                        return ''
                    else:
                        return data.get(path)
                
                current = data
                for key in path:
                    if current is None:
                        return ''
                    
                    # 处理数字索引
                    if isinstance(key, (str, int)):
                        # 如果是数字字符串，转换为整数
                        if isinstance(key, str) and key.isdigit():
                            key = int(key)
                        
                        # 根据键的类型选择不同的访问方式
                        if isinstance(key, int):
                            if isinstance(current, (list, tuple)):
                                if 0 <= key < len(current):
                                    current = current[key]
                                else:
                                    return ''
                            else:
                                return ''
                        else:
                            if isinstance(current, dict):
                                current = current.get(str(key))
                            else:
                                return ''
                    else:
                        return ''
                
                return current
            except Exception:
                return ''

        # 解析字段映射
        try:
            mapping_dict = json.loads(field_mapping)
        except:
            return jsonify({"status": "fail", "message": "Invalid field mapping format"}), 500

        # 根据字段映射解析代理信息
        proxy_info = {}
        for key, path in mapping_dict.items():
            if key == 'type':
                proxy_info[key] = path
            else:
                value = get_nested_value(proxy_data, path)
                proxy_info[key] = value

        return jsonify({"status": "success", "proxy": proxy_info})

    except requests.RequestException as e:
        return jsonify({"status": "fail", "message": str(e)}), 500
    except Exception as e:
        return jsonify({"status": "fail", "message": f"Error parsing proxy data: {str(e)}"}), 500


class ProxyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("代理管理器  v1.0")
        self.root.iconbitmap(".\\resource\\proxy.ico")
        self.config_file = "config.ini"

        # 定义 StringVar 变量
        self.url = tk.StringVar()
        self.mapping = tk.StringVar()
        
        # 从配置文件加载设置
        self.load_config()
        
        # 绑定变量更新事件
        self.url.trace_add("write", self.update_url)
        self.mapping.trace_add("write", self.update_mapping)

        # 添加 API 地址提示
        api_info_frame = tk.Frame(root)
        api_info_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.EW)
        
        tk.Label(api_info_frame, text="本地代理服务地址: ").pack(side=tk.LEFT)
        local_api_label = tk.Label(api_info_frame, 
                                  text="http://127.0.0.1:5001/proxy", 
                                  fg="blue", 
                                  cursor="hand2")
        local_api_label.pack(side=tk.LEFT)
        
        # 绑定点击事件
        local_api_label.bind('<Button-1>', self.copy_local_api)

        # 创建按钮框架
        button_frame = tk.Frame(root)
        button_frame.grid(row=1, column=0, padx=10, pady=0, sticky=tk.EW)

        # 保存配置按钮
        self.save_button = tk.Button(button_frame, text="保存代理配置", command=self.save_mapping)
        self.save_button.pack(side=tk.LEFT, padx=(0, 10))

        # 获取代理测试按钮
        self.submit_button = tk.Button(button_frame, text="获取代理测试", command=self.get_proxy)
        self.submit_button.pack(side=tk.LEFT)

        # 原有的控件，行号需要往后移动一行
        tk.Label(root, text="代理提取 API 地址:").grid(row=2, column=0, padx=10, pady=0, sticky=tk.W)
        tk.Entry(root, textvariable=self.url).grid(row=3, column=0, padx=10, pady=0, sticky=tk.EW)
        
        tk.Label(root, text="字段映射 (JSON格式):").grid(row=4, column=0, padx=10, pady=(10, 0), sticky=tk.W)
        self.text_mapping = tk.Text(root, height=8, wrap="word")
        self.text_mapping.grid(row=5, column=0, padx=10, pady=0, sticky=tk.EW)

        # 创建结果框架
        res_frame = tk.Frame(root)
        res_frame.grid(row=6, column=0, padx=10, pady=10, sticky=tk.EW)
        res_frame.grid_columnconfigure((0, 1), weight=1)
        res_frame.grid_rowconfigure(0, weight=1)

        self.text_res = tk.Text(res_frame, height=12, wrap='word')
        self.text_res.grid(row=0, column=0, padx=(0, 10), pady=0, sticky=tk.NSEW)

        self.text_use = tk.Text(res_frame, height=12, wrap='word')
        self.text_use.grid(row=0, column=1, padx=0, pady=0, sticky=tk.NSEW)

        # 配置列的权重，使其可以随窗口调整大小
        root.grid_columnconfigure(0, weight=1)

        # 如果没有从配置文件加载到映射，则使用默认值
        if not self.mapping.get():
            default_mapping = '''{
    "type": "http",
    "ip": "data,0,ip",
    "port": "data,0,port",
    "username": "auth,username",
    "password": "auth,password"
}'''
            self.mapping.set(default_mapping)
        self.text_mapping.insert(tk.END, self.mapping.get())

    def load_config(self):
        """从配置文件加载设置"""
        config = configparser.ConfigParser()
        
        if os.path.exists(self.config_file):
            config.read(self.config_file, encoding='utf-8')
            if 'Settings' in config:
                # 加载 API URL
                self.url.set(config.get('Settings', 'api_url', fallback=''))
                global api_url
                api_url = self.url.get()

                # 加载字段映射
                mapping_str = config.get('Settings', 'field_mapping', fallback='')
                if mapping_str:
                    self.mapping.set(mapping_str)
                global field_mapping
                field_mapping = self.mapping.get()

    def save_config(self):
        """保存设置到配置文件"""
        config = configparser.ConfigParser()
        config['Settings'] = {
            'api_url': self.url.get(),
            'field_mapping': self.mapping.get()
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as configfile:
            config.write(configfile)

    def update_url(self, *args):
        global api_url
        api_url = self.url.get()
        self.save_config()  # 保存更新后的设置

    def update_mapping(self, *args):
        global field_mapping
        try:
            # 尝试解析 JSON 格式
            mapping_text = self.mapping.get()
            json.loads(mapping_text)  # 验证 JSON 格式
            field_mapping = mapping_text
            self.text_mapping.delete(1.0, tk.END)
            self.text_mapping.insert(tk.END, mapping_text)
            self.save_config()  # 保存更新后的设置
        except json.JSONDecodeError:
            # JSON 格式无效时不更新
            pass

    def save_global(self):
        # 获取文本框内容
        mapping_text = self.text_mapping.get(1.0, tk.END).strip()
        # 验证 JSON 格式
        json.loads(mapping_text)
        # 更新变量
        self.mapping.set(mapping_text)
        global field_mapping
        field_mapping = mapping_text
        global api_url
        api_url = self.url.get()

    def save_mapping(self):
        """保存字段映射配置"""
        try:
            # 保存配置
            self.save_config()
            messagebox.showinfo("成功", "代理配置已保存")
            self.save_global()
        except json.JSONDecodeError:
            messagebox.showerror("错误", "JSON 格式无效，请检查配置")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置时出错: {str(e)}")

    def get_proxy(self):
        try:
            response = requests.post('http://127.0.0.1:5001/proxy')
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'success':
                    proxy_info = data['proxy']
                    self.text_res.delete(1.0, tk.END)
                    
                    # 显示原始响应数据
                    self.text_res.insert(tk.END, "接口原始数据:\n")
                    formatted_json = json.dumps(data, ensure_ascii=False, indent=4)
                    self.text_res.insert(tk.END, f"{formatted_json}\n\n")

                    self.text_use.delete(1.0, tk.END)
                    
                    # 显示格式化后的代理信息
                    self.text_use.insert(tk.END, "有效代理数据:\n")
                    self.text_use.insert(tk.END, f"类型: {proxy_info['type']}\n"
                                                 f"主机: {proxy_info['ip']}\n"
                                                 f"端口: {proxy_info['port']}\n"
                                                 f"用户: {proxy_info['username']}\n"
                                                 f"密码: {proxy_info['password']}")
                else:
                    messagebox.showerror("错误", data['message'])
            else:
                data = response.json()
                messagebox.showerror("错误", "请求失败，状态码：" + str(response.status_code) + f"\n错误信息：{data['message']}")

        except Exception as e:
            messagebox.showerror("错误", str(e))

    def copy_local_api(self, event):
        """复制本地API地址到剪贴板"""
        api_address = "http://127.0.0.1:5001/proxy"
        self.root.clipboard_clear()
        self.root.clipboard_append(api_address)
        
        # 显示提示信息
        messagebox.showinfo("成功", "本地代理服务地址已复制到剪贴板")


if __name__ == "__main__":
    # 启动 Flask 服务
    from threading import Thread
    flask_thread = Thread(target=lambda: app.run(port=5001, debug=True, use_reloader=False))
    flask_thread.start()

    # 启动 Tkinter 界面
    root = tk.Tk()
    app = ProxyApp(root)
    root.mainloop()
