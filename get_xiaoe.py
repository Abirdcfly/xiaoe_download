# coding:utf-8
"""
用于小鹅通的视频下载，因为小鹅通没有倍速播放，并且PC界面直接拿mobile界面用，太丑，不能忍
"""
from urllib import quote

import requests

CID = "appxxxxxxxxxxxx"  # app_id
RID = "p_xxxxxxxxxxxxx_xxxxxxxx"  # resource_id
UID = "u_xxxxxxxxxxxxx_xxxxxxxxxx"  # user_id
COOKIES = "laravel_session=xxxxxxxxxxxxxxxxxxxxxxxxxx; tgw_l7_route=xxxxxxxxxxxxxxxxxxxxxxxxxx"
# 修改以上变量即可

VIDO_HOST = "https://vod2.xiaoe-tech.com/"
LIST_HOST = "https://pc-shop.xiaoe-tech.com"
COOKIES_DICT = {}
DATA = {}


def main():
    global VIDO_HOST
    parse_cofig()
    page_all = 10  # TODO:自动获取
    for i in range(1, page_all + 1):
        x = get_resource_list(i, page_all)
        for rid, title in x.iteritems():
            try:  # TODO:处理非视频资源
                video_hls = get_videos_m3u8(rid)
                t = video_hls.split("/")
                if t[2].startswith("vod2"):
                    VIDO_HOST = "%(http)s//%(host)s/%(fid)s/%(sid)s/" % {"http": t[0], "host": t[2], "fid": t[3],
                                                                         "sid": t[4]}
                else:
                    VIDO_HOST = "%(http)s//%(host)s/" % {"http": t[0], "host": t[2]}
                data = ''
                for vurl in get_video_detail(video_hls):
                    data += get_ts(vurl, rid)
                file_name = title + ".ts"
                with open(file_name, 'wb') as fd:
                    fd.write(data)
            except:
                continue


def parse_cofig():
    # TODO:从文件导入cookie和网址而不是全局变量
    global COOKIES_DICT
    COOKIES_DICT = {i[0]: i[1] for i in [i.strip().split("=") for i in COOKIES.split(";")]}


def get_ids():
    # TODO: 自动获取CID，RID，UID
    pass


def get_resource_list(page_now, page_all=10):
    """获取课程列表"""
    headers = {"Host": "pc-shop.xiaoe-tech.com",
               "Origin": "http://pc-shop.xiaoe-tech.com",
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                             "AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/62.0.3202.94 Safari/537.36",
               "X-Requested-With": "XMLHttpRequest",
               "Accept": "*/*",
               "DNT": "1",
               "Content-Type": "application/x-www-form-urlencoded",
               "Referer": "http://pc-shop.xiaoe-tech.com/%(cid)s/columnist_detail?id=%(uid)s" % {"cid": CID,
                                                                                                 "uid": UID},
               "Accept-Encoding": "gzip, deflate",
               "Accept-Language": "zh-CN,zh;q=0.9"}
    resource_list_url = "http://pc-shop.xiaoe-tech.com/%(cid)s/open/column.resourcelist.get/2.0" % {"cid": CID}
    payload = "data[page_index]=%(page_now)s" \
              "&data[page_size]=%(page_all)s" \
              "&data[order_by]=start_at:desc" \
              "&data[resource_id]=%(rid)s" \
              "&data[state]=0" \
              "&data[resource_types][]=1" \
              "&data[resource_types][]=2" \
              "&data[resource_types][]=3" \
              "&data[resource_types][]=4" % {
                  "page_now": page_now,
                  "page_all": page_all,
                  "rid": RID}
    r = requests.post(resource_list_url, headers=headers, cookies=COOKIES_DICT, data=quote(payload, "=&"))
    tmp_data = r.json()
    data = {i["id"]: i["title"] for i in tmp_data["data"]}
    return data


def get_video_detail(url):
    """获取某一节内容视频列表"""
    headers = {"Host": "vod2.xiaoe-tech.com",
               "Pragma": "no-cache",
               "Cache-Control": "no-cache",
               "X-Requested-With": "ShockwaveFlash/28.0.0.126",
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                             "AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/62.0.3202.94 Safari/537.36",
               "Accept": "*/*",
               "DNT": "1",
               "Referer": "http://pc-shop.xiaoe-tech.com/%(cid)s/columnist_detail?id=%(uid)s" % {"cid": CID,
                                                                                                 "uid": UID},
               "Accept-Encoding": "gzip, deflate",
               "Accept-Language": "zh-CN,zh;q=0.9"}
    r = requests.get(url, headers=headers, cookies=COOKIES_DICT)
    tmp_data = r.text
    url_list = [i.strip() for i in tmp_data.split("\n") if not i.startswith("#") and i != ""]
    return url_list


def get_videos_m3u8(resource_id):
    """解析某一节内容视频列表得到具体链接"""
    headers = {"Host": "pc-shop.xiaoe-tech.com",
               "Pragma": "no-cache",
               "Cache-Control": "no-cache",
               "Accept": "*/*",
               "Origin": "http://pc-shop.xiaoe-tech.com",
               "X-Requested-With": "XMLHttpRequest",
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                             "AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/62.0.3202.94 Safari/537.36",
               "DNT": "1",
               "Content-Type": "application/x-www-form-urlencoded",
               "Referer": "http://pc-shop.xiaoe-tech.com/%(cid)s/columnist_detail?id=%(uid)s" % {"cid": CID,
                                                                                                 "uid": UID},
               "Accept-Encoding": "gzip, deflate",
               "Accept-Language": "zh-CN,zh;q=0.9"}
    m3u8_url = "http://pc-shop.xiaoe-tech.com/%(cid)s/open/video.detail.get/1.0" % {"cid": CID}
    payload = "data[resource_id]=%(resource_id)s" % {"resource_id": resource_id}
    r = requests.post(m3u8_url, headers=headers, cookies=COOKIES_DICT, data=quote(payload, "="))
    tmp_data = r.json()
    video_hls = tmp_data["data"]["video_hls"]
    return video_hls


def get_ts(vurl, rid):
    """下载视频分片"""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                             "AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/62.0.3202.94 Safari/537.36",
               "X-Requested-With": "ShockwaveFlash/28.0.0.126",
               "Accept": "*/*",
               "DNT": "1",
               "Referer": "http://pc-shop.xiaoe-tech.com/%(cid)s/video_details?id=%(rid)s" % {"cid": CID,
                                                                                              "rid": rid},
               "Accept-Encoding": "gzip, deflate",
               "Accept-Language": "zh-CN,zh;q=0.9"}
    r = requests.get(VIDO_HOST + vurl, headers=headers, cookies=COOKIES_DICT, stream=True)
    return r.content


if __name__ == '__main__':
    main()
