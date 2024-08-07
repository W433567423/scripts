from db import  get_chapters_list_from_db,update_novel_download,update_download_wrong
from utils import session,set_path,console, FrameProgress
from rich.progress import BarColumn, MofNCompleteColumn, TimeRemainingColumn
from concurrent.futures import ThreadPoolExecutor,wait
from bs4 import BeautifulSoup
import os

db_tasks = []

# 保存小说内容
def save_novel_list(novel_list: list):
    with FrameProgress(
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.1f}%",
        MofNCompleteColumn(),
        "[cyan]⏳",
        TimeRemainingColumn(),
    ) as progress, ThreadPoolExecutor(max_workers=6) as executor:
        
        task = progress.add_task("正在保存小说至本地", total=len(novel_list))
        task_list = []
        for novel in novel_list:
            chapters_list = get_chapters_list_from_db(novel["novel_id"])
            task_list.append(executor.submit(get_chapter_content_thread, novel, chapters_list,progress,task))
        wait(task_list, return_when="ALL_COMPLETED")
        update_db(None)
        if(len(novel_list)<99):
            console.log(f"本次下载成功{len(novel_list)}本小说")
            for novel in novel_list:
                console.log(novel["novel_name"])

# 获取某章节内容(用于submit)
def get_chapter_content_thread(novel, chapter_list,progress,parent_task):
    novel_content=f"""
小说名:《{novel["novel_name"]}》
作者:   {novel["novel_author"]}
简介:   {novel["intro"]}\n\n
"""
    task=progress.add_task(f"正在保存《{novel['novel_name']}》", total=len(chapter_list))
    for chapter in chapter_list:
        novel_content =novel_content+ get_chapter_content(novel,chapter).strip()+"\n\n"
        progress.update(task, advance=1)
    # save
    path=set_path(f"novel/{novel["novel_name"]}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(novel_content)
    update_db({"novel_id":novel["novel_id"],"file_path": path})
    progress.update(task, visible=False)
    progress.update(parent_task, advance=1)


# 根据novel_id、chapter_id获取章节内容
def get_chapter_content(novel, chapter):
    chapter_content=f"""{chapter["chapter_name"]}
"""
    url = f"https://m.biqugen.net/book/{novel["novel_id"]}/{chapter["chapter_id"]}.html"
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
    soup = BeautifulSoup(res.text, "html.parser")
    contents = soup.find("div", id="nr1").contents
    if contents == None:
        novel["abnormal"] = True
        print(f"获取失败,{url}")
        return
    
    for content in contents:
        if content.name == "center":
            pass
        elif content.name == "br":
            pass
        elif '第' in str(content) and '章' in str(content):
            pass
        elif "-->>" in str(content):
            pass
        else:
            chapter_content=chapter_content+ str(content).replace("\xa0"," ").replace("\n\n"," ")+'\n'
    return  chapter_content

# 初始化文件夹
def init_dir():
    path=set_path("novel")
    if not os.path.exists(path):
        os.makedirs(path)
  
#   更新数据库
def update_db(task:dict|None):
    if(task==None):
        update_novel_download(db_tasks)
        console.log("[green]下载并更新到数据库完成")
        return
    db_tasks.append(task)
    if(len(db_tasks)%6==0):
        update_novel_download(db_tasks)
        db_tasks.clear()

# 扫描本地小说上传至数据库
def scan_local_novels():
    path = set_path("novel")
    novel_list = []
    for root, dirs, files in os.walk(path):
        for file in files:
            novel = {}
            novel["novel_name"] = file.replace(".txt", "")
            novel["file_path"] = os.path.join(root, file)
            novel_list.append(novel)
    
    update_download_wrong(novel_list)


# 根据章节id获取content
def get_content_by_chapter_list(chapter_list):
    with FrameProgress(
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.1f}%",
        MofNCompleteColumn(),
        "[cyan]⏳",
        TimeRemainingColumn(),
    ) as progress, ThreadPoolExecutor(max_workers=6) as executor:
        task = progress.add_task("正在获取章节内容", total=len(chapter_list))
        task_list = []
        for chapter in chapter_list:
            task_list.append(executor.submit(get_content_by_chapter_id, chapter,progress,task))
        wait(task_list, return_when="ALL_COMPLETED")
    

def get_content_by_chapter_id(chapter,progress,task_id):
    chapter_id=chapter["chapter_id"]
    novel_id=chapter["novel_id"]
    url = f"https://m.biqugen.net/book/{novel_id}/{chapter_id}.html"
    res=None
    try:
        res = session.get(url,timeout=5)
    except Exception:
        chapter["abnormal"] = True
        print(f"获取失败,{url}")
        return
    soup = BeautifulSoup(res.text, "html.parser")
    contents = soup.find("div", id="nr1").contents
    if contents == None:
        chapter["abnormal"] = True
        print(f"获取失败,{url}")
        return
    chapter_content=""
    for content in contents:
        if content.name == "center":
            pass
        elif content.name == "br":
            pass
        elif '第' in str(content) and '章' in str(content):
            pass
        elif "-->>" in str(content):
            pass
        else:
            chapter_content=chapter_content+ str(content).replace("\xa0"," ").replace("\n\n"," ")+'\n'
    chapter["content"]=chapter_content
    progress.update(task_id, advance=1)
