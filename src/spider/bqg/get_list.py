from global_config import FrameProgress,maxThread,session,console
from bs4 import BeautifulSoup
from utils import normalize_novel_name,normalize_intro
from rich.progress import MofNCompleteColumn,BarColumn,TimeRemainingColumn
from concurrent.futures import ThreadPoolExecutor, as_completed,wait, ALL_COMPLETED

# 获取小说列表页数
def get_books_list_page_num()->int:
    url = "https://www.biqugen.net/quanben/"
    res = session.get(url)
    res.encoding = "gbk"
    res.close()
    soup = BeautifulSoup(res.text, "html.parser")
    num_page = int(soup.find("div", class_="articlepage").find("a", class_="last").text)
    return num_page

# 获取小说列表
def get_books_list()->list:
    novel_set = set() # 用于存储小说名字，避免重复
    novel_list = []
    # 获取每一页的小说列表
    # 开启线程池
    start_num=0
    num_page = get_books_list_page_num()
    taskList=[]
    percent=0
    console.log(f"爬取的页数范围页数: {start_num+1}-{num_page},每页40本小说")
    with FrameProgress(
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.1f}%",
        MofNCompleteColumn(),
        "[cyan]⏳",
        TimeRemainingColumn()
        ) as progress, ThreadPoolExecutor(max_workers=maxThread) as executor:
        task = progress.add_task("从网站获取小说列表", total=num_page-start_num)
        for i in range(start_num,num_page):
            taskList.append(executor.submit(get_books_info_thread,i+1,novel_set))
            # 当一个线程完成时，更新进度条
        for _ in as_completed(taskList):
            percent+=1
            progress.update(task, completed=percent)
        wait(taskList, return_when=ALL_COMPLETED)
        for thread_task in taskList:
            novel_list.extend(thread_task.result())
        progress.update(task, completed=num_page-start_num)
    console.log(f"共获取小说{len(novel_list)}本")
    return novel_list

# 获取第i页小说列表(用于submit)
def get_books_info_thread(i:int,novel_set:list)->list:
    novel_list=[]
    url = f"https://www.biqugen.net/quanben/{i}"
    try:
        res = session.get(url)
    except Exception:     
        print(f"第{i}页获取失败,https://www.biqugen.net/quanben/{i}")
        return novel_list
    res.encoding = "gbk"
    res.close()
    soup = BeautifulSoup(res.text, "html.parser")
    tlist = soup.find("div", id="tlist")
    if tlist==None:
        print(f"第{i}页获取失败,https://www.biqugen.net/quanben/{i}")
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
            }
        novel["book_name"] = normalize_novel_name(
            item.find("div", class_="zp").find("a", class_="name").text
        )
        if not setFlag:
            setFlag=True
        if novel["book_name"] not in novel_set:
            novel_set.add(novel["book_name"])
            novel["book_link"] = (
                item.find("div", class_="zp").find("a", class_="name").attrs["href"]
            )
            novel["book_id"] = int(
                item.find("div", class_="zp")
                .find("a", class_="name")
                .attrs["href"]
                .split("book/")[-1]
                .split("/")[0]
            )
            novel["book_author"] = item.find("div", class_="author").text
            novel["book_publish_time"] = item.find("div", class_="sj").text
            novel_list.append(novel)
    setFlag=False
    return novel_list

# 逐本获取小说其他信息
def get_books_other_info(novel_list:list)->list:
    with FrameProgress(
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.1f}%",
        MofNCompleteColumn(),
        "[cyan]⏳",
        TimeRemainingColumn()
        ) as progress, ThreadPoolExecutor(max_workers=maxThread) as executor:
        task_list = []
        task = progress.add_task("获取小说其他信息", total=len(novel_list))
        for novel in novel_list:
            task_list.append(executor.submit(get_books_other_info_thread,novel))
        for _ in as_completed(task_list):
            progress.update(task, advance=1)
        wait(task_list, return_when=ALL_COMPLETED)
    console.log("获取小说其他信息完成")
    return novel_list

# 获取某本小说其他信息(用于submit)
def get_books_other_info_thread(novel:dict)->None:
    url = f"https://www.biqugen.net/book/{novel["book_id"]}/"
    try:
        res = session.get(url)
    except Exception:
        print (f"{url}访问失败")
        return 
    res.encoding = "gbk"
    res.close()
    soup = BeautifulSoup(res.text, "html.parser")
    info = soup.find("div", id="info")
    if(info==None):
        return
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
    novel["is_extra"] = True


# ---------------------------------------------------
