import re
from pathvalidate import sanitize_filename


# 处理不规范的小说名(需要成为文件名的字符串)
def normalize_novel_name(str: str) -> str:
    novel_name = str
    # 正则匹配删除()内的内容
    novel_name = re.sub(r"\([^)]*\)", "", novel_name)
    # 正则匹配删除（）内的内容
    novel_name = re.sub(r"（[^）]*）", "", novel_name)

    # 处理特殊字符
    novel_name = (
        sanitize_filename(novel_name)
        .replace("、", ",")
        .replace("，", ",")
        .replace("：", ",")
        .replace("！", "!")
        .replace("？", "?")
        .replace("（", "(")
        .replace("）", ")")
        .replace("【", "[")
        .replace("】", "]")
        .replace("《", "")
        .replace("》", "")
        .replace("“", "")
        .replace("”", "")
        .replace("‘", "")
        .replace("’", "")
        .replace(" ", "")
    )
    return novel_name
