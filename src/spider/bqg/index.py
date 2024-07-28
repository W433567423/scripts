from rich.panel import Panel
from get_list import (
    get_books_list,
    get_books_other_info,
)
from db import (
    get_books_list_from_db,
    get_no_extra_books_list_from_db,
    reset_books_list_to_db,
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
    * 1. 重置数据库books表
    * 2. 从网站更新所有的小说列表
    * 3. 从网站更新每本小说的详情(简介等)
    * 4. 从数据库获取所有的小说列表
    * 5. 从小说的目录
""",
        title="小说爬虫菜单",
    )
    flag = True
    while flag:
        # 显示panel
        console.print(menu)
        # 选择功能
        choice = input("请输入功能编号：")
        # 控制台自动输入 1
        match choice:
            case "0":
                conn.close()
                flag = False
            case "1":
                reset_books_list_to_db()
            case "2":
                novel_list = get_books_list()
                save_books_list_to_db(novel_list)
            case "3":
                raw_list = get_no_extra_books_list_from_db()
                novel_list = get_books_other_info(raw_list)
                update_books_list(novel_list)
            case "4":
                raw_list = get_books_list_from_db()
                console.log("🚀 ~ len(raw_list):", len(raw_list))
                if len(raw_list) != 0:
                    console.log("🚀 ~ raw_list[0]:", raw_list[0])
            case "5":
                raw_list = get_books_list_from_db()
                console.log("🚀 ~ len(raw_list):", len(raw_list))
            case _:
                pass
