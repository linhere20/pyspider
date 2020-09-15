from utils.map import Map

bb = Map()

def get_spider_type():
  return bb.config._args["type"]

def get_spider_name():
  return bb.config._args["name"]

def get_spider_imei():
  return f"{get_spider_type()}-{get_spider_name()}"

def get_kwai_session_filepath():
  return f"kwai/{get_spider_imei()}.session"

def get_xinkuai_cookies_filepath():
  return "xinkuai/cookies.txt"
