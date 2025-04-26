from . import server

def main():
    """Main entry point for the package."""
    server.main()  # 修改为调用server.py中的main函数

def login():
    """Login entry point for the package."""
    server.login()  # 修改为调用server.py中的login函数

# Expose important items at package level
__all__ = ['main', 'server','login']