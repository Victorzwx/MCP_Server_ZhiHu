# 小红书的自动发稿
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import json
import os
import sys
import subprocess
import platform
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ZhuHuPoster')

class ZhuHuPoster:
    def __init__(self, path=os.path.dirname(os.path.abspath(__file__)), headless=False):
        # 创建 Chrome 选项对象
        chrome_options = Options()
        # 如果 headless 为 True，则设置为无头模式
        if headless:
            chrome_options.add_argument('--headless=new')  # 使用新的无头模式
            chrome_options.add_argument('--disable-gpu')  # 禁用 GPU 加速
            chrome_options.add_argument('--window-size=1920,1080')  # 设置窗口大小
            chrome_options.add_argument('--no-sandbox')  # 禁用沙盒模式
            chrome_options.add_argument('--disable-dev-shm-usage')  # 禁用 /dev/shm 使用
        
        # 添加更多选项以提高稳定性
        chrome_options.add_argument('--disable-extensions')  # 禁用扩展
        chrome_options.add_argument('--disable-popup-blocking')  # 禁用弹出窗口阻止
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')  # 禁用自动化控制检测
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])  # 排除自动化开关
        chrome_options.add_experimental_option('useAutomationExtension', False)  # 不使用自动化扩展
        
        # 尝试多种方式初始化 Chrome 驱动
        self.driver = self._initialize_chrome_driver(chrome_options)
        
        # 设置等待时间为 10 秒
        self.wait = WebDriverWait(self.driver, 10)

        # 保存路径
        self.path = path
        # 设置 cookies 文件路径 - 修改为直接使用xiaohongshu_cookies.json
        self.cookies_file = os.path.join(os.path.dirname(__file__), "zhihu_cookies.json")
        # 确保目录存在
        os.makedirs(os.path.dirname(self.cookies_file), exist_ok=True)

        
        # 输出cookies文件路径，便于调试
        print(f"Cookies文件路径: {self.cookies_file}")
        
        # 加载 cookies
        self._load_cookies()

    def _initialize_chrome_driver(self, chrome_options):
        """尝试多种方式初始化 Chrome 驱动"""
        methods = [
            self._init_with_default,
            self._init_with_service,
            self._init_with_executable_path,
            self._init_with_system_chrome,
            self._init_with_webdriver_manager
        ]
        
        for method in methods:
            try:
                logger.info(f"尝试使用方法 {method.__name__} 初始化 Chrome 驱动")
                driver = method(chrome_options)
                if driver:
                    logger.info(f"使用方法 {method.__name__} 成功初始化 Chrome 驱动")
                    return driver
            except Exception as e:
                logger.error(f"使用方法 {method.__name__} 初始化 Chrome 驱动失败: {str(e)}")
                continue
        
        # 如果所有方法都失败，抛出异常
        raise Exception("无法初始化 Chrome 驱动，请确保已安装 Chrome 浏览器并将 ChromeDriver 添加到系统路径中")

    def _init_with_default(self, chrome_options):
        """使用默认方式初始化 Chrome 驱动"""
        return webdriver.Chrome(options=chrome_options)
    
    def _init_with_service(self, chrome_options):
        """使用 Service 对象初始化 Chrome 驱动"""
        service = Service()
        return webdriver.Chrome(service=service, options=chrome_options)
    
    def _init_with_executable_path(self, chrome_options):
        """使用可执行路径初始化 Chrome 驱动"""
        # 尝试在常见位置查找 chromedriver
        possible_paths = [
            "chromedriver.exe",  # 当前目录
            os.path.join(os.path.dirname(__file__), "chromedriver.exe"),  # 包目录
            os.path.join(os.path.expanduser("~"), "chromedriver.exe"),  # 用户目录
            r"C:\Program Files\Google\Chrome\Application\chromedriver.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                service = Service(executable_path=path)
                return webdriver.Chrome(service=service, options=chrome_options)
        
        # 如果找不到，尝试使用 PATH 中的 chromedriver
        return None
    
    def _init_with_system_chrome(self, chrome_options):
        """尝试使用系统 Chrome 浏览器路径初始化 Chrome 驱动"""
        # 获取 Chrome 浏览器路径
        chrome_path = self._get_chrome_path()
        if chrome_path:
            chrome_options.binary_location = chrome_path
            return webdriver.Chrome(options=chrome_options)
        return None
    
    def _init_with_webdriver_manager(self, chrome_options):
        """使用 webdriver_manager 初始化 Chrome 驱动"""
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            return webdriver.Chrome(service=service, options=chrome_options)
        except ImportError:
            # 如果没有安装 webdriver_manager，尝试安装
            subprocess.check_call([sys.executable, "-m", "pip", "install", "webdriver-manager"])
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            return webdriver.Chrome(service=service, options=chrome_options)
    
    def _get_chrome_path(self):
        """获取系统 Chrome 浏览器路径"""
        system = platform.system()
        if system == "Windows":
            # Windows 系统下的常见 Chrome 路径
            possible_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    return path
        elif system == "Darwin":  # macOS
            return "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        elif system == "Linux":
            # 尝试使用 which 命令查找 Chrome
            try:
                return subprocess.check_output(["which", "google-chrome"]).decode().strip()
            except:
                return None
        return None

    def _load_cookies(self):
        """从文件加载cookies"""
        if os.path.exists(self.cookies_file):
            try:
                # 打开 cookies 文件
                with open(self.cookies_file, 'r') as f:
                    # 加载 cookies
                    cookies = json.load(f)
                    # 访问知乎创作者中心
                    self.driver.get("https://zhuanlan.zhihu.com/write")
                    # 添加 cookies
                    for cookie in cookies:
                        # 移除可能导致问题的属性
                        if 'expiry' in cookie:
                            del cookie['expiry']
                        # 确保域名正确
                        if 'domain' in cookie:
                            if cookie['domain'].startswith('.'):
                                cookie['domain'] = cookie['domain']
                            else:
                                cookie['domain'] = '.zhihu.com'
                        try:
                            self.driver.add_cookie(cookie)
                        except Exception as e:
                            print(f"添加单个cookie失败: {e}")
                            continue
                    # 添加完cookies后再访问创作者中心
                    self.driver.get("https://zhuanlan.zhihu.com/write")
                # 返回 True 表示成功加载 cookies
                return True
            except Exception as e:
                # 打印错误信息
                print(f"加载 cookies 失败: {e}")
                # 返回 False 表示加载 cookies 失败
                return False
        # 如果 cookies 文件不存在，返回 False
        return False

    def _save_cookies(self):
        """保存cookies到文件"""
        # 获取当前的 cookies
        cookies = self.driver.get_cookies()
        # 确保目录存在
        os.makedirs(os.path.dirname(self.cookies_file), exist_ok=True)
        # 将 cookies 保存到文件
        with open(self.cookies_file, 'w') as f:
            json.dump(cookies, f)

    def login(self):
        """登录知乎"""
        # 访问知乎写文章页面
        self.driver.get("https://zhuanlan.zhihu.com/write")
        # 加载 cookies
        cookies_loaded = self._load_cookies()
        # 刷新页面
        self.driver.refresh()
        # 等待 1.5 秒
        time.sleep(1.5)
        
        # 检查是否已经登录
        if self.driver.current_url != "https://www.zhihu.com/signin?next=http%3A%2F%2Fzhuanlan.zhihu.com%2Fwrite":
            print("使用cookies登录成功")
            # 保存 cookies
            self._save_cookies()
            # 等待 2 秒
            time.sleep(2)
            # 登录成功，返回
            return True
        else:
            # 清理无效的cookies
            self.driver.delete_all_cookies()
            print("无效的cookies，已清理")

        # 如果cookies登录失败，则进行手动登录
        self.driver.get("https://www.zhihu.com/signin?next=http%3A%2F%2Fzhuanlan.zhihu.com%2Fwrite")


        # 输入验证码
        verification_code = input("请输入验证码: ")
        # 定位验证码输入框
        code_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='输入 6 位短信验证码']")))
        # 清空输入框
        code_input.clear()
        # 输入验证码
        code_input.send_keys(verification_code)

        # 点击登录按钮
        login_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/main/div/div/div/div/div[2]/div/div[1]/div/div[1]/form/button")))
        login_button.click()

        # 等待登录成功
        time.sleep(3)
        # 保存cookies
        self._save_cookies()
        
        # 返回登录成功
        return True

    def post_article(self, title, content, images=None, topic=None):
        """发布文章
        Args:
            title: 文章标题
            content: 文章内容
            images: 文章封面图片路径，可以是单个字符串路径或包含一个路径的列表，也可以为空
            topic: 文章话题，如果为None则自动选择最相关的话题
        """

        # 处理图片上传
        if images:
            # 确定图片路径
            img_path = ""
            if isinstance(images, list) and len(images) > 0:
                img_path = images[0]  # 只使用列表中的第一个路径
            elif isinstance(images, str):
                img_path = images  # 直接使用字符串路径
            
            # 如果有有效路径且文件存在，则上传
            if img_path and os.path.exists(img_path):
                try:
                    # 使用更精确的CSS选择器定位上传输入框
                    upload_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file'][accept='.jpeg, .jpg, .png']")
                    
                    # 确保图片路径是绝对路径
                    img_path = os.path.abspath(img_path)
                    logger.info(f"准备上传图片: {img_path}")
                    
                    # 直接使用JavaScript执行上传
                    self.driver.execute_script(
                        "arguments[0].style.display = 'block'; arguments[0].style.visibility = 'visible';", 
                        upload_input
                    )
                    
                    # 上传单个图片
                    upload_input.send_keys(img_path)
                    logger.info(f"已发送图片路径: {img_path}")
                    
                    # 给上传更多时间
                    time.sleep(10)
                    
                    # 检查上传是否成功
                    try:
                        # 尝试查找上传成功后的元素
                        self.driver.find_element(By.CSS_SELECTOR, ".css-uas1lu")
                        logger.info("图片上传成功")
                    except:
                        logger.warning("未检测到图片上传成功的元素，但继续执行")
                        
                except Exception as e:
                    logger.error(f"上传图片失败: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
            else:
                logger.warning(f"图片路径无效或文件不存在: {img_path}")
        
        # 限制标题长度为100字
        title = title[:100]
        
        # 输入标题 - 使用新的选择器
        try:
            # 根据新的HTML结构定位标题输入框
            title_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea.Input[placeholder='请输入标题（最多 100 个字）']")))
            title_input.clear()
            title_input.send_keys(title)
            logger.info(f"已输入标题: {title}")
            
            # 等待标题输入后页面变化
            time.sleep(2)
        except Exception as e:
            logger.error(f"输入标题失败: {e}")
            import traceback
            logger.error(traceback.format_exc())

            # 输入内容 - 使用新的方法
        try:
                # 首先点击编辑区域以激活它
            editor_area = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".public-DraftEditor-content")))

            editor_area.click()
            time.sleep(1)
            editor_area.send_keys(content)
            logger.info("已使用send_keys输入文章内容")

            time.sleep(2)  # 等待内容加载
        except Exception as e:
            logger.error(f"输入文章内容失败: {e}")
            import traceback
            logger.error(traceback.format_exc())

        #     # 等待2秒
        # time.sleep(2)

        # 处理话题选择 - 使用新的选择器和方法
        try:

                # 首先尝试定位添加话题按钮
            add_topic_btn = self.driver.find_element(By.CSS_SELECTOR, "button.css-1gtqxw0")

                
                # 使用JavaScript点击按钮，避免元素不可点击的问题
            self.driver.execute_script("arguments[0].click();", add_topic_btn)
            logger.info("已使用JavaScript点击添加话题按钮")
                
            time.sleep(1)
            
                # 在搜索框中输入话题关键词
            search_topic = topic if topic else title[:4]  # 如果没有指定话题，使用标题的前4个字符
            topic_search_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.Input[placeholder='搜索话题...']")))
            topic_search_input.clear()
            topic_search_input.send_keys(search_topic)
            logger.info(f"已在话题搜索框输入: {search_topic}")
            time.sleep(2)
                
                # 检查是否出现预设话题按钮
            preset_topic_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button.css-gfrh4c")
            if preset_topic_buttons and len(preset_topic_buttons) > 0:
                    # 选择第一个预设话题
                preset_topic_buttons[0].click()


            time.sleep(1)
        except Exception as e:
            logger.error(f"处理话题选择失败: {e}")
            import traceback
            logger.error(traceback.format_exc())

        # 输出内容到控制台
        print(content)

        # 点击发布按钮 - 使用新的选择器
        try:
            # 等待发布按钮变为可点击状态
            self.wait.until(lambda driver: not driver.find_element(By.CSS_SELECTOR, 
                "button.Button--primary.Button--blue").get_attribute("disabled"))
            
            # 点击发布按钮
            submit_btn = self.driver.find_element(By.CSS_SELECTOR, "button.Button--primary.Button--blue")
            submit_btn.click()
            logger.info("已点击发布按钮")

            
        except Exception as e:
            logger.error(f"点击发布按钮失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
        # 等待8s
        time.sleep(8)
        # 输出发布成功信息
        print('发布成功')
        # 返回发布成功
        return True


    def close(self):
        """关闭浏览器"""
        # 关闭浏览器
        self.driver.quit()

