# zh_mcp_server介绍
一种用于知乎发文章的模型上下文协议（MCP）服务器，使用者可以通过该服务与大模型自动生成文章并在知乎发文章。

# 使用方法

## 1. 克隆代码

```
git https://github.com/Victorzwx/zh_mcp_server.git
```

## 2. 环境配置前提

建议在Windows环境下运行
  
python版本要求 >= 3.10

- **方式1：**

配置环境要求满足 requirements.txt 文件的要求
  - selenium>=4.0.0
  - requests>=2.25.1
  - mcp>=0.1.0
  - webdriver-manager>=3.8.0
可以通过如下代码安装：
```
pip install -r requirements.txt
```
然后安装ChromeDriver，本项目依赖于谷歌浏览器，134.0.6998.166是版本号，需要手动查询使用者电脑上的谷歌浏览器版本
```
npx @puppeteer/browsers install chromedriver@134.0.6998.166
```
- **方式2：**
  
运行setup_environment.py，如果该方式失败则有可能是ChromeDriver版本不正确，建议以方式1重新安装
```
python setup_environment.py
```

## 3.保存个人cookie

在该代码文件夹下运行保存cookie的代码：

```
python -m zh_mcp_server.__login__
```
- 注意运行后会自动打开谷歌浏览器
- 在谷歌浏览器输入使用者的手机账号，然后点击获取验证码
- 然后，将得到的**验证码输入到Terminal**，即运行python -m zh_mcp_server.__login__的终端，这很重要！

## 4. 在MCP客户端（如Cherry Studio）配置MCP服务
通过python的方式运行
```
"zh_mcp_server": {
      "command": "python",
      "args": [
        "-m",
        "zh_mcp_server"
      ]
 }
```
然后就可以使用了

如果是通过代码使用该MCP服务，如基于Spring AI的JAVA代码，还需要加上编码方式，以避免生成乱码：
```
"zh_mcp_server": {
      "command": "D:\\aconda\\python.exe",
      "args": [
        "-m",
        "zh_mcp_server",
        "--encoding=utf-8"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
```

# 调试
如果需要调试大模型调用该MCP服务时的具体过程或者可视化浏览器的操作，需要关闭无头浏览器模式，如下：
```
poster = ZhuHuPoster(path, headless=True)##如果要调试，请设置为False
```
代码位于server.py中
# CSDN
[本人CSDN账号](https://blog.csdn.net/qq_61302385?type=blog)

# 微信
![image](https://github.com/user-attachments/assets/f7a51982-917f-48b1-9d1f-9f90dc02143f)
