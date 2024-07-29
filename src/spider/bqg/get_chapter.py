from global_config import FrameProgress, maxThread, session, console
from bs4 import BeautifulSoup
from rich.progress import MofNCompleteColumn, BarColumn, TimeRemainingColumn
from concurrent.futures import ThreadPoolExecutor, as_completed, wait, ALL_COMPLETED


# 获取小说章节数量
def get_chapters_count(novel: dict):
    url = f"https://www.biqugen.net/book/{novel['book_id']}/"
    res = session.get(url)
    res.encoding = "gbk"
    res.close()
    soup = BeautifulSoup(res.text, "html.parser")
    count = int(
        (soup.find("select", class_="form-control").find_all("option")[-1].text)
        .split("第")[1]
        .split("页")[0]
    )

    return count


# 获取小说章节
# def get_chapters(novel: dict):
#     chapters_list = []
#     chapters_count = get_chapters_count(novel)
#     with FrameProgress(
#         "[progress.description]{task.description}",
#         BarColumn(),
#         "[progress.percentage]{task.percentage:>3.1f}%",
#         MofNCompleteColumn(),
#         "[cyan]⏳",
#         TimeRemainingColumn(),
#     ) as progress, ThreadPoolExecutor(max_workers=maxThread) as executor:
#         task_list = []
#         print("🚀 ~ novel:", novel)

#         task = progress.add_task("获取小说章节", total=chapters_count)

#         for i in range(0, chapters_count):
#             task_list.append(executor.submit(get_chapters_thread, novel, i))
#         for _ in as_completed(task_list):
#             progress.update(task, advance=1)
#         wait(task_list, return_when=ALL_COMPLETED)
#         for thread_task in task_list:
#             chapters_list.extend(thread_task.result())
#         print("🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀" )
#         for i in range(0, len(chapters_list)):
#             chapters_list[i]["chapter_order"] = i + 1
#     return chapters_list


# 获取小说章节(用于submit)
def get_chapters_thread(novel: dict,progress: any) -> list:
    chapter_count = get_chapters_count(novel)
    chapters_list = []
    task = progress.add_task(f"获取《{novel["book_name"]}》章节", total=chapter_count)
    for i in range(0, chapter_count):
        url = f"https://www.biqugen.net/book/{novel['book_id']}/index_{i+1}.html"
        try:
            res = session.get(url)
        except Exception:
            console.log("🚀 ~ 访问失败:", url)
            return []
        res.encoding = "gbk"
        res.close()
        soup = BeautifulSoup(res.text, "html.parser")
        items = soup.find("dl", class_="zjlist").find_all("dd")

        for item in items:
            chapter = {}
            a = item.find("a")
            if a is None:
                continue
            chapter["chapter_name"] = item.find("a").text
            chapter["chapter_id"] = int(item.find("a").attrs["href"].split(".")[0])
            chapters_list.append(chapter)
        progress.update(task, advance=1)
    for i in range(0, len(chapters_list)):
        chapters_list[i]["chapter_order"] = i + 1
    novel["chapters_list"] = chapters_list


# 获取小说章节列表
def get_chapters_list(list: list):
    with FrameProgress(
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.1f}%",
        MofNCompleteColumn(),
        "[cyan]⏳",
        TimeRemainingColumn(),
    ) as progress, ThreadPoolExecutor(max_workers=maxThread) as executor:
        task_list = []
        task = progress.add_task("获取小说章节", total=len(list))
        for novel in list:
            task_list.append(executor.submit(get_chapters_thread, novel, progress))
        for _ in as_completed(task_list):
            progress.update(task, advance=1)
        wait(task_list, return_when=ALL_COMPLETED)
