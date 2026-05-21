"""开发入口——IDE 右键运行此文件即可启动服务。"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from astra_pro.main import main

if __name__ == "__main__":
    main()
