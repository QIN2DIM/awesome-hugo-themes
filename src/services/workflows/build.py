# -*- coding: utf-8 -*-
# Time       : 2021/10/3 9:01
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description: 初始化数据库
import csv

import bs4.element
from bs4 import BeautifulSoup

from setting import logger
from utils.accelerator.core import CoroutineSpeedup
from utils.toolbox import handle_html

BASE_URL = "https://themes.gohugo.io"


def preload() -> list:
    response = handle_html(BASE_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    section = soup.find("section")
    tags = section.find_all("a")

    urls = [tag['href'] for tag in tags]

    logger.info(">>> PRELOAD AwesomeThemesBuilder.")
    return urls


class AwesomeThemesBuilder(CoroutineSpeedup):
    def __init__(self, urls: list = None, output_path_csv: str = None):
        super(AwesomeThemesBuilder, self).__init__(task_docker=urls)

        self.output_path_csv = output_path_csv if output_path_csv else "./awesome-hugo-themes.csv"
        self.title = []
        self.alias = "nil"

    @logger.catch()
    def control_driver(self, task):
        response = handle_html(task)
        soup = BeautifulSoup(response.text, "html.parser")

        section = soup.find("div", class_="flex-l bg-light-gray")
        subsection: bs4.element.ResultSet = section.find("ul").find_all("li")

        # 主题名
        theme = section.find("h1")
        # 主题简介
        description = section.find("p")
        # 主题展示页链接
        profile_link = section.find("img")['srcset'].strip().split(" ")[0]
        # 作者名
        author = None
        # GitHub Stars
        github_stars = None
        # 最后更新日期
        updated = None
        # 项目许可证
        license_ = None
        # 主题标签
        theme_tags = None
        for check in subsection:
            label = check.find("span", class_="label")
            if label:
                if "GitHub Stars" in label.text:
                    github_stars = check.find("span", class_="value")
                elif "Author" in label.text:
                    author = check.find("a")
                elif "Updated" in label.text:
                    updated = check.find("span", class_="value")
                elif "License" in label.text:
                    license_ = check.find("span", class_="value")
                else:
                    theme_tags = [tag.text for tag in check.find_all("a")]

        self.done_q.put_nowait({
            "theme": theme.text if theme else self.alias,
            "description": description.text if description else self.alias,
            "profile_link": profile_link,
            "author": author.text if author else self.alias,
            "github_stars": github_stars.text if github_stars else self.alias,
            "updated": updated.text if updated else self.alias,
            "license": license_.text if license_ else self.alias,
            "theme_tags": theme_tags,
            "theme-repo": self.alias,
            "theme-ref": task
        })

        print(f">>> [{self.max_queue_size - self.work_q.qsize()}/{self.max_queue_size}] "
              f"GET {theme} {task}")

    def killer(self):
        items = []
        while not self.done_q.empty():
            items.append(self.done_q.get())

        logger.info(f">>> [Builder] Capture Flow to {self.output_path_csv}.")
        with open(self.output_path_csv, "w", encoding="utf8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(list(items[0].keys()))
            for item in items:
                writer.writerow(list(item.values()))
