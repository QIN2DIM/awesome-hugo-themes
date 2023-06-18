# -*- coding: utf-8 -*-
# Time       : 2021/10/3 17:18
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:

import csv
import typing

from loguru import logger

from setting import project, Env
from utils import from_text_to_markdown, format_time


def convert_data_format(path_input: str, to: typing.Optional[str] = None):
    """
    - Format
        theme            author                     License      GitHub Stars  updated
        [theme](ref)      [author](repo/"alias")     text         number        time
    - Title
        theme,description,profile_link,author,github_stars,updated,
        license,theme_tags,theme-repo,theme-ref

    :param path_input: awesome-hugo-themes.csv
    :param to: ./new-table.csv
    :return:
    """
    # 数据重新写回不影响
    to = to if to else path_input

    with open(path_input, "r", encoding="utf8") as f:
        reader = list(csv.reader(f))

    with open(to, "w", encoding="utf8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Theme", "Author", "License", "GitHub Stars", "Updated"])
        for i in reader[1:]:
            new_theme = from_text_to_markdown(i[0].replace("|", "\\|"), i[-1])
            new_author = from_text_to_markdown(
                i[3].replace("|", "\\|"), i[-2] if i[-2] != "nil" else "#"
            )
            new_license = i[-4]
            new_github_stars = i[4]
            new_updated = i[5]
            writer.writerow([new_theme, new_author, new_license, new_github_stars, new_updated])


def new_markdown_wrapper(path_markdown_context: str, to: str, build_mode="none"):
    h1_title = "# awesome-hugo-themes\n"

    description = (
        f"> Automated deployment @ {format_time('time')} Asia/Shanghai &sorted={build_mode} \n"
    )

    with open(path_markdown_context, "r", encoding="utf8") as f:
        data = [i for i in f.read().split("\n") if i]

    with open(to, "w", encoding="utf8") as f:
        f.write(f"{h1_title}\n")
        f.write(f"{description}\n")
        for i in data:
            f.write(f"{i}\n")


def from_csv_to_markdown(
    path_input: str,
    to: typing.Optional[str] = "README-spider.md",
    style: typing.Literal["center", "normal"] = "center",
):
    if style == "center":
        markdown_table_sep = " :---: "
    else:
        markdown_table_sep = " --- "
    markdown_table_context = ""

    with open(path_input, "r", encoding="utf8") as f:
        reader = list(csv.reader(f))

    for tag in reader[1:]:
        markdown_table_context += "\n|{}|".format("|".join(tag))

    with open(to, "w", encoding="utf") as f:
        f.write(f"|{'|'.join(reader[0])}|\n")
        f.write(f"|{'|'.join([markdown_table_sep for _ in range(reader[0].__len__())])}|\n")
        for tag in reader[1:]:
            f.write("|{}|\n".format("|".join(tag)))


def sort_data(path_input: str, by: str = "stars"):
    """
    调整排序
    :param path_input:
    :param by: stars ,updated
    :return:
    """
    new_data = []
    with open(path_input, "r", encoding="utf8") as f:
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
    with open(path_input, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(reader[0])
        for data in new_data:
            writer.writerow(data)


class MarkdownRender:
    def __init__(self, **kwargs):
        self.path_hugo_urls_plus = kwargs.get("path_hugo_urls_plus")

        # ::hugo_pending_csv:: 对合并后的数据进行了排序、格式预渲染以及排版的表
        self.hugo_pending_csv = str(project.cache.joinpath(f"pending_to_markdown.csv"))

        # ::hugo_themes_markdown_context:: 将 csv 映射成 markdown 文件
        # 仅当 PRODUCTION 时才把处理完毕的缓存文件移动到项目根目录下，否则先暂存在缓存目录下
        self.hugo_themes_markdown_context = project.get_readme_path(_env=Env.DEVELOPMENT)

    @classmethod
    def from_hugo_urls_plus(cls):
        return cls(path_hugo_urls_plus=str(project.path_hugo_urls_plus))

    def run(self, path_readme: str, sort: typing.Literal["stars", "updated"]):
        # 将 csv 表中的数据转换成可以被渲染的 markdown 语法值
        convert_data_format(self.path_hugo_urls_plus, to=self.hugo_pending_csv)
        logger.success(f"Convert the format of the data table")

        # 在原文件上操作，根据 stars 或 updated 对 csv 表数据进行降序排序
        sort_data(self.hugo_pending_csv, by=sort)
        logger.success(f"Rearrange table elements", sorted_by=sort)

        # 转换文件格式 csv --> Markdown
        from_csv_to_markdown(self.hugo_pending_csv, to=self.hugo_themes_markdown_context)
        logger.success(f"Generate README.md table file")

        # 向已生成的README文件（markdown-context）注入其他的信息，如采集时间、运行配置等
        # 再根据指定的运行模式（prod/dev）决定改动后的文件输出到项目根还是缓存根
        new_markdown_wrapper(self.hugo_themes_markdown_context, build_mode=sort, to=path_readme)
        logger.success(f"Generate the final readme file")
