import time
import random
from state.loop import bb,tt,fs
from utils import ihttp
from loguru import logger


def start():
  return "success"

def login():
  session_filepath = tt.get_kwai_session_filepath() 
  session = fs.read(session_filepath)
  if session is None:
     response = ihttp.post(f"{bb.config.gwServerURL}/v1/authWithoutCode", json={"proxy_url":bb.socks5})
     if response.ok:
       data = response.json()
       if data["mmret"] == 0:
         fs.write(session_filepath, data["session"])
         return "self"
     return "failed"
  bb.session = session
  return "success"

def do_task():
  json = {
    "session": bb.session,
    "proxy_url": bb.socks5,
    "taskType": bb.task["task_type"],
  }
  json.update(bb.task_data)
  response = ihttp.post(f"{bb.config.gwServerURL}/v1/spider", json=json)
  if response.ok:
    data = response.json()
    if data["mmret"] == 0:
      bb.task_result = data["data"]
      return "success"
    elif data["mmret"] == -40300:
      fs.delete(tt.get_kwai_session_filepath())
      return "acc_error"
  return "failed"

def task_success():
  json = {
    "result": 1,
    "imei": tt.get_spider_imei(),
    "task_id": bb.task["task_id"],
    "data": bb.task_result,
  }
  response = ihttp.post(f'{bb.config.taskServerURL}/{bb.task["task_type"]}', json=json)
  if response.ok:
    data = response.json()
    if data["result"] == 1:
      bb.reuseSocks5 = True
      delay = random.randint(2, 8)
      logger.info("delay {}s for next task", delay)
      time.sleep(delay)
      return "success"
  return "failed"

