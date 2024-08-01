from utils import conn, set_path, console, chunk_size, FrameProgress
from rich.progress import MofNCompleteColumn, BarColumn, TimeRemainingColumn
import time, os


# 从数据库获取小说列表
def get_books_list_from_db() -> list:
    global conn
    conn.ping(reconnect=True)
    cursor = conn.cursor()  # 创建游标
    novel_list = []
    cursor.execute(
        "SELECT book_id,book_name,book_link,book_author,write_status,popularity,intro,file_path,abnormal,is_extra FROM books"
    )
    db_list = cursor.fetchall()
    for item in db_list:
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

    cursor.execute(
        "SELECT book_id FROM books WHERE is_extra=False ORDER BY book_id ASC"
    )
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


# 获取待下载的小说列表
def get_download_books_list_from_db() -> list:
    global conn
    conn.ping(reconnect=True)
    cursor = conn.cursor()  # 创建游标
    novel_list = []
    # where file_path is null and is_chapter is true
    cursor.execute(
        "SELECT book_id,book_name,intro,book_author FROM books WHERE file_path IS NULL AND is_chapter=True"
    )
    db_list = cursor.fetchall()
    for item in db_list:
        novel = {
            "book_id": "",
            "book_name": "",
            "file_path": "",
        }
        novel["book_id"] = item[0]
        novel["book_name"] = item[1]
        novel["intro"] = item[2]
        novel["book_author"] = item[3]
        novel["file_path"] = None
        novel_list.append(novel)
    cursor.close()
    return novel_list


# 获取小说章节列表
def get_chapters_list_from_db(book_id: int) -> list:
    global conn
    conn.ping(reconnect=True)
    cursor = conn.cursor()  # 创建游标
    chapters_list = []
    cursor.execute(
        "SELECT chapter_id,chapter_name,chapter_order FROM chapters WHERE book_id=%s ORDER BY chapter_order ASC",
        (book_id,),
    )
    db_list = cursor.fetchall()
    for item in db_list:
        chapter = {
            "chapter_id": "",
            "chapter_name": "",
            "chapter_order": "",
        }
        chapter["chapter_id"] = item[0]
        chapter["chapter_name"] = item[1]
        chapter["chapter_order"] = item[2]
        chapters_list.append(chapter)
    cursor.close()
    return chapters_list


# 获取已下载完成的小说列表
def get_download_overed_books_list_from_db() -> list:
    global conn
    conn.ping(reconnect=True)
    cursor = conn.cursor()  # 创建游标
    novel_list = []
    cursor.execute("SELECT book_name FROM books WHERE file_path IS NOT NULL")
    db_list = cursor.fetchall()
    for item in db_list:
        novel_list.append(item[0])
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
            book_cover VARCHAR(255) COMMENT '小说封面',
            book_author VARCHAR(255) COMMENT '小说作者',
            book_category VARCHAR(255) COMMENT '小说分类',
            write_status VARCHAR(255) COMMENT '小说连载状态',
            publish_time VARCHAR(255) COMMENT '小说发布时间',
            intro TEXT COMMENT '小说简介',
            is_extra BOOLEAN DEFAULT FALSE COMMENT '是否已添加额外信息(连载情况、人气、评分等)',
            is_chapter BOOLEAN DEFAULT FALSE COMMENT '是否已添加章节信息',
            abnormal BOOLEAN DEFAULT FALSE COMMENT '是否异常',
            file_path VARCHAR(255) COMMENT '小说文件路径'
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
    console.log("[green]数据库表books重置成功")
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
    console.log("[green]数据库表chapters重置成功")
    cursor.close()


# 重置下载
def reset_download_to_db() -> None:
    global conn
    conn.ping(reconnect=True)
    # 删除path目录下所有文件
    path = set_path("novel")
    if os.path.exists(path):
        for file in os.listdir(path):
            os.remove(os.path.join(path, file))
    cursor = conn.cursor()
    cursor.execute("UPDATE books SET file_path=Null")
    conn.commit()
    console.log("[green]下载的文件已全部删除,下载重置成功")
    cursor.close()


# ---------------------小说---------------------
# 存储小说列表至数据库
def save_books_list_to_db(novel_list: list) -> None:
    if len(novel_list) == 0:
        return
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
                    book_name
                )
                VALUES(
                    %s,
                    %s
                )
            """,
            [
                (
                    novel["book_id"],
                    novel["book_name"],
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
    if len(list) == 0:
        console.log("[red]列表为空")
        return
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

        for i in range(0, len(right_list), chunk_size):
            cursor.executemany(
                """
                    UPDATE books
                    SET
                        book_cover=%s,
                        book_author=%s,
                        book_category=%s,
                        write_status=%s,
                        publish_time=%s,
                        intro=%s,
                        is_extra=True
                    WHERE book_id=%s
                """,
                [
                    (
                        novel["book_cover"],
                        novel["book_author"],
                        novel["book_category"],
                        novel["write_status"],
                        novel["publish_time"],
                        novel["intro"],
                        novel["book_id"],
                    )
                    for novel in right_list[i : i + chunk_size]
                ],
            )
            progress.update(task1, advance=chunk_size)
        progress.update(task1, completed=len(right_list))
        if len(wrong_list) != 0:
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
    if len(novel_list) == 0:
        console.log("[red]列表为空")
        return
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
            try:
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
            except Exception as e:
                # 写入log文件
                with open(
                    set_path(
                        f"log-{time.strftime('%Y-%m-%d',time.localtime(time.time()))}.txt"
                    ),
                    "a",
                    encoding="utf-8",
                ) as f:
                    # 写入时间、id、书名、错误信息
                    f.write(
                        f"{time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))} {novel['book_id']} {novel['book_name']} {e}\n"
                    )
                    # 如果有章节信息,写入前三节章节信息
                    if novel.get("chapters_list") and len(novel["chapters_list"]) != 0:
                        f.write(
                            f"{novel['chapters_list'][0]}\n{novel['chapters_list'][1]}\n{novel['chapters_list'][2]}\n\n"
                        )

            progress.update(task, advance=1)
        progress.update(task, completed=len(novel_list))
        conn.commit()
        cursor.close()
        console.log("章节列表存储成功")


# 更新小说下载地址
def update_book_download(novel_list: list) -> None:
    global conn
    conn.ping(reconnect=True)
    cursor = conn.cursor()  # 创建游标
    cursor.executemany(
        """
            UPDATE books
            SET
                file_path=%s
            WHERE book_id=%s
        """,
        [(item["book_id"], item["file_path"]) for item in novel_list],
    )
    # 当前时间
    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    print(f"{now_time} 更新了{len(novel_list)}条数据")
    conn.commit()
    cursor.close()


# 更新下载并更新到数据库
def update_download_wrong(novel_list: list) -> None:
    global conn
    conn.ping(reconnect=True)
    cursor = conn.cursor()  # 创建游标
    remote_list = get_download_overed_books_list_from_db()
    console.log(f"[green]获取数据库已下载成功数量:{len(remote_list)}")

    if len(novel_list) == len(remote_list):
        console.log("[green]无需上传")
        return

    # 剔除已下载的小说
    ready_arr = []
    for novel in novel_list:
        if novel["book_name"] not in remote_list:
            ready_arr.append(novel)

    with FrameProgress(
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.1f}%",
        MofNCompleteColumn(),
        "[cyan]⏳",
        TimeRemainingColumn(),
    ) as progress:
        task = progress.add_task("将本地小说更新到数据库", total=len(ready_arr))
        for novel in ready_arr:
            cursor.execute(
                "UPDATE books SET file_path=%s WHERE book_id=%s",
                (novel["file_path"], novel["book_id"]),
            )
            progress.update(task, advance=1)

    conn.commit()
    cursor.close()
    console.log("[green]本地小说更新到数据库完成")
