import os


# 处理字符串
def trim(s:str):
    return (
        s.replace("\r", "")
        .replace("\n", "")
        .replace(".txt", "")
        .replace("【完结】", "")
        .replace("/", ",")
        .replace("\\", ",")
        .replace("：", ",")
        .replace(":", ",")
        .replace("（", "(")
        .replace("）", ")")
        .replace("，", ",")
        .replace(" ", "")
    )


# 获取文件路径
def getFilePath(bookName, prefix=""):
    if prefix:
        return f"books/{prefix}/《{bookName}》.txt"
    else:
        return f"books/《{bookName}》.txt"


# 读取错误文件
def readErrorFile():
    # 错误文件不存在
    errorList = []
    if os.path.exists("errorList.txt"):
        with open("errorList.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines:
            book = {}
            book["bookid"] = line.split(" ")[0]
            book["bookname"] = line.split(" ")[1]
            book["authorname"] = line.split(" ")[2]
            book["categoryname"] = line.split(" ")[3].replace("\n", "")
            errorList.append(book)
        f.close()
        return errorList
    else:
        return []  # 读取错误文件


# 过滤小说
def filterBook(errorList, overList, books):
    newArr=[]
    errorIdList=[]
    for e in errorList:
        errorIdList.append(e["bookid"])
    for book in books:
        if not book["bookid"] in errorIdList and not book["bookname"] in overList:
            newArr.append(book)
        else:
            pass
            # if book["bookid"] in errorList:
            #     print(f"\033[1;31m《{book['bookname']}》已下载失败，跳过...\033[0m")
            # if book["bookname"] in overList:
            #     print(f"\033[1;31m《{book['bookname']}》已存在，跳过...\033[0m")
    return newArr


# 获取异常的小说
def get_e_files(filePath):
    novelList = []
    def f(filePath):
        files = os.listdir(filePath)
        for file in files:
            # 打开所有目录
            if os.path.isdir(os.path.join(filePath, file)):
                f(os.path.join(filePath, file))
            else:
                if not file.endswith(".txt"):
                    # 删除
                    os.remove(os.path.join(filePath, file))
                    novelList.append(file)
    f(filePath)
    return novelList


# 获取所有已下载的小说
def get_all_files(filePath):
    novelList = []
    def f(filePath:str):
        files = os.listdir(filePath)
        for file in files:
            # 打开所有目录
            if os.path.isdir(os.path.join(filePath, file)):
                f(os.path.join(filePath, file))
            else:
                if file.endswith(".txt"):
                    novelList.append(file.replace('《','').replace("》.txt", ""))
    f(filePath)
    return novelList

# 获取小说总大小
def get_all_size(filePath):

    def f(filePath):
        size=0
        files = os.listdir(filePath)
        for file in files:
            # 打开所有目录
            if os.path.isdir(os.path.join(filePath, file)):
                size +=f(os.path.join(filePath, file))
            else:
                if file.endswith(".txt"):
                    size += os.path.getsize(os.path.join(filePath, file))
        return size
    # bit转换为mb(保留两位小数)
    return round(f(filePath) / 1024 / 1024, 2)


# 保存小说列表
def save_books_list(books):
    print(f"\033[1;32m---开始保存小说列表{len(books)}本---\033[0m\n")
    with open(f'novelList.txt','w',encoding='utf-8') as f:
        for book in books:
            f.write(f"{book["bookid"]} {book['bookname']} {book["authorname"]} {book["categoryname"]}\n")
    f.close()

# 从本地读取小说列表
def load_local_list():
    # 从本地读取小说列表
    with open('novelList.txt','r',encoding='utf-8') as f:
        lines = f.readlines()
    f.close()
    books=[]
    for line in lines:
        book = {}
        book["bookid"]=line.split(" ")[0]
        book["bookname"]=line.split(" ")[1]
        book["authorname"]=line.split(" ")[2]
        book["categoryname"]=line.split(" ")[3].replace("\n","")
        books.append(book)
    return books
