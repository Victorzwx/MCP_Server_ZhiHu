import os
import time
import requests
import tempfile
import sys
import logging
import traceback

from mcp.server import FastMCP
from mcp.types import TextContent

from .write_zhihu import ZhuHuPoster

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('zh_mcp_server')

# 初始化 FastMCP 实例，名称为 "zh"
mcp = FastMCP("zh")
# 直接使用包内的data目录
path = os.getenv("json_path", os.path.join(os.path.dirname(__file__), "data"))
# 确保 data 目录存在
os.makedirs(path, exist_ok=True)

def login():
    """登录知乎并保存 cookies"""
    try:
        logger.info("开始登录知乎")
        # 创建 ZhuHuPoster 实例，传入data目录路径
        poster = ZhuHuPoster(path)
        # 登录知乎
        poster.login()
        # 等待 1 秒
        time.sleep(1)
        # 关闭浏览器
        poster.close()
        logger.info("登录知乎成功")
        return True
    except Exception as e:
        logger.error(f"登录知乎失败: {str(e)}")
        traceback.print_exc()
        return False

@mcp.tool()
def create_atticle(title: str, content: str, images: list = None, topic: str = None) -> list[TextContent]:
    """发布文章到知乎
    Args:
        title: 文章标题，不多于100个字符
        content: 文章内容，不少于9个字
        images: 文章封面图片路径，可以是单个字符串路径或包含一个路径的列表，也可以为空，只能是本地文件
        topic: 文章话题，如果为None则根据标题前4个字符选择最相关的话题（这里仅根据标题来寻找话题极有可能找不到），最好为输入为已存在的话题否则无法成功发帖
    """

    logger.info(f"开始创建知乎笔记: 标题={title}")

    # 处理 images 参数，确保它是列表形式
    if images is None:
        images = []
    elif isinstance(images, str):
        images = [images]  # 如果是单个字符串，转换为列表
    
    # 验证图片路径
    valid_images = []
    if images:  # 只有当 images 不为空时才进行验证
        for img_path in images:
            # 检查本地图片是否存在
            if os.path.exists(img_path):
                logger.info(f"使用本地图片: {img_path}")
                valid_images.append(img_path)
            else:
                logger.error(f"图片路径不存在: {img_path}")
                return [TextContent(type="text", text=f"error: 图片路径不存在 - {img_path}")]


    try:
        # 创建 ZhuHuPoster 实例，启用无头模式，传入data目录路径
        logger.info("初始化 ZhuHuPoster")
        poster = ZhuHuPoster(path, headless=True)##如果要调试，请设置为False

        
        # 使用 cookies 登录
        logger.info("使用 cookies 登录")
        login_success = poster.login()
        
        if not login_success:
            logger.error("登录失败")
            return [TextContent(type="text", text="error: 登录失败，请先运行 login 命令设置 cookies")]
        
        # 发布文章，传入话题参数
        logger.info("开始发布文章")
        poster.post_article(title, content, valid_images[0] if valid_images else None, topic)


        # 关闭浏览器
        logger.info("关闭浏览器")
        poster.close()
        
        # 设置结果为成功
        logger.info("发布成功")
        res = "success"
    except Exception as e:
        # 如果发生异常，设置结果为错误信息
        logger.error(f"发布失败: {str(e)}")
        traceback.print_exc()
        res = f"error: {str(e)}"

    # 返回结果
    return [TextContent(type="text", text=res)]



def main():
    """主函数，运行 MCP 服务器"""
    # 运行 MCP 服务器
    mcp.run()

def test_create_note():
    """测试 create_note 函数"""
    # 测试标题
    title = "测试帖子"
    # 测试内容
    content = "这是一个测试帖子，用于测试 create_note 函数。"
    # 测试图片，
    images = ["本地文件"]
    # 测试话题
    topic = "测试"
    # 调用 create_note 函数
    result = create_atticle(title, content, images, topic)
    # 打印结果
    print(result)
    # 返回结果
    return result

if __name__ == "__main__":
    # 如果直接运行此脚本，则运行主函数
    main()