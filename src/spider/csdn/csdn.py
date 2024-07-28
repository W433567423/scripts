import requests
from bs4 import BeautifulSoup
import os
from selenium import webdriver
import time

originCookie = """
uuid_tt_dd=10_28743752850-1714137282724-214204; Hm_up_6bcd52f51e9b3dce32bec4a3997715ac=%7B%22islogin%22%3A%7B%22value%22%3A%220%22%2C%22scope%22%3A1%7D%2C%22isonline%22%3A%7B%22value%22%3A%220%22%2C%22scope%22%3A1%7D%2C%22isvip%22%3A%7B%22value%22%3A%220%22%2C%22scope%22%3A1%7D%7D; cf_clearance=FenZ3uS9iXqwzUnUdvNb5kvzt4XXgw1sznjgjNWXRHI-1716800043-1.0.1.1-3kwVnB0AKfXVWXEAtxiOW8Jaz8z6UsAhWBIH.f8u6KpMmvRD2Wgvwx6PjV17j8I5j4X31C6NqIfxgkllgiewzQ; c_dl_prid=-; c_dl_rid=1719906867459_247045; c_dl_fref=https://www.bing.com/; c_dl_fpage=/download/weixin_50843918/89406748; c_dl_um=distribute.pc_search_result.none-task-blog-2%7Eall%7Etop_positive%7Edefault-1-127914382-null-null.142%5Ev100%5Epc_search_result_base1; UN=m0_54500234; p_uid=U010000; historyList-new=%5B%5D; FCNEC=%5B%5B%22AKsRol8_3UObjLdHyYILVnN_YSQnwn6vxIC0O7yochA3kodTctSpdXmoEKGyyhbL5sWbCW9Uukwv4WepHaV2VbYHbRzwPduBTYMs5iTkMURUcsmQuD620n4i7xWtivK44Ad4u8SsVPfyOHp-b56xrPJgtaKVrSHpiQ%3D%3D%22%5D%5D; c_hasSub=true; _clck=aivykm%7C2%7Cfnl%7C0%7C1577; dc_session_id=10_1721374884773.880941; c_segment=12; dc_sid=8140c9a517b033d8a4f05841f8274b17; Hm_lvt_6bcd52f51e9b3dce32bec4a3997715ac=1721265121,1721288377,1721355136,1721374888; HMACCOUNT=0659AD0FA2C69EBB; ssxmod_itna=eqmx0D9Gi=eCwqmq0dD=wg0rKGOCdqDBWahiQc6mx0y03GzDAxn40iDt=rHo8Q1G04q+C087vQtQ7Ci+Id=33+YFKjIO4GLDmKDySG8D+oD445GwD0eG+DD4DW3qAoDexGPynLMKGWD4qDRDAQDzudyC0vgCq=DmMNDGTKUD7QDIdtqDDNqlnGHDiYDQ4GWCLtUCC03xGUtfkGxCqDMUeGXFBFqCdbCccGlfqFOdpPn3jiDtqD9Kn=DbRL3x0pB9LWGfGP4f7+sYimoF0ptKo+3QAqelIwP7XDelCCNlCeqeMMjQDDAS0MsQDxD=; ssxmod_itna2=eqmx0D9Gi=eCwqmq0dD=wg0rKGOCdqDBWahiQc6Dn93HeDsdrKDLliCNekqnbU57/KWTejzeVak22mgCYjIbzbo8nHtw3MgBFjzaf+AII30KmQl4qKMQ/vA8rGSrS+Pm=lpiUzsf12renhWCWu54tezq70r1erhd92rreHNhiFP=FrewaR=o79Yhr0+=FKO1PT5A1TCPCIxeaGCr=9aDFq44Fw=aQEb9enNe+ei=bjWXUMpFzDOeBBkc=Qobch0rsOswiKTY=i7/rBxLD07=408DYIx4D===; __gads=ID=85262d8a6233c2a0:T=1714463210:RT=1721375205:S=ALNI_MbUqX6EQMC6ETpX6wfmRBkX-vpbEw; __gpi=UID=00000e00ecb304bf:T=1714463210:RT=1721375205:S=ALNI_MZrvnPLi4bo8PTt3ruz5Qge9NJX2A; __eoi=ID=bb2ea58c483b4c2b:T=1714463210:RT=1721375205:S=AA-Afja92nJbDDfFW_c2cJg8nAyE; tfstk=fiOtnm2T2DmG0JMD1FMHobzzdVgH6CLaOh87iijghHKplhgNnCvmMKL9fRXj3nxYDMK4sIYDlKFvzMRi7i0aDnLvWc71GR_CAZb7GcW6MpPvzERi7s0N_F5VG0moZsLw7s-Al1boxegfuP4-9jlk7FzC35VQAb2xni0EkitfC9wCSM__1OtjO9sFuZZ1l5gpRM7fGNNfcwNCPaN_C5G31qjQ3iNvHbNLw3U3MVuw9wiVVFQd8wRdWOI5fMFXHBQOBgT9_dAqdwOH9TX3o0CBzpx1J_hYO1BJChQB8mFRfLYP3I6K95beChdCHB0qQedAXTO1prF5Te7XctpE27bOspBJ6du4AFtlXL1woznMJTpdUw6QkR1MEUAVFCGT4MXPk3QJXlIzSQA8NPZl2Z2sJ2e43O_h04L5-iPxZqbdqVH03-WnFS2OHVybh4MRJg0Kq-yVCm1..; c_first_ref=cn.bing.com; c_first_page=https%3A//blog.csdn.net/u010953692/article/details/78320025; c_dsid=11_1721378236658.433779; creativeSetApiNew=%7B%22toolbarImg%22%3A%22https%3A//img-home.csdnimg.cn/images/20231011044944.png%22%2C%22publishSuccessImg%22%3A%22https%3A//img-home.csdnimg.cn/images/20240229024608.png%22%2C%22articleNum%22%3A0%2C%22type%22%3A0%2C%22oldUser%22%3Afalse%2C%22useSeven%22%3Atrue%2C%22oldFullVersion%22%3Afalse%2C%22userName%22%3A%22m0_54500234%22%7D; SESSION=a4df0a8c-79be-43d9-8e95-f71e48084400; hide_login=1; loginbox_strategy=%7B%22taskId%22%3A317%2C%22abCheckTime%22%3A1721378375541%2C%22version%22%3A%22ExpA%22%2C%22nickName%22%3A%22tutu7331%22%2C%22blog-threeH-dialog-expa%22%3A1721378377516%7D; _clsk=1sqb1sz%7C1721378378677%7C8%7C0%7Cq.clarity.ms%2Fcollect; creative_btn_mp=3; log_Id_click=911; UserName=m0_54500234; UserInfo=84e9a1ca573a4193a5db379deef69e82; UserToken=84e9a1ca573a4193a5db379deef69e82; UserNick=tutu7331; AU=8FE; BT=1721378407215; dc_tos=sgv42z; c_pref=https%3A//shangjinzhu.blog.csdn.net/category_10943144_11.html; c_ref=https%3A//shangjinzhu.blog.csdn.net/category_10943144.html; Hm_lpvt_6bcd52f51e9b3dce32bec4a3997715ac=1721378430; c_page_id=default; log_Id_pv=418; log_Id_view=17323
"""


# 拆解cookie(字符串转数组)
def parse_cookie():
    cookies = []
    for item in originCookie.split(";"):
        key = item.split("=")[0].replace("\n", "")
        value = item.split("=")[1].replace("\n", "")
        # value从url编码转解码
        cookies.append(
            {
                "name": requests.utils.unquote(key),
                "value": requests.utils.unquote(value),
            }
        )

    return cookies


def get_file_path(name=None):
    currentPath = os.path.dirname(os.path.abspath(__file__))
    if name:
        return os.path.join(currentPath, "images", f"{name}.png")
    else:
        return os.path.join(currentPath, "list.txt")


def getList():
    arr = []
    # 循环11次
    for i in range(11):
        url = "https://shangjinzhu.blog.csdn.net/category_10943144"
        if i == 0:
            url = url + ".html"
        else:
            url = f"{url}_{i + 1}.html"

        res = session.get(url, headers={})
        res.encoding = "utf-8"
        soup = BeautifulSoup(res.text, "html.parser")
        list = soup.find("ul", class_="column_article_list").findAll("li")
        for j in list:
            item = {}
            item["link"] = j.find("a").attrs["href"]
            item["title"] = (
                j.find("h2", class_="title")
                .text.replace("\n", "")
                .replace(" ", "")
                .replace("【彻底搞懂算法和数据结构—算法之翼】", "")
            )
            arr.append(item)
    return arr[1:]


def get_image(item):
    # 保存图片
    options = webdriver.ChromeOptions()
    options.add_argument("--kiosk")
    options.add_argument(f"Cookie={originCookie}")
    print(options)
    diver = webdriver.Chrome(options=options)
    diver.get(item["link"])

    # for cookie in parse_cookie():
    #     diver.add_cookie
    #     diver.add_cookie(cookie)
    diver.get(item["link"])
    # 页面滚动到底部
    js = "var q=document.documentElement.scrollTop=10000"
    diver.execute_script(js)
    time.sleep(2)
    #
    diver.find_element("id", "content_views").screenshot(get_file_path(item["title"]))
    diver.quit()


# 保存到本地
def save(arr):
    with open(get_file_path(), "w", encoding="utf-8") as f:
        for i in arr:
            f.write(str(i))
            f.write("\n")


# 读取本地
def load():
    if not os.path.exists(get_file_path()):
        return []
    arr = []
    with open(get_file_path(), "r", encoding="utf-8") as f:
        for i in f.readlines():
            arr.append(eval(i))
    return arr


if __name__ == "__main__":
    # 获取当前目录
    session = requests.session()  # 创建会话
    parse_cookie()
    list = load()
    if len(list) == 0:
        print("list is empty, start spider...")
        list = getList()
        save(list)
    print("start download...")
    # 创建文件夹
    if not os.path.exists(os.path.join(os.path.dirname(get_file_path()), "images")):
        os.mkdir(os.path.join(os.path.dirname(get_file_path()), "images"))
    for i in list[:1]:
        get_image(i)
    print("download success")
    exit()
