import requests
from bs4 import BeautifulSoup
import os
import time
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from utils import (
    readErrorFile,
    get_all_files,
    filterBook,
    trim,
    save_books_list,
    load_local_list,
    get_e_files
)

# 全局变量
domainUrl = "https://h.yanqingzhan.net"  # 网站域名
keys = []  # 小说名列表
errorList = []  # 异常小说列表
rootDir = "books"  # 保存小说的根目录
session = requests.session()  # 创建会话
downloadNum=1  # 下载小说数量
maxThread = None  # 最大线程数
headers = {
    "Cookie": "PHPSESSID=8rre64qkin0t800l57ghoqk9b7; __51vcke__KRByPb0JAadZd4QS=8c7edfec-3106-5177-b5d7-4085d67d07fd; __51vuft__KRByPb0JAadZd4QS=1720424949691; rc=1; mlight=0; _ga=GA1.1.2115602680.1720424950; _ga_3WN83DRK1K=GS1.1.1720424980.1.1.1720425053.0.0.0; sid=wrJZEWgIpE2ExrZgHiIjcpaepC8nHPcg; uid=97595; rcapter=236452=47999494; __51uvsct__KRByPb0JAadZd4QS=6; __vtins__KRByPb0JAadZd4QS=%7B%22sid%22%3A%20%22ed3bc196-e5ed-5a0e-a494-eb522ae50a79%22%2C%20%22vd%22%3A%205%2C%20%22stt%22%3A%2015336%2C%20%22dr%22%3A%203140%2C%20%22expires%22%3A%201720495952730%2C%20%22ct%22%3A%201720494152730%7D; _ga_7PGFBLF0BP=GS1.1.1720494137.5.1.1720494157.0.0.0"
}  # 请求头
categorys = [
    "古代言情",
    "都市言情",
    "穿越时空",
    "浪漫幻想",
    "婚姻职场",
    "奇幻玄幻",
    "武侠仙侠",
    "恐怖灵异",
    "历史军事",
    "游戏科幻",
    "都市小说",
    "青春校园",
    "千千心结",
    "素锦年华",
    "同人小说",
    "其他类别",
]  # 小说类别


# 获取小说列表
def getBookList(category, page):
    books = []
    url = f"{domainUrl}/sort/{category}/3/{page}.html"
    res = session.get(url, headers=headers)
    res.encoding = "utf-8"
    soup = BeautifulSoup(res.text, "html.parser")
    if soup.find("div", id="bookList") == None:
        print(f"\033[1;31m该页目录异常!网址:{url}\033[0m")
        return []
    items = soup.find("div", id="bookList").find_all("h2")
    for item in items:
        if trim(item.find("a").string) in keys:
            continue
        else:
            keys.append(trim(item.find("a").string))
        book = {}
        book["bookid"] = item.find("a").attrs["href"].split("/")[-2]
        book["bookname"] = trim(item.find("a").string)
        book["authorname"] = trim(item.find("span").find("a").string)
        book["categoryname"] = categorys[category - 1]
        books.append(book)
    return books


# 获取完本小说列表
def get_final_books_list():
    books = []
    # 循环获取16类小说
    # 1:古代言情 2:都市言情 3:穿越时空 4:浪漫幻想 5:婚姻职场 6:奇幻玄幻 7:武侠仙侠 8:恐怖灵异 9:历史军事 10:游戏科幻 11:都市小说 12:青春校园 13:千千心结 14:素锦年华 15:同人小说 16:其他类别
    taskList = []
    length = 0
    with ThreadPoolExecutor(maxThread) as executor:
        for category in range(1, 17):
            # 获取页数总和
            url1 = f"{domainUrl}/sort/{category}/3/1.html"
            res1 = session.get(url1, headers=headers)
            res1.encoding = "utf-8"
            soup = BeautifulSoup(res1.text, "html.parser")
            pageNum = int(
                soup.find("span", class_="pagebox")
                .find("em")
                .next_element.text.split("/")[1]
                .split("页")[0]
            )
            for page in range(1, pageNum):
                # 创建并启动线程
                taskList.append(executor.submit(getBookList, category, page))
            wait(taskList, return_when=ALL_COMPLETED)
            for task in taskList:
                books.extend(task.result())
            taskList.clear()
            length = len(books) - length
            print(f"{categorys[category-1]} 类已获取{length}本小说")
    print(f"共获取小说{len(books)}本")
    return books


# 获取一本书所有章节信息
def get_books_chapter(domainUrl, bookInfo):
    chapters = []
    nextFlag = True
    i = 1
    while nextFlag:
        url = f"{domainUrl}/book/{bookInfo['bookid']}/0/{i}.html"
        # print(url)
        res = session.get(url, headers=headers)
        res.encoding = "utf-8"
        soup = BeautifulSoup(res.text, "html.parser")
        items = soup.find("div", id="chapterlist").find_all("a")
        for item in items:
            chapterTitle = trim(item.string)
            chapterId = item["href"].split("/")[-1].split(".")[0]
            chapters.append(
                {
                    "title": chapterTitle,
                    "id": chapterId,
                    "crypto_id": get_page_crypto_id(bookInfo, chapterTitle, chapterId),
                }
            )
        i += 1

        nextButton = (
            soup.find("div", class_="pagebtn")
            .find("div", class_="pagerightbtn")
            .find("a")
            .attrs["href"]
        )
        if nextButton == "javascript:void(0);":
            nextFlag = False
        pass
    return chapters


# 获取小说章节的加密id
def get_page_crypto_id(bookInfo, chapterTitle, chapterId):
    url = f"{domainUrl}/book/{bookInfo['bookid']}/{chapterId}.html"
    # print(chapterTitle)
    res = session.get(url, headers=headers)
    res.encoding = "utf-8"
    soup = BeautifulSoup(res.text, "html.parser")
    # 判断异常小说
    contentItem = (
        soup.find("div", class_="readMain")
        .find("div", class_="chapter")
        .find("div")
        .text
    )
    if trim(contentItem) == "章节内容显示异常！":
        return 0
    scripts = soup.find_all("script")
    for script in scripts:
        if script.text.find("___ChapterPageUrl") != -1:
            crypto_id = script.text.split("___ChapterPageUrl|book|")[1].split("=")[0]
            return crypto_id


# 获取每个章节的小说内容
def get_page_content(bookInfo, chapter, index):
    nextFlag = True
    i = 1
    if "第" in chapter["title"]:
        content = chapter["title"] + "\n"
    else:
        content = f"第{index}章 {chapter['title']}\n"
    # print(
    #     f"\033[1;32m---获取《{bookInfo['bookname']}》 {chapter['title']} ~的内容...---\033[0m\n"
    # )
    while nextFlag:
        # print(f"正在获取第{i}/∞页",end="\r")
        url = f"{domainUrl}/book/{bookInfo['bookid']}/{chapter['crypto_id']}.html?page={i}"
        res = session.get(url, headers=headers)
        res.encoding = "utf-8"
        soup = BeautifulSoup(res.text, "html.parser")
        contentItem = (
            soup.find("div", class_="readMain")
            .find("div", class_="chapter")
            .find("div")
            .text
        ).strip("\n")
        content += contentItem
        i += 1
        # 判断是否完结
        nextButton = soup.find("a", id="btnNext").attrs["href"]
        if not "javascript" in nextButton:
            content.replace('\n\n','')
            content += "\n\n\n\n" # 分节符
            nextFlag = False
    return content


# 下载小说
def downloadBook(rootDir, book):
    global downloadNum
    global errorList
    print(f"\033[1;36m---开始下载小说《{book['bookname']}》...---\033[0m")
    flag = True
    filepath = os.path.join(rootDir, book["categoryname"], f"《{book["bookname"]}》.txt")
    bookContent = f"小说名:《{book['bookname']}》\n作者:{book['authorname']}\n小说id:{book['bookid']}\n完结\n\n\n\n"

    # DONE 获取章节信息
    # print(f"\033[1;32m---获取小说《{book['bookname']}》目录...---\033[0m\n")
    chapters = get_books_chapter(domainUrl, book)
    # print(f"《{book['bookname']}》共{len(chapters)}章")
    # DONE 获取小说内容
    # print(f"\033[1;32m---开始获取小说内容...---\033[0m\n")
    i = 0
    for chapter in chapters:
        if flag:
            # 跳过异常章节
            if chapter["crypto_id"] == 0:
                flag = False
                continue
            bookContent+=get_page_content(book, chapter, chapters.index(chapter) + 1)
            i += 1
    if flag:
        try :
            print(f"\033[1;32m第{downloadNum}本 {book["bookname"]},共{i}章{len(bookContent)}字。\033[0m")
            f=open(filepath, "w", encoding="utf-8")
            f.write(bookContent)
            f.close()
            downloadNum+=1
        except Exception as e:
            print(f"\033[1;31m《{book['bookname']}》保存失败！\033[0m",e)
    else:
        print(f"\033[1;31m《{book['bookname']}》下载失败！\033[0m")
        errorList.append(book)
    i = 0


def main():
    global errorList 
    global novelList 
    novelList= []
    start = time.time()
    # DONE 创建文件夹books

    dirArr=['books']
    for category in categorys:
        dirArr.append(f"books/{category}")
    for dir in dirArr:
        if not os.path.exists(dir):
            # print(f"\033[1;32m---开始创建文件夹{dir}...---\033[0m\n")
            os.makedirs(dir)
    # DONE 读取错误文件
    errorList= readErrorFile()
    # DONE 读取已下载的小说列表
    overList = get_all_files(rootDir)

    # DONE 下载完本小说
    print(f"\033[1;32m---开始获取所有完本小说列表...---\033[0m\n")
    novelList = load_local_list()
    # novelList = get_final_books_list()
    print(
        f"已下载:{len(overList)},所有列表:{len(novelList)},异常列表:{len(get_e_files(rootDir))}",
    )
    realBookList = filterBook(errorList, overList, novelList)
    save_books_list(realBookList)
    # exit()
    # realBookList分割每个小说为一组
    b = [realBookList[i:i+100] for i in range(0, len(realBookList), 100)]
    for temp in b:
        print(f"\033[1;32m---开始下载{len(temp)}本小说...---\033[0m\n")
        taskList = []
        with ThreadPoolExecutor(maxThread) as executor:  # 创建线程池
            for i in temp:
                # 创建并启动线程
                taskList.append(
                    executor.submit(
                        downloadBook,
                        rootDir,
                        i
                    )
                )
        wait(taskList, return_when=ALL_COMPLETED)
        taskList.clear()
        # DONE 保存错误文件
        if len(errorList) > 0:
            print(f"\033[1;31m---开始保存错误文件{len(errorList)}本...---\033[0m\n")
            with open("errorList.txt", "w", encoding="utf-8") as f:
                for book in errorList:
                    f.write(f"{book['bookid']} {book['bookname']} {book['authorname']} {book['categoryname']}\n")
            f.close()
    print(f"\033[1;32m---全部小说内容保存完毕！---\033[0m\n")
    stop = time.time()
    # 输出用时 时分秒
    m, s = divmod(stop - start, 60)
    h, m = divmod(m, 60)
    print(f"\033[1;32m---用时{int(h)}小时{int(m)}分{int(s)}秒---\033[0m\n")


# 入口
if __name__ == "__main__":
    main()
