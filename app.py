import os
import sys
import click
from utils.map import Map
from config import load_config
from state import loop
from loguru import logger

project_path = os.path.dirname(os.path.abspath(__file__))
project_name = os.path.basename(os.path.normpath(project_path))
sys.path.insert(0, project_path)


def init_logger(**kwargs):
  log_name = f'{kwargs["type"]}-{kwargs["name"]}'
  log_dir = os.path.join(project_path, "logs")
  log_file = os.path.join(log_dir, f"{log_name}.log")
  error_log_file = os.path.join(log_dir, f"{log_name}-error.log")

  fmt = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <4}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
  logger.remove(handler_id=None)
  logger.add(sys.stdout, level="DEBUG", format=fmt)
  logger.add(log_file, level="DEBUG", format=fmt, rotation="100 MB", retention="14 days", compression="zip")
  logger.add(error_log_file, level="ERROR", format=fmt, rotation="100 MB", retention="14 days", compression="zip")


@click.command()
@click.option("--env", default="dev", type=str, help="env")
@click.option("--type", type=str, help="spider type")
@click.option("--name", type=str, help="spider name")
@logger.catch
def main(**kwargs):
  if kwargs["type"] is None or kwargs["name"] is None:
    raise Exception("spider type or name can not be null")

  init_logger(**kwargs)

  config = load_config(kwargs["env"])
  config._args = kwargs
  logger.info("load config: {}", config)

  loop.bb.config = config
  loop.start()

if __name__ == "__main__":
  main()

