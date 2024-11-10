import requests
import json
import time


# 比特浏览器API调用
class Bit:
    def __init__(self, url=None, headers=None, name=None, proxy=None, finger=None, abortImage=False, abortMedia=False):
        if url:
            self.url = url
        else:
            self.url = "http://127.0.0.1:54345"
        if headers:
            self.headers = headers
        else:
            self.headers = {'Content-Type': 'application/json'}
        if not name:
            name = time.time()
        if proxy:
            self.json_data = {
                'name': name,  # 窗口名称
                'remark': '',  # 备注
                'proxyMethod': 2,  # 代理方式 2自定义 3 提取IP
                # 自定义代理类型['noproxy', 'http', 'https', 'socks5', 'ssh']中一个，默认noproxy
                'proxyType': proxy['type'],
                'host': proxy['host'],  # 代理主机
                'port': proxy['port'],  # 代理端口
                'proxyUserName': proxy['username'],  # 代理账号
                'proxyPassword': proxy['password'],
                "browserFingerPrint": {  # 指纹对象
                    'coreVersion': '124'  # 内核版本，注意，win7/win8/winserver 2012 已经不支持112及以上内核了，无法打开
                }
            }
        else:
            self.json_data = {
                'name': name,  # 窗口名称
                'remark': '',  # 备注
                'proxyMethod': 2,  # 代理方式 2自定义 3 提取IP
                # 自定义代理类型['noproxy', 'http', 'https', 'socks5', 'ssh']中一个，默认noproxy
                'proxyType': 'noproxy',
                "browserFingerPrint": {  # 指纹对象
                    'coreVersion': '124'  # 内核版本，注意，win7/win8/winserver 2012 已经不支持112及以上内核了，无法打开
                }
            }
        if abortImage:
            self.json_data['abortImage'] = True
        if abortMedia:
            self.json_data['abortMedia'] = True
        if finger:
            self.json_data['browserFingerPrint'] = finger
        self.ids = []
        self.health()

    def health(self):
        res = requests.post(f"{self.url}/health").json()
        print(res)

    # 创建浏览器窗口
    def create(self):
        res = requests.post(f"{self.url}/browser/update",
                            data=json.dumps(self.json_data), headers=self.headers).json()
        browser_id = res['data']['id']
        print(f"浏览器ID:{browser_id}")
        self.ids.append(browser_id)
        return browser_id

    # 打开浏览器窗口
    def open(self, browser_id):
        if browser_id not in self.ids:
            return None
        json_data = {"id": f'{browser_id}'}
        res = requests.post(f"{self.url}/browser/open",
                            data=json.dumps(json_data), headers=self.headers).json()
        return res

    # 关闭浏览器窗口
    def close(self, browser_id):
        if browser_id not in self.ids:
            return None
        json_data = {"id": f'{browser_id}'}
        print("关闭浏览器窗口", requests.post(f"{self.url}/browser/close",
                                       data=json.dumps(json_data), headers=self.headers).json())

    # 关闭所有浏览器窗口
    def close_all(self):
        print(requests.post(f"{self.url}/browser/close/all"))

    # 重置浏览器关闭状态
    def reset(self, browser_id):
        if browser_id not in self.ids:
            return None
        json_data = {"id": f'{browser_id}'}
        print("重置浏览器关闭状态", requests.post(f"{self.url}/browser/reset",
                                         data=json.dumps(json_data), headers=self.headers).json())

    # 删除浏览器窗口
    def delete(self, browser_id):
        if browser_id not in self.ids:
            return None
        json_data = {"id": f'{browser_id}'}
        print("删除浏览器窗口", requests.post(f"{self.url}/browser/delete",
                                       data=json.dumps(json_data), headers=self.headers).json())
        self.ids.remove(browser_id)

    # 获取浏览器窗口详情
    def detail(self, browser_id):
        if browser_id not in self.ids:
            return None
        json_data = {"id": f'{browser_id}'}
        return requests.post(f"{self.url}/browser/delete",
                             data=json.dumps(json_data), headers=self.headers).json()

    # 清理窗口缓存
    def clear(self, browser_ids):
        json_data = {"ids": browser_ids}
        return requests.post(f"{self.url}/cache/clear",
                             data=json.dumps(json_data), headers=self.headers).json()

    # 一键自适应排列窗口
    def flexable(self):
        res = requests.post(f"{self.url}/windowbounds/flexable", headers=self.headers).json()
        print("一键自适应排列窗口", res)
        return res['success']

    # 批量修改窗口代理信息
    def proxy(self, json_data):
        res = requests.post(f"{self.url}/browser/proxy/update",
                            data=json.dumps(json_data), headers=self.headers).json()
        print("批量修改窗口代理信息", res)
        return res['success']

    # 随机指纹值
    def finger(self, browser_id):
        if browser_id not in self.ids:
            return None
        json_data = {"browserId": f'{browser_id}'}
        return requests.post(f"{self.url}/browser/fingerprint/random",
                             data=json.dumps(json_data), headers=self.headers).json()

    # 固定指纹值
    def finger_fix(self, browser_id, finger):
        if browser_id not in self.ids:
            return None
        json_data = {"ids": [browser_id], "browserFingerPrint": json.loads(finger)}
        return requests.post(f"{self.url}/browser/update/partial",
                             data=json.dumps(json_data), headers=self.headers).json()
    
    def run(self, rpa_id):
        json_data = {"id": f'{rpa_id}'}
        print(requests.post(f"{self.url}/rpa/run",
                            data=json.dumps(json_data), headers=self.headers).json())

    def stop(self, rpa_id):
        json_data = {"id": f'{rpa_id}'}
        print(requests.post(f"{self.url}/rpa/stop",
                            data=json.dumps(json_data), headers=self.headers).json())
