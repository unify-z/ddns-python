import core
import asyncio
from loguru import logger
import sys
basic_logger_format = "<green>[{time:YYYY-MM-DD HH:mm:ss}]</green> <level>[{level}] <yellow>[{name}:{function}:{line}]</yellow>: {message}</level>"
logger.remove()
logger.add(sys.stderr, format=basic_logger_format, level="DEBUG", colorize=True)
logger.add("log/log.log")
if __name__ == '__main__':
   logger.info("初始化中")
   try:
      asyncio.run(core.init())
   except Exception as e:
      logger.error(f"出现错误：{e}")
   except KeyboardInterrupt:
      logger.success("成功退出")