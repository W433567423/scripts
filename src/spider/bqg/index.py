from rich.panel import Panel
from get_list import (
    get_books_list,
    get_books_other_info,
)
from db import (
    get_books_list_from_db,
    get_no_extra_books_list_from_db,
    reset_books_to_db,
    reset_chapters_to_db,
    save_books_list_to_db,
    update_books_list,
    conn,
)
from global_config import console

# 入口
if __name__ == "__main__":
    # 显示菜单
    menu = Panel(
        """[black]
    * 0. 退出
    * 1-1. 重置数据库books表
    * 1-2. 重置数据库chapters表
    * 2. 从网站更新小说列表
    * 3. 更新小说的详情(简介、连载状态、评分等)
    * 4. 获取小说的目录

    * 999. 从数据库获取小说列表
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
            case "1-1":
                reset_chapters_to_db()
            case "2":
                novel_list = get_books_list()
                save_books_list_to_db(novel_list)
            case "3":
                raw_list = get_no_extra_books_list_from_db()[5000:]
                novel_list = get_books_other_info(raw_list)
                update_books_list(novel_list)
            case "4":
                raw_list = get_books_list_from_db()
                console.log("🚀 ~ len(raw_list):", len(raw_list))
            case "999":
                raw_list = get_books_list_from_db()
                console.log("🚀 ~ len(raw_list):", len(raw_list))
                if len(raw_list) > 2:
                    console.log("🚀 ~ raw_list[0]:", raw_list[0])
                    console.log("🚀 ~ raw_list[1]:", raw_list[1])
            case _:
                pass
