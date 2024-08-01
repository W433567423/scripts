from db import get_download_books_list_from_db, get_chapters_list_from_db,update_book_download
from global_config import console,maxThread,session,set_path, FrameProgress
from rich.progress import BarColumn, MofNCompleteColumn, TimeRemainingColumn
from concurrent.futures import ThreadPoolExecutor, as_completed, wait, ALL_COMPLETED
from bs4 import BeautifulSoup
import os


# 保存小说内容
def save_novel_list(novel_list: list):
    with FrameProgress(
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.1f}%",
        MofNCompleteColumn(),
        "[cyan]⏳",
        TimeRemainingColumn(),
    ) as progress, ThreadPoolExecutor(max_workers=8) as executor:
        
        task = progress.add_task("正在保存小说至本地", total=len(novel_list))
        task_list = []
        for novel in novel_list:
            chapters_list = get_chapters_list_from_db(novel["book_id"])
            task_list.append(executor.submit(get_chapter_content_thread, novel, chapters_list,progress,task))

# 获取某章节内容(用于submit)
def get_chapter_content_thread(novel, chapter_list,progress,parent_task):
    book_content=f"""
小说名:《{novel["book_name"]}》
作者:   {novel["book_author"]}
简介:   {novel["intro"]}\n\n
"""
    task=progress.add_task(f"正在保存《{novel['book_name']}》", total=len(chapter_list))
    for chapter in chapter_list:
        book_content =book_content+ get_chapter_content(novel,chapter).strip()+"\n\n"
        progress.update(task, advance=1)
    # save
    path=set_path(f"novel/{novel["book_name"]}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(book_content)
    update_book_download(novel["book_id"],path)
    progress.update(task, visible=False)
    progress.update(parent_task, advance=1)


# 根据book_id、chapter_id获取章节内容
def get_chapter_content(novel, chapter):
    chapter_content=f"""{chapter["chapter_name"]}
"""
    url = f"https://m.biqugen.net/book/{novel["book_id"]}/{chapter["chapter_id"]}.html"
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

def init_dir():
    if not os.path.exists("novel"):
        os.makedirs("novel")
  
