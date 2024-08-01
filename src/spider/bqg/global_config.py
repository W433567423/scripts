import requests
import os
import pymysql
import requests.adapters
from rich.panel import Panel
from rich.progress import Progress
from rich.console import Console

console = Console()


class FrameProgress(Progress):
    def get_renderables(self):
        yield Panel(
            self.make_tasks_table(self.tasks),
            expand=True,
            border_style="green",
            style="black",
            title=f"正在多线程进行中",
            safe_box=True,
        )


# 全局变量
maxThread = 20  # 最大线程数
requests.packages.urllib3.disable_warnings()  # 关闭警告
# requests.adapters.DEFAULT_RETRIES = 3  # 重试次数
session = requests.session()  # 创建会话
# session.keep_alive = False  # 关闭多余连接
requests.adapters.DEFAULT_POOLSIZE = 16  # 最大连接数
chunk_size = 512  # 分片大小

# 连接数据库
conn = pymysql.connect(
    host="bj-cynosdbmysql-grp-jrtc8xqu.sql.tencentcdb.com",
    user="tutu",
    password="1234TTtt",
    port=23423,
    database="novel",
    charset="utf8",
)


# 设置文件地址
def set_path(path: str):
    return os.path.join(os.path.dirname(__file__), path)
