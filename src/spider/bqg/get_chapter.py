from global_config import FrameProgress, maxThread, session, console
from bs4 import BeautifulSoup
from rich.progress import MofNCompleteColumn, BarColumn, TimeRemainingColumn
from concurrent.futures import ThreadPoolExecutor, as_completed, wait, ALL_COMPLETED


# 获取小说章节数量
def get_chapters_count(novel: dict):
    url = f"https://www.biqugen.net/book/{novel['book_id']}/"
    res = session.get(url,timeout=5)
    res.encoding = "gbk"
    res.close()
    soup = BeautifulSoup(res.text, "html.parser")
    form_control=soup.find("select", class_="form-control")
    if form_control==None:
        return 1
    count = int(
        form_control.find_all("option")[-1].text
        .split("第")[1]
        .split("页")[0]
    )

    return count


# 获取小说章节(用于submit)
def get_chapters_thread(novel: dict,progress: any) -> list:
    chapter_count = get_chapters_count(novel)
    chapters_list = []
    task = progress.add_task(f"《{novel["book_name"]}》", total=chapter_count)
    for i in range(0, chapter_count):
        if novel.get("abnormal"):
            break
        url = f"https://www.biqugen.net/book/{novel['book_id']}/index_{i+1}.html"
        try:
            res = session.get(url,timeout=5)
        except Exception:
            novel["abnormal"] = True
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
    progress.update(task, visible=False)

    for i in range(0, len(chapters_list)):
        chapters_list[i]["chapter_order"] = i + 1
    novel["chapters_list"] = chapters_list
    novel["abnormal"] = False


# 获取小说章节列表
def get_chapters_list(list: list) -> None:
    if len(list) == 0:
        return 
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
    # 提取出异常的小说列表返回
    wrong_list = [novel for novel in list if novel.get("abnormal")]
    if len(wrong_list) > 0:
        console.log(f"[red]有异常列表，正在递归重复获取{len(wrong_list)}")
    
    return get_chapters_list(wrong_list)
