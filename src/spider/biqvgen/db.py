from utils import conn, set_path, console, chunk_size, get_now_time,FrameProgress
from rich.progress import MofNCompleteColumn, BarColumn, TimeRemainingColumn
import time, os


# 从数据库获取小说列表
def get_books_list_from_db() -> list:
    global conn
    conn.ping(reconnect=True)
    cursor = conn.cursor()  # 创建游标
    novel_list = []
    cursor.execute(
        "SELECT novel_id,novel_name,novel_link,novel_author,write_status,popularity,intro,file_path,abnormal,is_extra FROM novels"
    )
    db_list = cursor.fetchall()
    for item in db_list:
        novel = {
            "novel_name": "",
            "novel_link": "",
            "novel_author": "",
            "novel_publish_time": "",
            "write_status": "",
            "popularity": "",
            "intro": "",
            "abnormal": False,
            "is_extra": False,
        }
        novel["novel_id"] = item[0]
        novel["novel_name"] = item[1]
        novel["novel_link"] = item[2]
        novel["novel_author"] = item[3]
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
        "SELECT novel_id FROM novels WHERE is_extra=False ORDER BY novel_id ASC"
    )
    db_list = cursor.fetchall()
    for item in db_list:
        novel = {
            "novel_id": "",
            "abnormal": False,
        }
        novel["novel_id"] = item[0]
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
        "SELECT novel_id,novel_name FROM novels WHERE is_chapter=0 And abnormal=0 ORDER BY novel_id ASC"
    )
    db_list = cursor.fetchall()
    for item in db_list:
        novel = {
            "novel_id": "",
            "novel_name": "",
            "abnormal": False,
        }
        novel["novel_id"] = item[0]
        novel["novel_name"] = item[1]
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
        "SELECT novel_id,novel_name,intro,novel_author FROM novels WHERE file_path IS NULL AND is_chapter=True"
    )
    db_list = cursor.fetchall()
    for item in db_list:
        novel = {
            "novel_id": "",
            "novel_name": "",
            "file_path": "",
        }
        novel["novel_id"] = item[0]
        novel["novel_name"] = item[1]
        novel["intro"] = item[2]
        novel["novel_author"] = item[3]
        novel["file_path"] = None
        novel_list.append(novel)
    cursor.close()
    return novel_list


# 获取小说章节列表
def get_chapters_list_from_db(novel_id: int) -> list:
    global conn
    conn.ping(reconnect=True)
    cursor = conn.cursor()  # 创建游标
    chapters_list = []
    cursor.execute(
        "SELECT chapter_id,chapter_name,chapter_order FROM chapters WHERE novel_id=%s ORDER BY chapter_order ASC",
        (novel_id,),
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
    cursor.execute("SELECT novel_name FROM novels WHERE file_path IS NOT NULL")
    db_list = cursor.fetchall()
    for item in db_list:
        novel_list.append(item[0])
    cursor.close()
    return novel_list


# 获取content为空的章节列表
def get_empty_content_chapters_list_from_db(limit=None) -> list:
    global conn
    conn.ping(reconnect=True)
    cursor = conn.cursor()  # 创建游标
    chapters_list = []
    sql = "SELECT chapter_id,chapter_name,novel_id FROM chapters WHERE content IS NULL ORDER BY chapter_id ASC"
    if(limit):
        sql += f" LIMIT {limit}"
    cursor.execute(sql
    )


    db_list = cursor.fetchall()
    for item in db_list:
        chapter = {
            "chapter_id": "",
            "chapter_name": "",
            "novel_id": "",
            "content": "",
            "abnormal": False,
        }
        chapter["chapter_id"] = item[0]
        chapter["chapter_name"] = item[1]
        chapter["novel_id"] = item[2]
        chapters_list.append(chapter)
    cursor.close()
    return chapters_list

#  获取content为空的章节数量
def get_empty_content_count_from_db()->list:
    global conn
    conn.ping(reconnect=True)
    cursor = conn.cursor()  # 创建游标
    cursor.execute("SELECT COUNT(*) FROM chapters WHERE content IS NULL")
    count = cursor.fetchall()[0][0]
    cursor.close()
    return count

# 重置数据库表books
def reset_books_to_db() -> None:
    global conn
    conn.ping(reconnect=True)
    cursor = conn.cursor()  # 创建游标
    # 删除表novels
    cursor.execute("DROP TABLE IF EXISTS chapters")
    cursor.execute("DROP TABLE IF EXISTS novels")
    # 创建表novels，novel_id:主键
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS novels(
            novel_id INT PRIMARY KEY COMMENT '笔趣阁小说id',
            novel_name VARCHAR(255) COMMENT '小说名' not null,
            novel_cover VARCHAR(255) COMMENT '小说封面',
            novel_author VARCHAR(255) COMMENT '小说作者',
            novel_category VARCHAR(255) COMMENT '小说分类',
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
            novel_id INT COMMENT '小说id',
            content TEXT COMMENT '章节内容',
            FOREIGN KEY (novel_id) REFERENCES novels(novel_id)
        )
    """
    )
    conn.commit()
    console.log("[green]数据库表novels重置成功")
    cursor.close()


# 重置数据库表chapters
def reset_chapters_to_db() -> None:
    global conn
    conn.ping(reconnect=True)
    cursor = conn.cursor()  # 创建游标
    # 删除表chapters
    cursor.execute("DROP TABLE IF EXISTS chapters")
    # 创建表chapters，chapter_id:主键,novel_id:外键
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS chapters(
            chapter_id INT PRIMARY KEY COMMENT '章节id',
            chapter_name VARCHAR(255) COMMENT '章节名' not null,
            chapter_order INT COMMENT '章节顺序',
            novel_id INT COMMENT '小说id',
            content TEXT COMMENT '章节内容',
            FOREIGN KEY (novel_id) REFERENCES novels(novel_id)
        )
    """
    )
    # 更新novels表is_chapter字段
    cursor.execute("UPDATE novels SET is_chapter=False")
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
    cursor.execute("UPDATE novels SET file_path=Null")
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
    cursor.execute("SELECT novel_id FROM novels")
    overed_novel_list = cursor.fetchall()
    # 从元组列表中提取小说id为元组
    overed_novel_list_id = []
    for novel in overed_novel_list:
        overed_novel_list_id.append(novel[0])

    cursor.executemany(
        """
            INSERT INTO novels(
                novel_id,
                novel_name
            )
            VALUES(
                %s,
                %s
            )
        """,
        [
            (
                novel["novel_id"],
                novel["novel_name"],
            )
            for novel in novel_list
            if novel["novel_id"] not in overed_novel_list_id
        ],
    )
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
                    UPDATE novels
                    SET
                        novel_cover=%s,
                        novel_author=%s,
                        novel_category=%s,
                        write_status=%s,
                        publish_time=%s,
                        intro=%s,
                        is_extra=True
                    WHERE novel_id=%s
                """,
                [
                    (
                        novel["novel_cover"],
                        novel["novel_author"],
                        novel["novel_category"],
                        novel["write_status"],
                        novel["publish_time"],
                        novel["intro"],
                        novel["novel_id"],
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
                        UPDATE novels
                        SET
                            abnormal=True
                        WHERE novel_id=%s
                    """,
                    [(novel["novel_id"],) for novel in wrong_list[i : i + chunk_size]],
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
                        novel_id
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
                            novel["novel_id"],
                        )
                        for chapter in novel["chapters_list"]
                    ],
                )
                # 更新books表is_chapter字段
                cursor.execute(
                    """
                        UPDATE novels
                        SET
                            is_chapter=True
                        WHERE novel_id=%s
                    """,
                    (novel["novel_id"],),
                )
            except Exception as e:
                # 写入log文件
                with open(
                    set_path(
                        f"log-{get_now_time()}.txt"
                    ),
                    "a",
                    encoding="utf-8",
                ) as f:
                    # 写入时间、id、书名、错误信息
                    f.write(
                        f"{get_now_time()} {novel['novel_id']} {novel['novel_name']} {e}\n"
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
def update_novel_download(novel_list: list) -> None:
    global conn
    conn.ping(reconnect=True)
    cursor = conn.cursor()  # 创建游标
    for novel in novel_list:
        try:
            cursor.execute(
                "UPDATE novels SET file_path=%s WHERE novel_id=%s",
                (novel["file_path"], novel["novel_id"]),
            )
        except Exception:
            # 写入日志
            with open(
                set_path(
                    f"log-{get_now_time()}.txt"
                ),
                "a",
                encoding="utf-8",
            ) as f:
                f.write(f"{get_now_time()} {novel['novel_id']} UPDATE novels SET file_path=%s WHERE novel_id=%s,{
                (novel["file_path"], novel["novel_id"])}\n"
                )
          
    # 当前时间
    now_time = get_now_time()
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
        if novel["novel_name"] not in remote_list:
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
                "UPDATE novels SET file_path=%s WHERE novel_name=%s",
                (novel["file_path"], novel["novel_name"]),
            )
            progress.update(task, advance=1)

    conn.commit()
    cursor.close()
    console.log("[green]本地小说更新到数据库完成")


# 更新数据库
def save_chapters_content_to_db(chapter_list)->None:
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
        task = progress.add_task("存储章节内容", total=len(chapter_list))
        for chapter in chapter_list:
            try:
                cursor.execute(
                    "UPDATE chapters SET content=%s WHERE chapter_id=%s",
                    (chapter["content"], chapter["chapter_id"]),
                )
            except Exception as e:
                # 写入log文件
                with open(
                    set_path(
                        f"log-{get_now_time()}.txt"
                    ),
                    "a",
                    encoding="utf-8",
                ) as f:
                    # 写入时间、id、书名、错误信息
                    f.write(
                        f"{get_now_time()} {chapter['chapter_id']} {chapter['chapter_name']} {e}\n"
                    )
            progress.update(task, advance=1)
        conn.commit()
        cursor.close()
