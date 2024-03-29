# -*- coding: utf-8 -*-
# Time       : 2021/10/3 9:01
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description: 初始化数据库
import csv
import typing

import bs4.element
import requests.exceptions
from aiohttp import ClientSession
from bs4 import BeautifulSoup

from utils.accelerator import AshFramework

BASE_URL = "https://themes.gohugo.io"


class AwesomeThemesBuilder(AshFramework):
    def __init__(self, output_path_csv: str):
        super().__init__()
        self.output_path_csv = output_path_csv

        self.alias = "nil"
        self.session = requests.session()

    def preload(self):
        """获取 hugo themes 展示页的所有主题链接"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.51"
        }

        session = requests.session()
        response = session.get(BASE_URL, headers=headers)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, "html.parser")
        section = soup.find("section")
        tags = section.find_all("a")

        urls = [tag["href"] for tag in tags]
        self.docker = urls

    async def _control_driver(self, context: typing.Any, session: ClientSession):
        async with session.get(context) as response:
            soup = BeautifulSoup(await response.text(), "html.parser")

        section = soup.find("div", class_="flex-l bg-light-gray")
        subsection: bs4.element.ResultSet = section.find("ul").find_all("li")

        # 主题名
        theme = section.find("h1")
        # 主题简介
        description = section.find("p")
        # 主题展示页链接
        profile_link = section.find("img")["srcset"].strip().split(" ")[0]
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

        self.done_q.put(
            {
                "theme": theme.text.strip() if theme else self.alias,
                "description": description.text.strip() if description else self.alias,
                "profile_link": profile_link,
                "author": author.text.strip() if author else self.alias,
                "github_stars": github_stars.text.strip() if github_stars else self.alias,
                "updated": updated.text.strip() if updated else self.alias,
                "license": license_.text.strip() if license_ else self.alias,
                "theme_tags": theme_tags,
                "theme-repo": self.alias,
                "theme-ref": context,
            }
        )

    def offload(self):
        items = []
        while not self.done_q.empty():
            items.append(self.done_q.get())

        with open(self.output_path_csv, "w", encoding="utf8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(list(items[0].keys()))
            for item in items:
                writer.writerow(list(item.values()))
