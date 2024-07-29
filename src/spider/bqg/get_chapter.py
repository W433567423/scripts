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
def get_chapters(novel: dict):
    chapters_list = []
    count = get_chapters_count(novel)
    with FrameProgress(
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.1f}%",
        MofNCompleteColumn(),
        "[cyan]⏳",
        TimeRemainingColumn(),
    ) as progress, ThreadPoolExecutor(max_workers=maxThread) as executor:
        task_list = []
        task = progress.add_task("获取小说章节", total=count)
        for i in range(0, count):
            task_list.append(executor.submit(get_chapters_thread, novel, i))
        for _ in as_completed(task_list):
            progress.update(task, advance=1)
        wait(task_list, return_when=ALL_COMPLETED)
        for thread_task in task_list:
            chapters_list.extend(thread_task.result())
    return chapters_list


# 获取小说章节(用于submit)
def get_chapters_thread(novel: dict, i: int) -> list:
    chapters_list = []
    url = f"https://www.biqugen.net/book/{novel['book_id']}/index_{i+1}.html"
    try:
        res = session.get(url)
    except Exception:
        console.log("🚀 ~ 访问失败:", url)
        return chapters_list

    res.encoding = "gbk"
    res.close()
    soup = BeautifulSoup(res.text, "html.parser")
    items = soup.find("dl", class_="zjlist").find_all("dd")

    for item in items:
        chapter = {}
        a = item.find("a")
        if a is None:
            continue
        chapter["title"] = item.find("a").text
        chapter["url"] = item.find("a").attrs["href"]
        chapters_list.append(chapter)
    return chapters_list
