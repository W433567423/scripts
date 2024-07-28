from global_config import db, FrameProgress
from rich.progress import BarColumn, MofNCompleteColumn, TimeRemainingColumn
from concurrent.futures import ThreadPoolExecutor, as_completed
from global_config import maxThread


# 从数据库获取小说列表
def get_books_list_from_db() -> list:
    global db
    db.connect()  # 连接
    cursor = db.cursor()  # 创建游标
    novel_list = []
    novel = {
        "book_id": 0,
        "book_name": "",
        "book_link": "",
        "book_author": "",
        "book_publish_time": "",
        "write_status": "",
        "popularity": "",
        "intro": "",
        "abnormal": False,
    }
    # 需要获取的值：id,book_id,book_name,book_link,book_author,write_status,popularity,intro,abnormal,file_path
    cursor.execute(
        "SELECT id,book_id,book_name,book_link,book_author,write_status,popularity,intro,abnormal,file_path FROM books"
    )
    db_list = cursor.fetchall()
    for item in db_list:
        novel["id"] = item[0]
        novel["book_id"] = item[1]
        novel["book_name"] = item[2]
        novel["book_link"] = item[3]
        novel["book_author"] = item[4]
        novel["write_status"] = item[5]
        novel["popularity"] = item[6]
        novel["intro"] = item[7]
        novel["abnormal"] = True if item[8] == 1 else False
        novel["file_path"] = item[9]
        novel_list.append(novel)
    cursor.close()
    db.close()
    return novel_list


# 从数据库获取异常的小说列表
def get_abnormal_books_list_from_db() -> list:
    global db
    db.connect()  # 连接
    cursor = db.cursor()  # 创建游标
    novel_list = []
    novel = {
        "book_id": 0,
        "book_name": "",
        "book_link": "",
        "book_author": "",
        "book_publish_time": "",
        "write_status": "",
        "popularity": "",
        "intro": "",
        "abnormal": False,
    }
    # 需要获取的值：id,book_id,book_name,book_link,book_author,write_status,popularity,intro,abnormal,file_path
    cursor.execute(
        "SELECT id,book_id,book_name,book_link,book_author,write_status,popularity,intro,abnormal,file_path FROM books WHERE abnormal=TRUE"
    )
    db_list = cursor.fetchall()
    for item in db_list:
        novel["id"] = item[0]
        novel["book_id"] = item[1]
        novel["book_name"] = item[2]
        novel["book_link"] = item[3]
        novel["book_author"] = item[4]
        novel["write_status"] = item[5]
        novel["popularity"] = item[6]
        novel["intro"] = item[7]
        novel["abnormal"] = True if item[8] == 1 else False
        novel["file_path"] = item[9]
        novel_list.append(novel)
    cursor.close()
    db.close()
    return novel_list


# 重置数据库表books
def reset_books_list_to_db() -> None:
    global db
    db.connect()  # 连接
    cursor = db.cursor()  # 创建游标
    # 删除表books
    cursor.execute("DROP TABLE IF EXISTS books")
    # 创建表books，id:自增主键
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS books(
            id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
            book_id INT COMMENT '笔趣阁小说id' not null,
            book_name VARCHAR(255) COMMENT '小说名' not null,
            book_link VARCHAR(255) COMMENT '小说链接' not null,
            book_author VARCHAR(255) COMMENT '小说作者',
            book_publish_time VARCHAR(255) COMMENT '小说发布时间',
            write_status VARCHAR(255) COMMENT '小说连载状态',
            file_path VARCHAR(255) COMMENT '小说文件路径',
            popularity VARCHAR(255) COMMENT '小说人气',
            intro TEXT COMMENT '小说简介',
            abnormal BOOLEAN DEFAULT FALSE COMMENT '是否异常'
        )
    """
    )
    db.commit()
    print("数据库表books重置成功")
    cursor.close()
    db.close()


# 存储小说列表至数据库
def save_books_list_to_db(novel_list: list) -> None:
    global db
    db.connect()  # 连接
    cursor = db.cursor()  # 创建游标
    # 获取数据库中已有的小说列表(仅获取小说名)
    cursor.execute("SELECT book_name FROM books")
    overed_novel_list = cursor.fetchall()
    # 从元组列表中提取小说名
    overed_novel_list_name = (novel[0] for novel in overed_novel_list)
    with FrameProgress(
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.1f}%",
        MofNCompleteColumn(),
        "[cyan]⏳",
        TimeRemainingColumn(),
    ) as progress:
        task = progress.add_task("小说存入数据库", total=len(novel_list))
        # 将小说列表存入数据库
        for novel in novel_list:
            # 如果数据库中已经存在该小说，则跳过
            if novel["book_name"] not in overed_novel_list_name:
                # 捕获异常
                try:
                    cursor.execute(
                        f"""
                            INSERT INTO books(
                                book_id,
                                book_name,
                                book_link,
                                book_author,
                                book_publish_time,
                                write_status,
                                popularity,
                                intro,
                                abnormal
                            )
                            VALUES(
                                {novel["book_id"]},
                                "{novel["book_name"]}",
                                "{novel["book_link"]}",
                                "{novel["book_author"]}",
                                "{novel["book_publish_time"]}",
                                "{novel["write_status"]}",
                                "{novel["popularity"]}",
                                "{novel["intro"]}",
                                {novel["abnormal"]}
                            )
                        """
                    )
                except Exception as e:
                    print(
                        f"""
                            INSERT INTO books(
                                book_id,
                                book_name,
                                book_link,
                                book_author,
                                book_publish_time,
                                write_status,
                                popularity,
                                intro,
                                abnormal
                            )
                            VALUES(
                                {novel["book_id"]},
                                "{novel["book_name"]}",
                                "{novel["book_link"]}",
                                "{novel["book_author"]}",
                                "{novel["book_publish_time"]}",
                                "{novel["write_status"]}",
                                "{novel["popularity"]}",
                                "{novel["intro"]}",
                                {novel["abnormal"]}
                            )
                        """
                    )
            progress.update(task, advance=1)
    db.commit()
    cursor.close()
    db.close()
    print("小说列表存储成功")


# 更新小说列表到数据库
def update_books_list(list: list) -> None:
    global db
    db.connect()  # 连接
    cursor = db.cursor()  # 创建游标
    with FrameProgress(
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.1f}%",
        MofNCompleteColumn(),
        "[cyan]⏳",
        TimeRemainingColumn(),
    ) as progress:
        task = progress.add_task("更新小说列表", total=len(list))
        for novel in list:
            # 捕获异常
            try:
                cursor.execute(
                    f"""
                        UPDATE books
                        SET
                            book_id={novel["book_id"]},
                            book_name="{novel["book_name"]}",
                            book_link="{novel["book_link"]}",
                            book_author="{novel["book_author"]}",
                            book_publish_time="{novel["book_publish_time"]}",
                            write_status="{novel["write_status"]}",
                            popularity="{novel["popularity"]}",
                            intro="{novel["intro"]}",
                            abnormal={novel["abnormal"]}
                        WHERE id={novel["id"]}
                    """
                )
            except Exception as e:
                print(
                    f"""
                        UPDATE books
                        SET
                            book_id={novel["book_id"]},
                            book_name="{novel["book_name"]}",
                            book_link="{novel["book_link"]}",
                            book_author="{novel["book_author"]}",
                            book_publish_time="{novel["book_publish_time"]}",
                            write_status="{novel["write_status"]}",
                            popularity="{novel["popularity"]}",
                            intro="{novel["intro"]}",
                            abnormal={novel["abnormal"]}
                        WHERE id={novel["id"]}
                    """
                )
            progress.update(task, advance=1)
    db.commit()
    cursor.close()
    db.close()
    print("小说列表更新成功")
