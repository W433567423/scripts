import requests
import pymysql
from rich.panel import Panel
from rich.progress import Progress


class FrameProgress(Progress):
    def get_renderables(self):
        yield Panel(self.make_tasks_table(self.tasks), expand=False)


# 全局变量
requests.packages.urllib3.disable_warnings()  # 关闭警告
requests.adapters.DEFAULT_RETRIES = 5  # 重试次数
session = requests.session()  # 创建会话
session.keep_alive = False  # 关闭多余连接
maxThread = None  # 最大线程数
db = pymysql.connect(
    host="bj-cynosdbmysql-grp-jrtc8xqu.sql.tencentcdb.com",
    user="tutu",
    password="1234TTtt",
    port=23423,
    database="novel",
    charset="utf8",
)  # 连接数据库
