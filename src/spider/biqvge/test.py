# TODO 爬取笔趣阁小说并保存在本地
import pymysql
import requests
from bs4 import BeautifulSoup
from utils import normalize_novel_name
from rich.progress import Progress,MofNCompleteColumn,TextColumn,BarColumn,TimeRemainingColumn
from concurrent.futures import ThreadPoolExecutor, as_completed,wait, ALL_COMPLETED
import time
from rich.panel import Panel


class FrameProgress(Progress):
    def get_renderables(self):
        yield Panel(self.make_tasks_table(self.tasks), expand=False)


# 1.获取小说列表
def get_books_list()->list:
    novel_set = set() # 用于存储小说名字，避免重复
    novel_list = []
    # 获取每一页的小说列表
    # 开启线程池
    num_page = get_books_list_page_num()
    num_page=15
    taskList=[]
    with FrameProgress(
        TextColumn("[bold blue]{task.description}", justify="left"),
        BarColumn(),
        MofNCompleteColumn(),
        "[progress.percentage]{task.percentage:>3.1f}%",
        TimeRemainingColumn()) as progress, ThreadPoolExecutor(max_workers=maxThread) as executor:
        task = progress.add_task("[green]获取完本小说列表...", total=num_page)
        for i in range(num_page):
            taskList.append(executor.submit(get_books_info,i+1,novel_list,novel_set,progress))
            # 当一个线程完成时，更新进度条
        for _ in as_completed(taskList):
            percent=len(novel_list)/40
            progress.update(task, completed=percent)
        wait(taskList, return_when=ALL_COMPLETED)
        progress.update(task, completed=num_page)
    print(f"共获取小说{len(novel_list)}本")
    return novel_list

# 1-1.获取小说列表页数
def get_books_list_page_num():
    url = "https://www.biqugen.net/quanben/"
    res = session.get(url)
    res.encoding = "gbk"
    soup = BeautifulSoup(res.text, "html.parser")
    num_page = int(soup.find("div", class_="articlepage").find("a", class_="last").text)
    print(f"完本小说列表总页数: {num_page},每页40本小说")
    return num_page

# 1-2.获取第i页小说列表
def get_books_info(i,novel_list,novel_set,progress):
    task = progress.add_task(f"[blue]获取第{i}页完本小说列表...", total=40)
    url = f"https://www.biqugen.net/quanben/{i}"
    res = session.get(url)
    res.encoding = "gbk"
    soup = BeautifulSoup(res.text, "html.parser")
    items = soup.find("div", id="tlist").find_all("li")
    setFlag=False # 用于判断是否已经设置了total
    for item in items:
        novel = {
            "book_name": "",
            "book_link": "",
            "book_id": 0,
            "book_author": "",
            "book_publish_time": "",
            "write_status": "",
            "popularity": '',
            "intro": "",
            "abnormal": False
        }
        novel["book_name"] = normalize_novel_name(
            item.find("div", class_="zp").find("a", class_="name").text
        )
        if not setFlag:
            progress.update(task, total=len(items))
            setFlag=True
        if novel["book_name"] not in novel_set:
            novel_set.add(novel["book_name"])
            novel["book_link"] = (
                item.find("div", class_="zp").find("a", class_="name").attrs["href"]
            )
            novel["book_id"] = (
                item.find("div", class_="zp")
                .find("a", class_="name")
                .attrs["href"]
                .split("book/")[-1]
                .split("/")[0]
            )
            novel["book_author"] = item.find("div", class_="author").text
            novel["book_publish_time"] = item.find("div", class_="sj").text
            # 获取小说其他信息
            get_books_other_info(novel)
            novel_list.append(novel)
        progress.update(task, advance=1)
    setFlag=False
    progress.update(task, visible=False)

# 1-3.获取小说其他信息
def get_books_other_info(novel)->bool:
    url = f"https://www.biqugen.net/book/{novel["book_id"]}/"
    res = session.get(url)
    res.encoding = "gbk"
    soup = BeautifulSoup(res.text, "html.parser")
    info = soup.find("div", id="info")
    if(info==None):
        novel["abnormal"]=True
        return False
    # 获取小说连载状态
    popularity = info.find("span", class_="blue").text.split("：")[1]
    # 获取小说人气
    write_status = info.find("span", class_="red").text
    # 获取小说简介
    intro = soup.find("div", id="intro").text
    # 去除\xa0
    novel["intro"] = intro.replace("\xa0", "").replace("&amp;", "").replace("#61", "").strip()
    novel["write_status"] = '已完结' if write_status=="已完成" else "连载中"
    novel["popularity"] = popularity
    return True
    
# 1-4.存储小说列表至数据库
def save_books_list_to_db(novel_list:list):
    # 获取数据库中已有的小说列表(仅获取小说名)
    cursor.execute('SELECT book_name FROM books')
    overed_novel_list = cursor.fetchall()
    # 从元组列表中提取小说名
    overed_novel_list_name=(novel[0] for novel in overed_novel_list)
    with FrameProgress(
        TextColumn("[bold blue]{task.description}", justify="left"),
        BarColumn(),
        MofNCompleteColumn(),
        "[progress.percentage]{task.percentage:>3.1f}%",
        TimeRemainingColumn()) as progress:
        task = progress.add_task("小说列表存入数据库...", total=len(novel_list))
        # 将小说列表存入数据库
        for novel in novel_list:
            # 如果数据库中已经存在该小说，则跳过
            if novel["book_name"] not in overed_novel_list_name:
                # 捕获异常
                try:
                    cursor.execute(
                        f'''
                            INSERT INTO books(
                                book_id,
                                book_name,
                                book_link,
                                book_author,
                                book_publish_time,
                                write_status,
                                popularity,
                                intro,
                                abnormal
                            )
                            VALUES(
                                {novel["book_id"]},
                                "{novel["book_name"]}",
                                "{novel["book_link"]}",
                                "{novel["book_author"]}",
                                "{novel["book_publish_time"]}",
                                "{novel["write_status"]}",
                                "{novel["popularity"]}",
                                "{novel["intro"]}",
                                {novel["abnormal"]}
                            )
                        '''
                    )
                except Exception as e:
                    print(f'''
                            INSERT INTO books(
                                book_id,
                                book_name,
                                book_link,
                                book_author,
                                book_publish_time,
                                write_status,
                                popularity,
                                intro,
                                abnormal
                            )
                            VALUES(
                                {novel["book_id"]},
                                "{novel["book_name"]}",
                                "{novel["book_link"]}",
                                "{novel["book_author"]}",
                                "{novel["book_publish_time"]}",
                                "{novel["write_status"]}",
                                "{novel["popularity"]}",
                                "{novel["intro"]}",
                                {novel["abnormal"]}
                            )
                        ''')
            progress.update(task, advance=1)
    db.commit()
    print("小说列表存储成功")
    pass

# 1-5.重置数据库表books
def reset_books_list_to_db():
    # 删除表books
    cursor.execute('DROP TABLE IF EXISTS books')
    # 创建表books，id:自增主键
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books(
            id INT AUTO_INCREMENT PRIMARY KEY,
            book_id INT,
            book_name VARCHAR(255),
            book_link VARCHAR(255),
            book_author VARCHAR(255),
            book_publish_time VARCHAR(255),
            write_status VARCHAR(255),
            file_path VARCHAR(255),
            popularity VARCHAR(255),
            intro TEXT,
            abnormal BOOLEAN DEFAULT FALSE
        )
    ''')
    db.commit()
    print("数据库表books重置成功")


# 2.从数据库中获取小说列表
def get_books_list_from_db():
    cursor.execute('SELECT * FROM books')
    novel_list = cursor.fetchall()
    return novel_list

# 3.获取小说内容

# 4.保存小说内容

# 入口
if __name__ == "__main__":
    # 全局变量
    session = requests.session()  # 创建会话
    maxThread = None  # 最大线程数
    db=pymysql.connect(host='bj-cynosdbmysql-grp-jrtc8xqu.sql.tencentcdb.com',
                       user='tutu',
                       password='1234TTtt',
                       port=23423,
                       database='novel',
                       charset='utf8',
                       )
    cursor = db.cursor()
    print("开始爬取")
    # reset_books_list_to_db()
    novel_list=get_books_list()
    save_books_list_to_db(novel_list)
    cursor.close()
    db.close()
