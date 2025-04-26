import os
import sys
import subprocess
import platform
import requests
import time

def main():
    """设置环境，安装必要的依赖"""
    print("开始设置环境...")
    
    # 安装依赖
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(requirements_path):
        print(f"安装依赖: {requirements_path}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_path])
    else:
        print("安装基本依赖...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium", "requests", "mcp", "webdriver-manager"])
    


    # 尝试安装 ChromeDriver
    try:
        print("安装 ChromeDriver...")
        from webdriver_manager.chrome import ChromeDriverManager
        driver_path = ChromeDriverManager().install()
        print(f"ChromeDriver 已安装到: {driver_path}")
    except Exception as e:
        print(f"安装 ChromeDriver 失败: {str(e)}")
        print("请手动下载 ChromeDriver 并将其添加到系统路径中")
        print("下载地址: https://chromedriver.chromium.org/downloads")
    
    print("环境设置完成")

if __name__ == "__main__":
    main()