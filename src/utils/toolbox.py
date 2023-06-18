# -*- coding: utf-8 -*-
# Time       : 2021/10/3 13:46
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
import sys
import typing
import urllib.request
from datetime import datetime, timezone, timedelta

import requests
from loguru import logger


def handle_html(url: str):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/99.0.4606.61 Safari/537.36 Edg/94.0.992.31"
    }
    proxies = urllib.request.getproxies()
    session = requests.session()
    response = session.get(url, headers=headers, proxies=proxies)
    response.encoding = response.apparent_encoding

    return response


def from_text_to_markdown(text: str, link: str, mode: typing.Literal["hyperlinks"] = "hyperlinks"):
    if mode == "hyperlinks":
        return f"[{text}]({link})"


def format_time(pattern: typing.Literal["file", "time"] = "file"):
    # timezone of "Asia/Shanghai"
    tz = timezone(timedelta(hours=8))
    now: datetime = datetime.now(tz=tz)

    mini2now = {
        # 方便文件名读写
        "file": str(now).split(" ")[0],
        # 精确到人类理解即可
        "time": str(now).split(".")[0],
    }
    return mini2now[pattern]


def init_log(**sink_channel):
    event_logger_format = "<g>{time:YYYY-MM-DD HH:mm:ss}</g> | <lvl>{level}</lvl> - {message}"
    serialize_format = event_logger_format + "- {extra}"
    logger.remove()
    logger.add(sink=sys.stdout, colorize=True, level="DEBUG", diagnose=False)
    if sink_channel.get("error"):
        logger.add(
            sink=sink_channel.get("error"),
            level="ERROR",
            rotation="1 week",
            encoding="utf8",
            diagnose=False,
        )
    if sink_channel.get("runtime"):
        logger.add(
            sink=sink_channel.get("runtime"),
            level="DEBUG",
            rotation="20 MB",
            retention="20 days",
            encoding="utf8",
            diagnose=False,
        )
    if sink_channel.get("serialize"):
        logger.add(
            sink=sink_channel.get("serialize"),
            format=serialize_format,
            encoding="utf8",
            diagnose=False,
        )
    return logger
