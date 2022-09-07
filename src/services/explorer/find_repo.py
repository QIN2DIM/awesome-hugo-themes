# -*- coding: utf-8 -*-
# Time       : 2021/10/3 11:06
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description: 尝试查找主题部署的 { 文档链接 / GitHub 仓库链接 }

import csv
import os
from datetime import datetime
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from services.setting import logger
from services.utils import ToolBox, CoroutineSpeedup

_SEP = ","


def review(input_path_csv: str = None) -> list:
    try:
        with open(input_path_csv, "r", encoding="utf8") as f:
            reader = list(csv.reader(f))

        print(">>> preload complete.")
        return [i[-1] for i in reader[1:]]
    except FileNotFoundError as e:
        logger.error(f"数据集预导入失败：{input_path_csv}。{e}")


def merge(input_path_csv: str, cache_txt: str, output_path_csv: str):
    logger.info("Merge data.")

    # 读取第一轮采集的缺少属性的表
    with open(input_path_csv, "r", encoding="utf8") as f:
        reader = list(csv.reader(f))

    # 读取第二轮采集的补充数据
    with open(cache_txt, "r", encoding="utf8") as f:
        data = {i.split(_SEP)[0]: i.split(_SEP)[-1] for i in f.read().split("\n") if i}

    # 根据键值对映射补充表数据并保存
    with open(output_path_csv, "w", encoding="utf8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(reader[0])
        for i in reader[1:]:
            i[-2] = data[i[-1]]
            writer.writerow(i)

    logger.success("Merge data.")


class FindRelatedLink(CoroutineSpeedup):
    def __init__(self, urls: list = None, output_path_txt=None):
        super(FindRelatedLink, self).__init__(docker=urls)

        self.output_path_txt = output_path_txt
        self.sep = _SEP

    def preload(self):
        # Clear file cache.
        if os.path.exists(self.output_path_txt):
            with open(self.output_path_txt, "w", encoding="utf8"):
                pass

    @logger.catch()
    def control_driver(self, task):
        response = ToolBox.handle_html(task)
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
        with open(self.output_path_txt, "a", encoding="utf8") as f:
            if not repo_urls:
                f.write(f"{task}{self.sep}nil\n")
            else:
                f.write(f"{task}{self.sep}{repo_urls[-1]}\n")

        print(
            f">>> [{self.max_queue_size - self.work_q.qsize()}/{self.max_queue_size}] "
            f"{str(datetime.now()).split('.')[0]} GET {task}"
        )
