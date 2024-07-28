from global_config import db


# 1-5.重置数据库表books
def reset_books_list_to_db():
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
