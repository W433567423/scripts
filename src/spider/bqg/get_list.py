from utils import FrameProgress,maxThread,session,console
from bs4 import BeautifulSoup
from utils import normalize_novel_name,normalize_intro
from rich.progress import MofNCompleteColumn,BarColumn,TimeRemainingColumn
from concurrent.futures import ThreadPoolExecutor, as_completed,wait, ALL_COMPLETED
import time

# 获取小说列表页数
def get_books_list_page_num()->int:
    url = "https://m.biqugen.net/full/1.html"
    res = session.get(url)
    res.encoding = "gbk"
    res.close()
    soup = BeautifulSoup(res.text, "html.parser")
    num_page = int(soup.find("table", class_="page-book").find_all("td")[-1].find("a").attrs["href"].split("/")[-1].split(".")[0])
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
    url = f"https://m.biqugen.net/full/{i}.html"
    try:
        res = session.get(url,timeout=5)
    except Exception:     
        print(f"第{i}页访问异常,{url}")
        return novel_list
    res.encoding = "gbk"
    res.close()
    soup = BeautifulSoup(res.text, "html.parser")
    ul = soup.find("ul", class_="s_m")
    if ul==None:
        print(f"第{i}页获取失败,{url}")
        return novel_list
    items=ul.find_all("li",class_='list-item')
    setFlag=False # 用于判断是否已经设置了total
    for item in items:
        novel = {
            "book_id": 0,
            "book_name": "",
            }
        novel["book_name"] = normalize_novel_name(item.find("a").text)
        if not setFlag:
            setFlag=True
        if novel["book_name"] not in novel_set:
            novel_set.add(novel["book_name"])
            novel["book_id"] = int(
                item.find("a").attrs["href"]
                .split("book/")[-1]
                .split("/")[0]
            )
            novel_list.append(novel)
    setFlag=False
    time.sleep(1)
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
    url = f"https://m.biqugen.net/book/{novel["book_id"]}/"
    res=None
    try:
        res = session.get(url,timeout=5)
    except Exception:
        try:
            res = session.get(url,timeout=5)
        except Exception:
            novel["abnormal"] = True
            print(f"获取失败,{url}")
            return
    res.encoding = "gbk"
    res.close()
    soup = BeautifulSoup(res.text, "html.parser")
    info_div = soup.find("div", class_="bookinfo")
    if(info_div==None):
        novel["abnormal"] = True
        print(f"获取info失败,{url}")
        return
    novel["book_cover"] = info_div.find("img").attrs["src"]
    info_td = info_div.find("td", class_="info")
    novel["book_author"] = info_td.find_all("p")[0].find("a").text
    novel["book_category"] = info_td.find_all("p")[1].find("a").text
    novel["write_status"] = '已完结' if info_td.find_all("p")[2].text.split("：")[1] else "连载中"
    # 转换为时间戳
    novel["publish_time"] = time.mktime(time.strptime(info_td.find_all("p")[3].text.split("：")[1], "%Y-%m-%d %H:%M:%S"))
    novel["intro"] = normalize_intro(soup.find("div", class_="intro").text)
    novel["is_extra"] = True


