import time
import random
import os

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
                    novelList.append(file)
    f(filePath)
    return novelList


# 获取所有已下载的小说
def get_all_files(filePath):
    novelList = []
    def f(filePath):
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




if __name__ == "__main__":
    # 每20秒输出一次,并显示上一次的差值
    all_size = 0
    all_files = []
    all_files_origin = get_all_files("books")
    # 异常的小说列表
    errorList = []
    # 失败的小说列表
    defeatList = []
    
    while True:
        # 输出当前时间
        print( f"当前时间~ {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}")
        all_files= get_all_files("books")
        all_size = get_all_size("books")
        errorList = get_e_files("books")
        defeatList = readErrorFile()
        print(f"\033[1;32m已下载成功{len(all_files)-len(all_files_origin)}本\033[0m")

        print(
            f"\033[1;36m已下载{len(all_files)}本小说\n已下载小说总大小:{all_size}MB\033[0m"
        )
        print(
            f"\033[1;31m{len(defeatList)}本小说下载失败\n异常小说名单如下:\033[0m\n{errorList}\n\n"
        )
        # 随机等待1-2分钟
        time.sleep(40 * (1 + random.random()))
