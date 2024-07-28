from rich.console import Console
from rich.panel import Panel
from get_list import (
    get_books_list,
    get_books_other_info,
)
from db import (
    get_books_list_from_db,
    get_abnormal_books_list_from_db,
    reset_books_list_to_db,
    save_books_list_to_db,
    update_books_list,
)

console = Console()
# 入口
if __name__ == "__main__":
    # 显示菜单
    menu = Panel(
        """[black]
    * 0. 重置数据库books表
    * 1. 从网站更新所有的小说列表
    * 2. 从网站更新每本小说的详情
        (完本情况、介绍、人气、评分等)
    * 3. 从网站更新[red]异常[black]的小说列表
    * 4. 从数据库获取所有的小说列表
""",
        title="小说爬虫菜单",
    )
    while True:
        # 显示panel
        console.print(menu)
        # 选择功能
        choice = input("请输入功能编号：")
        # 控制台自动输入 1
        # choice = "1"
        match choice:
            case "0":
                reset_books_list_to_db()
            case "1":
                novel_list = get_books_list()
                save_books_list_to_db(novel_list)
            case "2":
                raw_list = get_books_list_from_db()
                novel_list = get_books_other_info(raw_list)
                update_books_list(novel_list)
                pass
            case "3":
                raw_list = get_abnormal_books_list_from_db()
                novel_list = get_books_other_info(raw_list)
                update_books_list(novel_list)
                pass
            case "4":
                raw_list = get_books_list_from_db()
                console.log("🚀 ~ raw_list:", len(raw_list))
                if len(raw_list) != 0:
                    console.log("🚀 ~ raw_list[0]:", raw_list[0])
            case _:
                pass
