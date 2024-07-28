from global_config import session
from bs4 import BeautifulSoup


# 3.获取小说章节数量
def get_chapters_count(novel: dict):
    url = f"https://www.biqugen.net/book/{novel['book_id']}/"
    res = session.get(url, verify=False)
    res.encoding = "gbk"
    res.close()
    soup = BeautifulSoup(res.text, "html.parser")
    count = int(
        (soup.find("select", class_="form-control").find_all("option")[-1].text)
        .split("第")[1]
        .split("页")[0]
    )

    return count


# 3.获取小说章节
def get_chapters(novel: dict):
    url = f"https://www.biqugen.net/book/{novel['book_id']}/"
    count = get_chapters_count(novel)
    for i in range(1, count + 1):
        url = f"https://www.biqugen.net/book/{novel['book_id']}/index_{i}.html"
        res = session.get(url, verify=False)
        res.encoding = "gbk"
        res.close()
        soup = BeautifulSoup(res.text, "html.parser")
        items = soup.find("dl", class_="zjlist").find_all("dd")
        for item in items:
            print(item.find("a").text)
            print(item.find("a").attrs["href"])
        print(items[0])
        exit()
