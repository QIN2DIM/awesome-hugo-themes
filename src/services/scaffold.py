# -*- coding: utf-8 -*-
# Time       : 2021/10/3 9:05
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
import typing

from gevent import monkey

monkey.patch_all()

from os.path import join, dirname, exists

from services.explorer.build import AwesomeThemesBuilder, preload
from services.explorer.find_repo import review, merge, FindRelatedLink
from services.explorer.show import format_conversion
from services.setting import DIR_CACHE_BUILDER, DIR_CACHE
from services.setting import logger, PATH_README, PROJECT_ROOT
from services.utils import ToolBox


@logger.catch()
class Scaffold:
    ENV_DEVELOPMENT = "development"
    ENV_PRODUCTION = "production"

    SORT_STARS = "stars"
    SORT_UPDATED = "updated"

    def __init__(self):
        # 存储本次操作的 csv 文件，从 hugo 官方主题库拿
        self.awesome_csv = f"{DIR_CACHE_BUILDER}-{ToolBox.format_time()}.csv"
        # 内容经过格式变换，适应 Markdown 写法
        self.awesome_csv_show = f"{DIR_CACHE_BUILDER}-markdown-{ToolBox.format_time()}.csv"
        self.awesome_csv_show_cache = join(DIR_CACHE, f"SHOW-{ToolBox.format_time()}.csv")
        # 运行缓存
        self.awesome_txt_cache = join(DIR_CACHE, f"REPO-{ToolBox.format_time()}.txt")
        # 自动生成的 README 缓存文件
        self.readme_md_cache = join(DIR_CACHE, f"README-{ToolBox.format_time()}.md")

    def build(
            self,
            force: typing.Optional[bool] = False,
            sort: typing.Optional[str] = None,
            env: typing.Optional[str] = None,
    ):
        """
        首次运行采集任务，使用全功率的爬虫初始化本地数据库

        Usage: python main.py build
        or: python main.py build --key=stars

        :param env: default `development`, options: [development, production]
        :param force:
        :param sort: 输出排序，默认根据 stars 排序，可选项 ["stars", "updated"]
        :return:
        """
        if env in [self.ENV_DEVELOPMENT, "dev", None]:
            env = self.ENV_DEVELOPMENT
        elif env not in [self.ENV_PRODUCTION]:
            logger.error(
                "Wrong input parameter [env] @ "
                f"this parameter must be within [{self.ENV_DEVELOPMENT}, {self.ENV_PRODUCTION}]"
            )
            return

        if sort in [self.SORT_STARS, None]:
            sort = self.SORT_STARS
        elif sort not in [self.SORT_UPDATED]:
            logger.error(
                "Wrong input parameter [sort] @ "
                f"this parameter must be within [{self.SORT_STARS}, {self.SORT_UPDATED}]"
            )
            return

        logger.success(f"STARTUP [ScaffoldBuild] HelloHugo | {sort=} {env=}")

        logger.debug("Start the Builder Collector")
        if not exists(self.awesome_csv) or force:
            AwesomeThemesBuilder(preload(), self.awesome_csv).go(power=16)
        else:
            logger.warning(
                f"<ScaffoldBuild> AwesomeThemesBuilder 任务跳过，今日任务文件已存在{self.awesome_csv}。"
                "若仍要运行请执行 `build --force`。 "
            )

        logger.info("Start the Mapping Collector")
        if not exists(self.awesome_csv_show) or force:
            FindRelatedLink(review(self.awesome_csv), self.awesome_txt_cache).go(power=32)
            merge(self.awesome_csv, self.awesome_txt_cache, self.awesome_csv_show_cache)
        else:
            logger.warning(
                f"<ScaffoldBuild> FindRelatedLink 任务跳过，今日任务文件已存在{self.awesome_csv_show}。"
                "若仍要运行请执行 `build --force`。 "
            )

        # Markdown 格式转换
        format_conversion(self.awesome_csv_show_cache, self.awesome_csv_show)
        logger.success(f"Convert the format of the data table --> {self.awesome_csv_show}")

        # 排序 根据 stars 或 updated 进行（降序）排序
        ToolBox.table_sorted(input_path_csv=self.awesome_csv_show, by=sort)
        logger.success(f"Rearrange table elements (key={sort}) --> {self.awesome_csv_show}")

        # csv --> Markdown 自动生成 README 表格文件
        ToolBox.csv_to_markdown_table(self.awesome_csv_show, self.readme_md_cache)
        logger.success(f"Generate README.md table file --> {self.readme_md_cache}")

        # 写入其他数据，嵌入 README 表格，写回/覆盖 Project README
        path_readme = PATH_README
        if env == self.ENV_PRODUCTION:
            path_readme = join(dirname(PROJECT_ROOT), "README.md")
        ToolBox.generate_root_readme(self.readme_md_cache, path_readme, sort)
        logger.success(f"Generate complete README.md file of project --> {path_readme}")
