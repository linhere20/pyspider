import time
import random
from state.loop import bb,tt,fs
from utils import ihttp
from loguru import logger
from utils import crypto


def _api(url, referer, json):
  headers = {
    "Cookie": bb.cookies,
    "origin": "https://xk.newrank.cn",
    "referer": referer,
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
  }
  return ihttp.post(url, json=json, headers=headers, proxies=bb.proxies)

def _get_or_default(obj, key, default=None):
  if obj.get(key) is None:
    return default
  return obj.get(key)


def start():
  return "success"

def load_cookies():
  cookies_filepath = tt.get_xinkuai_cookies_filepath() 
  cookies = fs.read(cookies_filepath)
  if cookies is None:
    logger.warning("{} does not exists.", cookies)
    return "failed"
  bb.cookies = cookies
  return "success"

# 新快登录需要走滑块了，尚未处理，目前登录接口不可用，先直接用保存cookies的方式应对
def login():
  account = "xxxx"
  password = "Aa112211"
  password_md5 = crypto.md5(crypto.md5(password) + "daddy")

  json = {
    "account": account,
    "password": password_md5,
    "state": 1
  }

  response = ihttp.post("https://xk.newrank.cn/nr/user/login/loginByAccount", json=json)
  if response.ok:
    data = response.json()
    if data["success"] and hasattr(data["value"], "token"):
      fs.write("xinkuai/token.txt", data["value"]["token"])
      return "success"
  return "failed"

def do_task():
  return bb.task["task_type"]

def spider_video():
  user_id = str(bb.task_data["user_id"])
  pcursor = bb.task_data.get("pcursor", 1)
  size = bb.task_data.get("size", 20)

  bb.task_result = {
    "size": size
  }
  # 超过10页就结束了，新快会返回参数异常
  if type(pcursor) == int and pcursor > 10:
    bb.task_result["data"] = []
    return "success"

  response = _api(
    url="https://xk.newrank.cn/xdnphb/nr/cloud/ks/account/accountDetailPhotoSearch",
    referer=f"https://xk.newrank.cn/data/d/account/works/{user_id}",
    json={
      "keyword": "", "timeStart": "", "timeEnd": "", "dateType": "", "isPromotion": "",
      "userId": user_id, "sort": "", "size": size, "start": pcursor
    }
  )

  if response.ok:
    data = response.json()
    if data["code"] != 2000:
      bb.task_error_code = data["code"]
      bb.task_error_msg = data.get("msg", "")
      return "failed"

    result = []
    for item in data["data"]["list"]:
      if item["userId"] == user_id:
        result.append({
          "account_id": user_id,
          "video_id": str(_get_or_default(item, "photoId", "")),
          "video_duration": int(_get_or_default(item, "duration", 0) / 1000),
          "video_name": _get_or_default(item, "caption", ""),
          "release_time": _get_or_default(item, "time", ""),
          "like_count": int(_get_or_default(item, "likeCount", 0)),
          "comment_count": int(_get_or_default(item, "commentCount", 0)),
          "play_count": int(_get_or_default(item, "viewCount", 0)),
          "share_count": int(_get_or_default(item, "shareCount", 0)),
          "is_promotion": _get_or_default(item, "isPromotion", 0),
          "video_cover_url": _get_or_default(item, "cover", ""),
          "video_url": _get_or_default(item, "mvUrl", ""),
        })
    bb.task_result["total"] = data["data"]["total"]
    bb.task_result["data"] = result
    return "success"
  return "failed"

def spider_user_top():
  search_type = str(bb.task_data["search_type"])
  pcursor = bb.task_data.get("pcursor", 1)
  size = bb.task_data.get("size", 100)

  bb.task_result = {
    "size": size
  }

  response = _api(
    url="https://xk.newrank.cn/xdnphb/nr/cloud/ks/account/accountSearch",
    referer="https://xk.newrank.cn/data/account/search",
    json={
      "input": {"keyword": "", "type": "all"}, "verifyType": [], "contact": "",
      "withFusionShopEntry": "", "maxUserSex": "",
      "accountInfo": {"province": "", "city": "", "ageRange": [], "userSex": "", "constellationName": []},
      "dataPerformance": {"fanRange": [], "newrankIndexRange": [], "avgLike30Range": [],
      "avgComment30Range": [], "avgView30Range": []}, "contentTags": [], "hasLive": "",
      "sort": "fan", "size": size, "start": pcursor, "type": [search_type]
    }
  )
  
  if response.ok:
    data = response.json()
    if data["code"] != 2000:
      bb.task_error_code = data["code"]
      bb.task_error_msg = data.get("msg", "")
      return "failed"

    result = []
    for item in data["data"]["list"]:
      profile = item["profile"]
      ownerCount = item["ownerCount"]

      account_certification_type = ""
      account_certification_content = ""
      if profile.get("verifiedDetail") is not None:
        account_certification_content = _get_or_default(profile["verifiedDetail"], "description", "")
        iconType = profile["verifiedDetail"].get("iconType")
        if iconType == 1:
          account_certification_type = "黄V"
        elif iconType == 2:
          account_certification_type = "蓝V"

      gender = "未知"
      if profile.get("userSex") == "F":
        gender = "女"
      elif profile.get("userSex") == "M":
        gender = "男"

      region = ""
      if profile.get("province") is not None:
        region = region + profile["province"]
      if profile.get("city") is not None:
        region = region + profile["city"]

      platform_category = []
      if item.get("type") is not None:
        platform_category = [item["type"]]

      result.append({
        "account_id": str(item["userId"]),
        "account": _get_or_default(profile, "kwaiId", ""),
        "avatar": _get_or_default(profile, "headurl", ""),
        "account_name": _get_or_default(profile, "userName", ""),
        "account_introduce": _get_or_default(profile, "userText", ""),
        "account_certification_type": account_certification_type,
        "account_certification_content": account_certification_content,
        "gender": gender,
        "region": region,
        "age": int(_get_or_default(profile, "age", 0)),
        "platform_category": platform_category,
        "total_video_count": int(_get_or_default(ownerCount, "photo", 0)),
        "total_display_video_count": int(_get_or_default(ownerCount, "photoPublic", 0)),
        "total_hidden_video_count": int(_get_or_default(ownerCount, "photoPrivate", 0)),
        "total_moment_count": int(_get_or_default(ownerCount, "moment", 0)),
        "total_fans_count": int(_get_or_default(ownerCount, "fan", 0)),
        "total_follow_count": int(_get_or_default(ownerCount, "follow", 0)),
        "platform_tag": _get_or_default(item, "contentTags", [])
      })
    bb.task_result["total"] = data["data"]["total"]
    bb.task_result["data"] = result
    return "success"
  return "failed"
 
def spider_user_rank():
  search_type = str(bb.task_data["search_type"])
  rank_type = bb.task_data["rank_type"]
  rank_date = bb.task_data["rank_date"]
  pcursor = bb.task_data.get("pcursor", 1)
  size = bb.task_data.get("size", 100)

  bb.task_result = {
    "size": size
  }

  if search_type in ["北京","天津","河北","山西","内蒙古","辽宁","吉林","黑龙江","上海","江苏","浙江","安徽","福建","山东","河南","湖北","湖南","广东","广西","海南","重庆","四川","贵州","云南","西藏","陕西","甘肃","青海","新疆","香港","澳门","台湾"]:
    url = "https://xk.newrank.cn/xdnphb/nr/cloud/ks/rank/accountDistrictRankList"
  else:
    url = "https://xk.newrank.cn/xdnphb/nr/cloud/ks/rank/accountAllRankList"

  response = _api(
    url=url,
    referer="https://xk.newrank.cn/data/account/rank/overall",
    json={
      "type": search_type, "rankDate": rank_date, "rankType": rank_type,
      "sort": "newrankIndex", "start": pcursor, "size": size
    }
  )
  
  if response.ok:
    data = response.json()
    if data["code"] != 2000:
      bb.task_error_code = data["code"]
      bb.task_error_msg = data.get("msg", "")
      return "failed"

    result = []
    for item in data["data"]["list"]:
      account_certification_type = ""
      account_certification_content = ""
      if item.get("verifiedDetail") is not None:
        account_certification_content = _get_or_default(item["verifiedDetail"], "description", "")
        iconType = item["verifiedDetail"].get("iconType")
        if iconType == 1:
          account_certification_type = "黄V"
        elif iconType == 2:
          account_certification_type = "蓝V"

      platform_category = []
      if item.get("type") is not None:
        platform_category = [item["type"]]

      result.append({
        "account_id": str(item["userId"]),
        "account": _get_or_default(item, "kwaiId", ""),
        "avatar": _get_or_default(item, "userHead", ""),
        "account_name": _get_or_default(item, "name", ""),
        "account_introduce": "",
        "account_certification_type": account_certification_type,
        "account_certification_content": account_certification_content,
        "gender": "未知",
        "region": _get_or_default(item, "cityName", ""),
        "age": 0,
        "platform_category": platform_category,
        "total_video_count": 0,
        "total_display_video_count": 0,
        "total_hidden_video_count": 0,
        "total_moment_count": 0,
        "total_fans_count": int(_get_or_default(item, "fan", 0)),
        "total_follow_count": 0,
        "platform_tag": []
      })
    bb.task_result["total"] = data["data"]["total"]
    bb.task_result["data"] = result
    return "success"
  return "failed"

def spider_user_single_rank():
  target = bb.task_data["target"]
  sort_type = bb.task_data["sort_type"]
  search_type = str(bb.task_data["search_type"])
  rank_type = bb.task_data.get("rank_type", "realTime") 
  pcursor = bb.task_data.get("pcursor", 1) 
  size = bb.task_data.get("size", 20)

  if target == "accountWithLoseCount" or target == "accountWithHotCount":
    sort_type = "addFanCountSevenRecent"
  elif target == "accountWithPlayCount":
    sort_type = "addClickCountSevenRecent"
  elif target == "accountWithDiggCount":
    sort_type = "addLikeCountSevenRecent"

  bb.task_result = {
    "size": size
  }

  response = _api(
    url=f"https://xk.newrank.cn/xdnphb/nr/cloud/ks/rank/{target}",
    referer="https://xk.newrank.cn/data/account/singleRank/fansUp",
    json={
      "type": search_type, "rankType": rank_type,
      "sort": sort_type, "start": pcursor, "size": size
    }
  )
  
  if response.ok:
    data = response.json()
    if data["code"] != 2000:
      bb.task_error_code = data["code"]
      bb.task_error_msg = data.get("msg", "")
      return "failed"

    result = []
    for item in data["data"]["list"]:
      platform_category = []
      if item.get("type") is not None:
        platform_category = [item["type"]]

      result.append({
        "account_id": str(item["userId"]),
        "account": _get_or_default(item, "kwaiId", ""),
        "avatar": _get_or_default(item, "headurl", ""),
        "account_name": _get_or_default(item, "name", ""),
        "account_introduce": "",
        "account_certification_type": "",
        "account_certification_content": "",
        "gender": "未知",
        "region": _get_or_default(item, "cityName", ""),
        "age": 0,
        "platform_category": platform_category,
        "total_video_count": 0,
        "total_display_video_count": 0,
        "total_hidden_video_count": 0,
        "total_moment_count": 0,
        "total_fans_count": int(_get_or_default(item, "fan", 0)),
        "total_follow_count": 0,
        "platform_tag": []
      })
    bb.task_result["total"] = data["data"]["total"]
    bb.task_result["data"] = result
    return "success"
  return "failed"

def task_success():
  json = {
    "result": 1,
    "imei": tt.get_spider_imei(),
    "task_id": bb.task["task_id"],
  }
  json.update(bb.task_result)
  response = ihttp.post(f'{bb.config.taskServerURL}/{bb.task["task_type"]}', json=json)
  if response.ok:
    data = response.json()
    if data["result"] == 1:
      bb.reuseSocks5 = True
      delay = random.randint(5, 20)
      logger.info("delay {}s for next task", delay)
      time.sleep(delay)
      return "success"
  return "failed"

def task_failed():
  if bb.task_error_code == 4014:
    logger.warning("新快接口超限额，限时3分钟请求")
    time.sleep(60 * 3)
  return "success"

