from rich.panel import Panel
from global_config import console
from db import (
    conn,
    get_no_extra_books_list_from_db,
    get_no_chapter_books_list_from_db,
    reset_books_to_db,
    reset_chapters_to_db,
    reset_download_to_db,
    save_books_list_to_db,
    save_chapters_list_to_db,
    update_books_list,
    get_download_books_list_from_db,
)
from get_list import get_books_list, get_books_other_info, get_books_other_info_thread
from get_chapter import (
    get_chapters_list,
)
from save_novel import save_novel_list, init_dir

# 入口
if __name__ == "__main__":
    # 显示菜单
    menu = Panel(
        """[black]
    * 0. 退出
    * 1-1. 重置数据库books表
    * 1-2. 重置数据库chapters表
    * 1-3. 重置数据库download表
    * 2.   从网站更新小说列表
    * 3.   更新小说的详情(简介、连载状态、评分等)
    * 4.   获取小说的目录
    * 5.   保存小说至本地

    * 999. 从数据库获取未获取章节的小说列表
""",
        title="小说爬虫菜单",
        border_style="blue",
        expand=True,
    )
    flag = True
    while flag:
        # 显示panel
        console.print(menu)
        # 选择功能
        choice = input("请输入功能编号：")
        match choice:
            case "0":
                conn.close()
                flag = False
            case "1-1":
                reset_books_to_db()
            case "1-2":
                reset_chapters_to_db()
            case "1-3":
                reset_download_to_db()
            case "2":
                novel_list = get_books_list()
                save_books_list_to_db(novel_list)
            case "3":
                raw_list = get_no_extra_books_list_from_db()
                novel_list = get_books_other_info(raw_list)
                update_books_list(novel_list)
            case "4":
                want = input("请输入要获取的小说数量：")
                raw_list = []
                # 如果输入的是数字
                try:
                    want = int(want)
                    if want < 1:
                        raw_list = get_no_chapter_books_list_from_db()
                    else:
                        raw_list = get_no_chapter_books_list_from_db()[:want]
                    get_chapters_list(raw_list)
                    save_chapters_list_to_db(raw_list)
                except:
                    console.log("[red]异常输入")
                    pass
            case "5":
                init_dir()
                want = input("请输入要获取的小说数量：")
                raw_list = []
                # 如果输入的是数字
                try:
                    want = int(want)
                    if want < 1:
                        raw_list = get_download_books_list_from_db()
                    else:
                        raw_list = get_download_books_list_from_db()[:want]
                    save_novel_list(raw_list)
                except:
                    console.log("[red]异常输入")

            case "999":
                raw_list = get_no_chapter_books_list_from_db()
                console.log("🚀 ~ len(raw_list):", len(raw_list))
                if len(raw_list) > 2:
                    console.log("🚀 ~ raw_list[0]:", raw_list[0])
                    console.log("🚀 ~ raw_list[1]:", raw_list[1])
            case "a":
                novel = {"book_id": 3030}
                get_books_other_info_thread(novel)
                console.log("🚀 ~ novel:", novel)
            case _:
                pass
