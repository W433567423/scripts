import requests
import pymysql
import requests.adapters
from rich.panel import Panel
from rich.progress import Progress
from rich.console import Console

console = Console()


class FrameProgress(Progress):
    def get_renderables(self):
        yield Panel(self.make_tasks_table(self.tasks), expand=False)


# 全局变量
maxThread = 16  # 最大线程数
requests.packages.urllib3.disable_warnings()  # 关闭警告
# requests.adapters.DEFAULT_RETRIES = 3  # 重试次数
session = requests.session()  # 创建会话
# session.keep_alive = False  # 关闭多余连接

# 连接数据库
conn = pymysql.connect(
    host="bj-cynosdbmysql-grp-jrtc8xqu.sql.tencentcdb.com",
    user="tutu",
    password="1234TTtt",
    port=23423,
    database="novel",
    charset="utf8",
)


# 检查数据库连接是否正常
def valid_conn():

    try:
        console.log("🚀 ~ valid_conn:", conn.ping())
    except:
        console.log("🚀 ~ 正在重连数据库:")
        conn = pymysql.connect(
            host="bj-cynosdbmysql-grp-jrtc8xqu.sql.tencentcdb.com",
            user="tutu",
            password="1234TTtt",
            port=23423,
            database="novel",
            charset="utf8",
        )  # 连接数据库


console.log("🚀 ~ conn.get_server_info():", conn.get_server_info())
