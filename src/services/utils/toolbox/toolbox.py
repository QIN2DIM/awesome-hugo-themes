# -*- coding: utf-8 -*-
# Time       : 2021/10/3 13:46
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
import csv
import sys
from datetime import datetime

import pytz
import requests
from loguru import logger


class ToolBox:
    @staticmethod
    def handle_html(url):
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/94.0.4606.61 Safari/537.36 Edg/94.0.992.31"
        }
        proxies = {"http": None, "https": None}

        session = requests.session()
        response = session.get(url, headers=headers, proxies=proxies)
        response.encoding = response.apparent_encoding

        return response

    @staticmethod
    def to_markdown(text, link, mode="hyperlinks"):
        if mode == "hyperlinks":
            return f"[{text}]({link})"

    @staticmethod
    def format_time(mini="file", tz="Asia/Shanghai"):
        # 方便文件名读写
        if mini == "file":
            return str(datetime.now(pytz.timezone(tz))).split(" ")[0]
        # 精确到人类理解即可
        if mini == "time":
            return str(datetime.now(pytz.timezone(tz))).split(".")[0]

    @staticmethod
    def csv_to_markdown_table(
        input_path_csv: str, output_path="./README-spider.md", style: str = "center"
    ):
        if style == "center":
            markdown_table_sep = " :---: "
        else:
            markdown_table_sep = " --- "
        markdown_table_context = ""

        with open(input_path_csv, "r", encoding="utf8") as f:
            reader = list(csv.reader(f))

        for tag in reader[1:]:
            markdown_table_context += "\n|{}|".format("|".join(tag))

        with open(output_path, "w", encoding="utf") as f:
            f.write(f"|{'|'.join(reader[0])}|\n")
            f.write(f"|{'|'.join([markdown_table_sep for _ in range(reader[0].__len__())])}|\n")
            for tag in reader[1:]:
                f.write("|{}|\n".format("|".join(tag)))

    @staticmethod
    def generate_root_readme(
        path_markdown_context: str, path_project_readme: str, build_mode="none"
    ):
        h1_title = "# awesome-hugo-themes\n"

        description = f"> Automated deployment @ {ToolBox.format_time('time')} Asia/Shanghai &sorted={build_mode} \n"

        with open(path_markdown_context, "r", encoding="utf8") as f:
            data = [i for i in f.read().split("\n") if i]

        with open(path_project_readme, "w", encoding="utf8") as f:
            f.write(f"{h1_title}\n")
            f.write(f"{description}\n")
            for i in data:
                f.write(f"{i}\n")

    @staticmethod
    def table_sorted(input_path_csv: str, by: str = "stars"):
        """
        调整排序
        :param input_path_csv:
        :param by: stars ,updated
        :return:
        """
        new_data = []
        with open(input_path_csv, "r", encoding="utf8") as f:
            reader = list(csv.reader(f))

        if by == "stars":
            # str --> int
            for i in reader[1:]:
                i[-2] = int(i[-2])
            # Descending order according to GitHub Stars.
            new_data = sorted(reader[1:], key=lambda x: x[-2], reverse=True)
        elif by == "updated":
            new_data = sorted(reader[1:], key=lambda x: x[-1], reverse=True)

        # new_data --> input.csv
        with open(input_path_csv, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(reader[0])
            for data in new_data:
                writer.writerow(data)

    @staticmethod
    def init_log(**sink_path):
        event_logger_format = (
            "<g>{time:YYYY-MM-DD HH:mm:ss}</g> | "
            "<lvl>{level}</lvl> - "
            # "<c><u>{name}</u></c> | "
            "{message}"
        )
        logger.remove()
        logger.add(
            sink=sys.stdout,
            colorize=True,
            level="DEBUG",
            format=event_logger_format,
            diagnose=False,
        )
        if sink_path.get("error"):
            logger.add(
                sink=sink_path.get("error"),
                level="ERROR",
                rotation="1 week",
                encoding="utf8",
                diagnose=False,
            )
        if sink_path.get("runtime"):
            logger.add(
                sink=sink_path.get("runtime"),
                level="DEBUG",
                rotation="20 MB",
                retention="20 days",
                encoding="utf8",
                diagnose=False,
            )
        return logger
