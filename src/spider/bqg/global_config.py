import requests
import pymysql
from rich.panel import Panel
from rich.progress import Progress


class FrameProgress(Progress):
    def get_renderables(self):
        yield Panel(self.make_tasks_table(self.tasks), expand=False)


# 全局变量
requests.packages.urllib3.disable_warnings()
session = requests.session()  # 创建会话
maxThread = 16  # 最大线程数
db = pymysql.connect(
    host="bj-cynosdbmysql-grp-jrtc8xqu.sql.tencentcdb.com",
    user="tutu",
    password="1234TTtt",
    port=23423,
    database="novel",
    charset="utf8",
)
cursor = db.cursor()
