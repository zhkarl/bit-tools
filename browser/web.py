import requests
import json
from browser.bit import Bit
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import random  # 确保导入 random 模块


class Web:
    def __init__(self, bit: Bit, browser_id):
        self.bit = bit
        self.browser_id = browser_id
        self.open_res = self.bit.open(browser_id)  # 窗口ID从窗口配置界面中复制，或者api创建后返回
        self.path = self.open_res['data']['driver']
        self.address = self.open_res['data']['http']

        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_experimental_option("debuggerAddress", self.address)

        self.chrome_service = Service(self.path)
        self.driver = webdriver.Chrome(service=self.chrome_service, options=self.chrome_options)

    # 访问URL
    def open(self, url):
        """访问指定的URL"""
        self.driver.get(url)

    # 回到顶部
    def top(self):
        """回到顶部"""
        self.driver.execute_script(f"window.scrollTo(0, 0);")

    # 滚动页面
    def scroll(self, scroll_amount):
        """滚动页面"""
        self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")

    # 滚动到指定元素
    def scroll_to_element(self, element_selector):
        """滚动到指定元素的位置"""
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, element_selector)
            self.driver.execute_script("arguments[0].scrollIntoView();", element)
        except NoSuchElementException:
            print(f"元素未找到: {element_selector}")

    # 鼠标悬停
    def hover(self, element_selector):
        """鼠标悬停在指定元素上"""
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, element_selector)
            ActionChains(self.driver).move_to_element(element).perform()
        except NoSuchElementException:
            print(f"元素未找到: {element_selector}")

    # 鼠标点击
    def click(self, element_selector):
        """点击指定元素"""
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, element_selector)
            element.click()
            windows = self.driver.window_handles
            self.driver.switch_to.window(windows[-1])
        except NoSuchElementException:
            print(f"元素未找到: {element_selector}")

    # 元素等待
    def wait_for_element(self, element_selector, timeout=10):
        """等待指定元素出现"""
        end_time = time.time() + timeout
        while time.time() < end_time:
            try:
                self.driver.find_element(By.CSS_SELECTOR, element_selector)
                return True
            except NoSuchElementException:
                time.sleep(0.5)
        print(f"超时: 元素未找到: {element_selector}")
        return False

    # 输入文本
    def input_text(self, element_selector, text):
        """在指定元素中输入文本，一个字一个字地输入"""
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, element_selector)
            element.clear()  # 清空输入框
            
            for char in text:
                element.send_keys(char)  # 一个字一个字地输入
                # 生成随机延迟时间，范围可以根据需要调整
                delay = random.uniform(0.2, 0.8)  # 随机延迟在0.2到0.8秒之间
                time.sleep(delay)  # 随机延迟
        except NoSuchElementException:
            print(f"元素未找到: {element_selector}")

    # 时间等待
    def wait(self, seconds):
        """等待指定的秒数"""
        time.sleep(seconds)

    # 获取页面标题
    def get_title(self):
        """获取当前页面的标题"""
        return self.driver.title

    # 获取当前URL
    def get_current_url(self):
        """获取当前页面的URL"""
        return self.driver.current_url

    # 关闭浏览器
    def close(self):
        """关闭浏览器"""
        self.driver.quit()
    
    # 谷歌搜索
    def google(self, site, keyword, page):
        """
        Google搜索指定关键词，在搜索结果中查找目标站点
        
        Args:
            site: 目标网站域名
            keyword: 搜索关键词
            page: 页码
        Returns:
            bool: 是否找到并点击了目标站点
        """
        try:
            # 遍历指定页码范围
            # 构造Google搜索URL
            search_url = f"https://www.google.com/search?q={keyword}&start={page * 10}"
            self.open(search_url)

            # 等待搜索结果加载
            self.wait(1)

            try:
                # 查找所有搜索结果链接
                search_results = self.driver.find_elements(By.CSS_SELECTOR, "div.g a")

                # 遍历搜索结果
                for result in search_results:
                    href = result.get_attribute("href")
                    if href and site.lower() in href.lower():
                        print(f"YES: 在第 {page + 1} 页找到目标站点: {site}")
                        # 找到目标站点，点击链接
                        result.click()
                        windows = self.driver.window_handles
                        self.driver.switch_to.window(windows[-1])
                        return page + 1

            except NoSuchElementException:
                # 当前页未找到，继续下一页
                print(f"NO: 在第 {page + 1} 页未找到目标站点: {site}")
                
            # 所有页面都搜索完毕，未找到目标站点
            print(f"NO: 在第 {page + 1} 页未找到目标站点: {site}")
            return 0
            
        except Exception as e:
            print(f"Google搜索出错: {str(e)}")
            return 0
        

