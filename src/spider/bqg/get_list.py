from global_config import maxThread,session,db,headers,FrameProgress
from bs4 import BeautifulSoup
from utils import normalize_novel_name,normalize_intro
from rich.progress import MofNCompleteColumn,BarColumn,TimeRemainingColumn
from concurrent.futures import ThreadPoolExecutor, as_completed,wait, ALL_COMPLETED



# 1.获取小说列表
def get_books_list()->list:
    novel_set = set() # 用于存储小说名字，避免重复
    novel_list = []
    # 获取每一页的小说列表
    # 开启线程池
    start_num=0
    num_page = get_books_list_page_num()
    # num_page=100
    taskList=[]
    percent=0
    print(f"爬取的页数范围页数: {start_num+1}-{num_page},每页40本小说")
    with FrameProgress(
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.1f}%",
        MofNCompleteColumn(),
        "[cyan]⏳",
        TimeRemainingColumn()
        ) as progress, ThreadPoolExecutor(max_workers=maxThread) as executor:
        task = progress.add_task("[green]获取所有小说", total=num_page)
        for i in range(start_num,num_page):
            taskList.append(executor.submit(get_books_info,i+1,novel_set,progress))
            # 当一个线程完成时，更新进度条
        for _ in as_completed(taskList):
            percent+=1
            progress.update(task, completed=percent)
        wait(taskList, return_when=ALL_COMPLETED)
        for thread_task in taskList:
            novel_list.extend(thread_task.result())
        progress.update(task, completed=num_page)
    print(f"共获取小说{len(novel_list)}本")
    return novel_list

# 1-1.获取小说列表页数
def get_books_list_page_num():
    url = "http://www.biqugen.net/quanben/"
    res = session.get(url,headers=headers,timeout=3)
    res.encoding = "gbk"
    res.close()
    soup = BeautifulSoup(res.text, "html.parser")
    num_page = int(soup.find("div", class_="articlepage").find("a", class_="last").text)
    return num_page

# 1-2.获取第i页小说列表
def get_books_info(i,novel_set,progress):
    novel_list=[]
    task = progress.add_task(f"[blue]第{i}页", total=40)
    url = f"http://www.biqugen.net/quanben/{i}"
    res = session.get(url,headers=headers,timeout=3,verify=False)
    res.encoding = "gbk"
    res.close()
    soup = BeautifulSoup(res.text, "html.parser")
    tlist = soup.find("div", id="tlist")
    if tlist==None:
        print(f"第{i}页获取失败,http://www.biqugen.net/quanben/{i}")
        progress.update(task, visible=False)
        return novel_list
    items=tlist.find_all("li")
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
    return novel_list

# 1-3.获取小说其他信息
def get_books_other_info(novel)->bool:
    url = f"http://www.biqugen.net/book/{novel["book_id"]}/"
    try:
        res = session.get(url,headers=headers,timeout=3,verify=False)
    except Exception as e:
        print (f"{url}访问失败")
        return False
    res.encoding = "gbk"
    res.close()
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
    novel["intro"] = normalize_intro(intro)
    novel["write_status"] = '已完结' if write_status=="已完成" else "连载中"
    novel["popularity"] = popularity
    return True
    
# 1-4.存储小说列表至数据库
def save_books_list_to_db(novel_list:list):
    global db
    db.connect()  # 连接
    cursor = db.cursor()  # 创建游标
    # 获取数据库中已有的小说列表(仅获取小说名)
    cursor.execute('SELECT book_name FROM books')
    overed_novel_list = cursor.fetchall()
    # 从元组列表中提取小说名
    overed_novel_list_name=(novel[0] for novel in overed_novel_list)
    with FrameProgress(
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.1f}%",
        MofNCompleteColumn(),
        "[cyan]⏳",
        TimeRemainingColumn()
        ) as progress:
        task = progress.add_task("小说列表存入数据库", total=len(novel_list))
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
    cursor.close()
    db.close()
    print("小说列表存储成功")

# 从数据库获取异常的小说列表
def get_abnormal_books_list_from_db():
    global db
    db.connect()  # 连接
    cursor = db.cursor()  # 创建游标
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
        "SELECT id,book_id,book_name,book_link,book_author,write_status,popularity,intro,abnormal,file_path FROM books WHERE abnormal=TRUE"
    )
    db_list = cursor.fetchall()
    for item in db_list:
        novel["id"] = item[0]
        novel["book_id"] = item[1]
        novel["book_name"] = item[2]
        novel["book_link"] = item[3]
        novel["book_author"] = item[4]
        novel["write_status"] = item[5]
        novel["popularity"] = item[6]
        novel["intro"] = item[7]
        novel["abnormal"] = item[8]
        novel["file_path"] = item[9]
        novel_list.append(novel)
    cursor.close()
    db.close()
    return novel_list

# 更新异常的小说
def update_abnormal_books_list(list:list):
    with FrameProgress(
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.1f}%",
        MofNCompleteColumn(),
        "[cyan]⏳",
        TimeRemainingColumn()
        ) as progress, ThreadPoolExecutor(max_workers=maxThread) as executor:
        task = progress.add_task("更新异常小说", total=len(list))
        for novel in list:
            executor.submit(get_books_info,novel,progress)
            progress.update(task, advance=1)
    return list    
