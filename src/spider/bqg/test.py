from bs4 import BeautifulSoup
from global_config import session, db, FrameProgress, maxThread
from get_chapter import get_chapters


# 1-5.重置数据库表books
def reset_books_list_to_db():
    global db
    db.connect()
    cursor = db.cursor()
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


# 2.从数据库中获取所有小说列表
def get_books_list_from_db():
    global db
    db.connect()
    cursor = db.cursor()
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
    with FrameProgress() as progress:
        task = progress.add_task("转化为novel_list", total=len(db_list))
        for item in db_list:
            novel["id"] = item[0]
            novel["book_id"] = item[1]
            novel["book_name"] = item[2]
            novel["book_link"] = item[3]
            novel["book_author"] = item[4]
            novel["write_status"] = item[5]
            novel["popularity"] = item[6]
            novel["intro"] = item[7]
            novel["abnormal"] = item[8]
            novel["file_path"] = item[9]
            novel_list.append(novel)
            progress.update(task, advance=1)
    cursor.close()
    db.close()
    return novel_list


# 3.获取没下载的小说
def get_download_books_list_from_db() -> list:
    global db
    db.connect()
    cursor = db.cursor()
    novel_list = []
    # 需要获取的值：id,book_id,book_name,book_link,book_author,write_status,popularity,intro,abnormal,file_path
    cursor.execute(
        "SELECT id,book_id,book_name,book_link,book_author,write_status,popularity,intro,abnormal FROM books WHERE file_path IS NULL"
    )
    db_list = cursor.fetchall()
    with FrameProgress() as progress:
        task = progress.add_task("转化为novel_list", total=len(db_list))
        for item in db_list:
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
            novel["id"] = item[0]
            novel["book_id"] = item[1]
            novel["book_name"] = item[2]
            novel["book_link"] = item[3]
            novel["book_author"] = item[4]
            novel["write_status"] = item[5]
            novel["popularity"] = item[6]
            novel["intro"] = item[7]
            novel["abnormal"] = item[8]
            novel["file_path"] = None
            novel_list.append(novel)
            progress.update(task, advance=1)
    cursor.close()
    db.close()
    return novel_list


# 4.保存小说内容

# 入口
if __name__ == "__main__":
    reset_books_list_to_db()
    # novel_list = get_download_books_list_from_db()
    # for novel in novel_list:
    #     # chapter_list = get_chapters(novel)
    #     print(novel["intro"], "\n\n")
    #     pass
