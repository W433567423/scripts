# TODO 爬取笔趣阁小说并保存在本地
import pymysql
import requests
from bs4 import BeautifulSoup
from utils import normalize_novel_name
from rich.progress import (
    Progress,
    MofNCompleteColumn,
    TextColumn,
    BarColumn,
    TimeRemainingColumn,
)
from concurrent.futures import ThreadPoolExecutor, as_completed, wait, ALL_COMPLETED
import time
from rich.panel import Panel


class FrameProgress(Progress):
    def get_renderables(self):
        yield Panel(self.make_tasks_table(self.tasks), expand=False)


# 1-5.重置数据库表books
def reset_books_list_to_db():
    # 删除表books
    cursor.execute("DROP TABLE IF EXISTS books")
    # 创建表books，id:自增主键
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS books(
            id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
            book_id INT COMMENT '笔趣阁小说id' not null,
            book_name VARCHAR(255) COMMENT '小说名' not null,
            book_link VARCHAR(255) COMMENT '小说链接' not null,
            book_author VARCHAR(255) COMMENT '小说作者',
            book_publish_time VARCHAR(255) COMMENT '小说发布时间',
            write_status VARCHAR(255) COMMENT '小说连载状态',
            file_path VARCHAR(255) COMMENT '小说文件路径',
            popularity VARCHAR(255) COMMENT '小说人气',
            intro TEXT COMMENT '小说简介',
            abnormal BOOLEAN DEFAULT FALSE COMMENT '是否异常'
        )
    """
    )
    db.commit()
    print("数据库表books重置成功")


# 2.从数据库中获取小说列表
def get_books_list_from_db():
    novel_list = []
    novel = {
        "book_id": 0,
        "book_name": "",
        "book_link": "",
        "book_author": "",
        "book_publish_time": "",
        "write_status": "",
        "popularity": "",
        "intro": "",
        "abnormal": False,
    }
    # 需要获取的值：id,book_id,book_name,book_link,book_author,write_status,popularity,intro,abnormal,file_path
    cursor.execute(
        "SELECT id,book_id,book_name,book_link,book_author,write_status,popularity,intro,abnormal,file_path FROM books"
    )
    db_list = cursor.fetchall()
    print("获取数据库中的小说列表成功")
    with FrameProgress() as progress:
        task = progress.add_task("转化为novel_list", total=len(db_list))
        for db in db_list:
            novel["id"] = db[0]
            novel["book_id"] = db[1]
            novel["book_name"] = db[2]
            novel["book_link"] = db[3]
            novel["book_author"] = db[4]
            novel["write_status"] = db[5]
            novel["popularity"] = db[6]
            novel["intro"] = db[7]
            novel["abnormal"] = db[8]
            novel["file_path"] = db[9]
            novel_list.append(novel)
            progress.update(task, advance=1)
            # 等待0.001秒
            time.sleep(0.001)
    return novel_list


# 3.获取小说章节
def get_chapters():

    pass


# 4.保存小说内容

# 入口
if __name__ == "__main__":
    # 全局变量
    session = requests.session()  # 创建会话
    maxThread = None  # 最大线程数
    db = pymysql.connect(
        host="bj-cynosdbmysql-grp-jrtc8xqu.sql.tencentcdb.com",
        user="tutu",
        password="1234TTtt",
        port=23423,
        database="novel",
        charset="utf8",
    )
    cursor = db.cursor()
    # reset_books_list_to_db()
    novel_list = get_books_list_from_db()
    print(novel_list[5])
    cursor.close()
    db.close()
