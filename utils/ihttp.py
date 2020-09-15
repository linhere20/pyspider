import requests
from loguru import logger

__all__ = ["get", "post"]

session = requests.Session()
default_timeout = 60

def get(url, **kwargs):
  response = requests.Response()
  response.status_code = 499
  if "timeout" not in kwargs:
    kwargs["timeout"] = default_timeout

  try:
    logger.info("http:get:req [url:{}, kwargs:{}]", url, kwargs)
    response = session.get(url, **kwargs)
    logger.info("http:get:rsp [code:{}, time:{}, content:{}]", response.status_code, response.elapsed.total_seconds(), response.text)
  except requests.RequestException as e:
    logger.error("http:get:err {}", e)
    response.reason = str(e)
  return response

def post(url, data=None, json=None, **kwargs):
  response = requests.Response()
  response.status_code = 499
  if "timeout" not in kwargs:
    kwargs["timeout"] = default_timeout

  try:
    logger.info("http:post:req [url:{}, data:{}, json:{}, kwargs:{}]", url, data, json, kwargs)
    response = session.post(url, data=data, json=json, **kwargs)
    logger.info("http:post:rsp [code:{}, time:{}, content:{}]", response.status_code, response.elapsed.total_seconds(), response.text)
  except requests.RequestException as e:
    logger.error("http:post:err {}", e)
    response.reason = str(e)
  return response
