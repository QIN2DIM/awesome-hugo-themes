# -*- coding: utf-8 -*-
# Time       : 2021/10/3 11:06
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description: 尝试查找主题部署的 { 文档链接 / GitHub 仓库链接 }

import csv
import typing
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from loguru import logger

from setting import project
from utils import handle_html
from utils.accelerator import CoroutineSpeedup


class LinkFinder(CoroutineSpeedup):
    sep = ","

    name = "LinkFinder"

    # ::runtime_cache:: GitHub 链接采集器的运行时缓存
    runtime_cache: Path = project.cache.joinpath("github_urls.txt")

    # ::from_hugo_urls::input_path_csv::
    path_hugo_urls = str(project.path_hugo_urls)

    @classmethod
    def from_hugo_urls(cls):
        input_path_csv = LinkFinder.path_hugo_urls
        try:
            with open(input_path_csv, "r", encoding="utf8") as f:
                urls = [i[-1] for i in list(csv.reader(f))[1:]]
            return cls(docker=urls)
        except FileNotFoundError as err:
            logger.error(f"<{LinkFinder.name}> 数据集预导入失败", input=input_path_csv, err=err)

    def preload(self):
        # Clear file cache.
        if self.runtime_cache.exists():
            self.runtime_cache.write_text("", encoding="utf8")

    @logger.catch()
    def control_driver(self, context: typing.Any):
        response = handle_html(context)
        soup = BeautifulSoup(response.text, "html.parser")
        tag_a = soup.find_all("a")
        repo_urls = []

        # Good gun.
        for a in tag_a:
            try:
                if (
                    a["href"].startswith("https://github.com/")
                    and not a["href"].startswith("https://github.com/gohugoio/")
                    and not a["href"].startswith("https://github.com/spf13/hugothemes")
                    and urlparse(a["href"]).path.split("/").__len__() >= 3
                ):
                    repo_urls.append(a["href"])
            except KeyError:
                pass

        # Good gun.
        with open(self.runtime_cache, "a", encoding="utf8") as f:
            if not repo_urls:
                f.write(f"{context}{self.sep}nil\n")
            else:
                f.write(f"{context}{self.sep}{repo_urls[0]}\n")

        # print(
        #     f"\r>>> [{self.max_queue_size - self.work_q.qsize()}/{self.max_queue_size}] "
        #     f"{str(datetime.now()).split('.')[0]} GET {task}",
        #     end="",
        # )

    def merge(self, to: str):
        # 读取第一轮采集的缺少属性的表
        with open(self.path_hugo_urls, "r", encoding="utf8") as f:
            reader = list(csv.reader(f))

        # 读取第二轮采集的补充数据
        with open(self.runtime_cache, "r", encoding="utf8") as f:
            data = {i.split(self.sep)[0]: i.split(self.sep)[-1] for i in f.read().split("\n") if i}

        # 根据键值对映射补充表数据并保存
        with open(to, "w", encoding="utf8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(reader[0])
            for i in reader[1:]:
                i[-2] = data[i[-1]]
                writer.writerow(i)
