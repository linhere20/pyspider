from state.loop import bb,tt,fs
from utils import ihttp
from loguru import logger

def start():
  return "success"

def spider_register():
  return "success"

"""
{
  "task_id": "任务ID",
  "task_type": "任务类型",
  "data": {
    这里是具体任务特有的字段
  }
}
"""
def get_task():
  response = ihttp.get(f"{bb.config.taskServerURL}/getTask?type={tt.get_spider_type()}&imei={tt.get_spider_imei()}")
  if response.ok:
    data = response.json()
    if data["result"] == 1:
      bb.task = data
      bb.task_data = data.get("data", {})
      return tt.get_spider_type()
  return "failed"

def get_socks5():
  if bb.reuseSocks5 is True and bb.socks5 is not None:
    bb.reuseSocks5Times = bb.get("reuseSocks5Times", 0) + 1
    logger.info("reuseSocks5 is True, times {}, {} ", bb.reuseSocks5Times, bb.socks5)
    bb.reuseSocks5 = False
    return "success"

  response = ihttp.get("http://get.socks5.com")
  if response.ok:
    try:
      data = response.json()
    except Exception:
      return "failed"

    if data["code"] == 0:
      bb.socks5 = f'socks5://@{data["data"][0]["ip"]}:{data["data"][0]["port"]}'
      bb.proxies = {
        "http": bb.socks5,
        "https": bb.socks5
      }
      logger.info("change {}", bb.socks5)
      bb.reuseSocks5 = False
      return "success"
  return "failed"
