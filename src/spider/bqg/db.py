from global_config import conn, console, chunk_size, FrameProgress
from rich.progress import MofNCompleteColumn, BarColumn, TimeRemainingColumn


# 从数据库获取小说列表
def get_books_list_from_db() -> list:
    global conn
    conn.ping(reconnect=True)
    cursor = conn.cursor()  # 创建游标
    novel_list = []
    novel = {
        "book_name": "",
        "book_link": "",
        "book_author": "",
        "book_publish_time": "",
        "write_status": "",
        "popularity": "",
        "intro": "",
        "abnormal": False,
        "is_extra": False,
    }
    cursor.execute(
        "SELECT book_id,book_name,book_link,book_author,write_status,popularity,intro,file_path,abnormal,is_extra FROM books"
    )
    db_list = cursor.fetchall()
    for item in db_list:
        novel["book_id"] = item[0]
        novel["book_name"] = item[1]
        novel["book_link"] = item[2]
        novel["book_author"] = item[3]
        novel["write_status"] = item[4]
        novel["popularity"] = item[5]
        novel["intro"] = item[6]
        novel["file_path"] = item[7]
        novel["abnormal"] = True if item[8] == 1 else False
        novel["is_extra"] = True if item[9] == 1 else False
        novel_list.append(novel)
    cursor.close()
    return novel_list


# 从数据库获取没有intro等信息的小说列表
def get_no_extra_books_list_from_db() -> list:
    global conn
    conn.ping(reconnect=True)
    cursor = conn.cursor()  # 创建游标
    novel_list = []

    cursor.execute("SELECT book_id FROM books WHERE is_extra=0")
    db_list = cursor.fetchall()
    for item in db_list:
        novel = {
            "book_id": "",
            "abnormal": False,
        }
        novel["book_id"] = item[0]
        novel_list.append(novel)
    cursor.close()
    return novel_list


# 从数据库获取没有章节信息的小说列表
def get_no_chapter_books_list_from_db() -> list:
    global conn
    conn.ping(reconnect=True)
    cursor = conn.cursor()  # 创建游标
    novel_list = []

    cursor.execute(
        "SELECT book_id,book_name FROM books WHERE is_chapter=0 And abnormal=0 ORDER BY book_id ASC"
    )
    db_list = cursor.fetchall()
    for item in db_list:
        novel = {
            "book_id": "",
            "book_name": "",
            "abnormal": False,
        }
        novel["book_id"] = item[0]
        novel["book_name"] = item[1]
        novel_list.append(novel)
    cursor.close()
    return novel_list


# 重置数据库表books
def reset_books_to_db() -> None:
    global conn
    conn.ping(reconnect=True)
    cursor = conn.cursor()  # 创建游标
    # 删除表books
    cursor.execute("DROP TABLE IF EXISTS chapters")
    cursor.execute("DROP TABLE IF EXISTS books")
    # 创建表books，books_id:主键
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS books(
            book_id INT PRIMARY KEY COMMENT '笔趣阁小说id',
            book_name VARCHAR(255) COMMENT '小说名' not null,
            book_author VARCHAR(255) COMMENT '小说作者',
            book_publish_time VARCHAR(255) COMMENT '小说发布时间',
            write_status VARCHAR(255) COMMENT '小说连载状态',
            file_path VARCHAR(255) COMMENT '小说文件路径',
            popularity VARCHAR(255) COMMENT '小说人气',
            intro TEXT COMMENT '小说简介',
            abnormal BOOLEAN DEFAULT FALSE COMMENT '是否异常',
            is_extra BOOLEAN DEFAULT FALSE COMMENT '是否已添加额外信息(连载情况、人气、评分等)',
            is_chapter BOOLEAN DEFAULT FALSE COMMENT '是否已添加章节信息'
        )
    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS chapters(
            chapter_id INT PRIMARY KEY COMMENT '章节id',
            chapter_name VARCHAR(255) COMMENT '章节名' not null,
            chapter_order INT COMMENT '章节顺序',
            book_id INT COMMENT '小说id',
            FOREIGN KEY (book_id) REFERENCES books(book_id)
        )
    """
    )
    conn.commit()
    console.log("数据库表books重置成功")
    cursor.close()


# 重置数据库表chapters
def reset_chapters_to_db() -> None:
    global conn
    conn.ping(reconnect=True)
    cursor = conn.cursor()  # 创建游标
    # 删除表chapters
    cursor.execute("DROP TABLE IF EXISTS chapters")
    # 创建表chapters，chapter_id:主键,book_id:外键
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS chapters(
            chapter_id INT PRIMARY KEY COMMENT '章节id',
            chapter_name VARCHAR(255) COMMENT '章节名' not null,
            chapter_order INT COMMENT '章节顺序',
            book_id INT COMMENT '小说id',
            FOREIGN KEY (book_id) REFERENCES books(book_id)
        )
    """
    )
    # 更新books表is_chapter字段
    cursor.execute("UPDATE books SET is_chapter=False")
    conn.commit()
    console.log("数据库表chapters重置成功")
    cursor.close()


# ---------------------小说---------------------
# 存储小说列表至数据库
def save_books_list_to_db(novel_list: list) -> None:
    console.log("🚀 ~ 正在存储进数据库")
    global conn
    conn.ping(reconnect=True)
    cursor = conn.cursor()  # 创建游标
    # 获取数据库中已有的小说列表(仅获取小说名)
    cursor.execute("SELECT book_id FROM books")
    overed_novel_list = cursor.fetchall()
    # 从元组列表中提取小说id为元组
    overed_novel_list_id = []
    for novel in overed_novel_list:
        overed_novel_list_id.append(novel[0])
    with FrameProgress(
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.1f}%",
        MofNCompleteColumn(),
        "[cyan]⏳",
        TimeRemainingColumn(),
    ) as progress:
        task = progress.add_task("存储小说列表", total=len(novel_list))
        # 将list分每chunk_size条执行一次executemany()方法批量更新数据
        cursor.executemany(
            """
                INSERT INTO books(
                    book_id,
                    book_name,
                    book_author,
                    book_publish_time
                )
                VALUES(
                    %s,
                    %s,
                    %s,
                    %s
                )
            """,
            [
                (
                    novel["book_id"],
                    novel["book_name"],
                    novel["book_author"],
                    novel["book_publish_time"],
                )
                for novel in novel_list
                if novel["book_id"] not in overed_novel_list_id
            ],
        )
        progress.update(task, advance=chunk_size)
    conn.commit()
    cursor.close()
    console.log("小说列表存储成功")


# 更新小说列表到数据库
def update_books_list(list: list) -> None:
    console.log("🚀 ~ 正在更新数据库")
    global conn
    conn.ping(reconnect=True)
    cursor = conn.cursor()  # 创建游标
    # 分类(正常/异常)
    right_list = []
    wrong_list = []
    for novel in list:
        if not novel["abnormal"]:
            right_list.append(novel)
        else:
            wrong_list.append(novel)

    with FrameProgress(
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.1f}%",
        MofNCompleteColumn(),
        "[cyan]⏳",
        TimeRemainingColumn(),
    ) as progress:
        task1 = progress.add_task("更新小说信息", total=len(right_list))
        # for novel in right_list:
        #     try:
        #         cursor.execute(
        #             """
        #                 UPDATE books
        #                 SET
        #                     write_status=%s,
        #                     popularity=%s,
        #                     intro=%s,
        #                     is_extra=%s
        #                 WHERE book_id=%s
        #             """,
        #             (
        #                 novel["write_status"],
        #                 novel["popularity"],
        #                 novel["intro"],
        #                 novel["is_extra"],
        #                 novel["book_id"],
        #             ),
        #         )
        #     except Exception as e:
        #         print(f"[red]异常:{novel}")
        #     progress.update(task1, advance=1)
        for i in range(0, len(right_list), chunk_size):
            cursor.executemany(
                """
                    UPDATE books
                    SET
                        write_status=%s,
                        popularity=%s,
                        intro=%s,
                        is_extra=%s
                    WHERE book_id=%s
                """,
                [
                    (
                        novel["write_status"],
                        novel["popularity"],
                        novel["intro"],
                        novel["is_extra"],
                        novel["book_id"],
                    )
                    for novel in right_list[i : i + chunk_size]
                ],
            )
            progress.update(task1, advance=chunk_size)
        progress.update(task1, completed=len(right_list))
        console.log(f"[red]上报异常,数量:{len(wrong_list)}")
        if len(wrong_list) != 0:
            console.log("🚀 ~ wrong_list:", wrong_list)
            task2 = progress.add_task("更新异常小说", total=len(wrong_list))
            for i in range(0, len(wrong_list), chunk_size):
                cursor.executemany(
                    """
                        UPDATE books
                        SET
                            abnormal=True
                        WHERE book_id=%s
                    """,
                    [(novel["book_id"],) for novel in wrong_list[i : i + chunk_size]],
                )
                progress.update(task2, advance=chunk_size)
            progress.update(task2, completed=len(wrong_list))
    conn.commit()
    cursor.close()
    console.log("小说列表更新成功")


# ---------------------章节---------------------
# 存储章节列表至数据库
def save_chapters_list_to_db(novel_list: list) -> None:
    console.log("🚀 ~ 正在存储进数据库")
    global conn
    conn.ping(reconnect=True)
    cursor = conn.cursor()  # 创建游标
    with FrameProgress(
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.1f}%",
        MofNCompleteColumn(),
        "[cyan]⏳",
        TimeRemainingColumn(),
    ) as progress:
        task = progress.add_task("存储章节列表", total=len(novel_list))
        for novel in novel_list:
            cursor.executemany(
                """
                    INSERT INTO chapters(
                        chapter_id,
                        chapter_name,
                        chapter_order,
                        book_id
                    )
                    VALUES(
                        %s,
                        %s,
                        %s,
                        %s
                    )
                """,
                [
                    (
                        chapter["chapter_id"],
                        chapter["chapter_name"],
                        chapter["chapter_order"],
                        novel["book_id"],
                    )
                    for chapter in novel["chapters_list"]
                ],
            )
            # 更新books表is_chapter字段
            cursor.execute(
                """
                    UPDATE books
                    SET
                        is_chapter=True
                    WHERE book_id=%s
                """,
                (novel["book_id"],),
            )
            progress.update(task, advance=1)
        conn.commit()
        cursor.close()
        console.log("章节列表存储成功")
