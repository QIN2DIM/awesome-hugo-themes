# -*- coding: utf-8 -*-
# Time       : 2021/10/3 9:05
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
from gevent import monkey

monkey.patch_all()

import os.path

from services.workflows.build import AwesomeThemesBuilder, preload
from services.workflows.find_repo import review, merge, FindRelatedLink
from services.workflows.show import format_conversion
from setting import SERVER_NAME_BUILD_CACHE, SERVER_DIR_DATABASE_TEMP
from setting import logger, SERVER_PATH_README, SERVER_ROOT
from utils.toolbox import format_time, csv_to_markdown_table, generate_root_readme, table_sorted


def check_system_path(dir_):
    if not os.path.exists(dir_):
        os.mkdir(dir_)


def within_error(flag_name: str, key_name: str, within_list: list):
    """

    :param flag_name:
    :param key_name:
    :param within_list:
    :return:
    """
    if key_name not in within_list:
        logger.error(f"<ScaffoldBuild> Wrong input parameter: --{flag_name}=`{key_name}` @ "
                     f"This parameter must be within {within_list}.")
        return False
    return True


class Scaffold:
    def __init__(self, env="development"):
        """

        :param env: Environment.There are two options, development(default) and production.
        """
        self.env = env

        # 存储本次操作的csv文件，从 hugo 官方主题库拿
        self.awesome_csv = f"{SERVER_NAME_BUILD_CACHE}-{format_time()}.csv"
        # 内容经过格式变换，适应 Markdown 写法
        self.awesome_csv_show = f"{SERVER_NAME_BUILD_CACHE}-markdown-{format_time()}.csv"
        self.awesome_csv_show_cache = os.path.join(SERVER_DIR_DATABASE_TEMP, f"SHOW-{format_time()}.csv")
        # 运行缓存
        self.awesome_txt_cache = os.path.join(SERVER_DIR_DATABASE_TEMP, f"REPO-{format_time()}.txt")
        # 自动生成的 README 缓存文件
        self.readme_md_cache = os.path.join(SERVER_DIR_DATABASE_TEMP, f"README-{format_time()}.md")

    @logger.catch()
    def build(self, force: bool = False, key: str = None):
        """
        首次运行采集任务，使用全功率的爬虫初始化本地数据库

        Usage: python main.py build
        or: python main.py build  --force
        or: python main.py build --key=stars    排序输出，根据 GitHub Stars，可选项 stars updated

        Usage: python main.py build --env=production    生产环境构建
        or: python main.py build --env=development      开发环境构建（不指定 `--env` 时默认）

        :param force:
        :param key:
        :return:
        """
        # ===========================================# ===========================================
        # TODO [✓] 路径调整 | 检查路径完整
        # ===========================================# ===========================================
        check_system_path(SERVER_DIR_DATABASE_TEMP)

        # 检查 key 参数是否在范围内
        key = key if key else "stars"
        if not within_error("key", key, ["stars", "updated"]):
            return None
        if not within_error("env", self.env, ["development", "production"]):
            return None

        # 根据参数确定合成的 README.md 输出路径
        # 当为生产环境时，将直接替换工程根目录的 README.md 文件
        if self.env == "production":
            build_path = os.path.join(os.path.dirname(SERVER_ROOT), "README.md")
        else:
            build_path = SERVER_PATH_README
        # ===========================================# ===========================================
        # TODO [✓] 业务执行
        # ===========================================# ===========================================
        # 启动 Builder 采集器
        if not os.path.exists(self.awesome_csv) or force:
            AwesomeThemesBuilder(preload(), self.awesome_csv).go(power=16)
        else:
            logger.warning(f"<ScaffoldBuild> AwesomeThemesBuilder 任务跳过，今日任务文件已存在{self.awesome_csv}。"
                           "若仍要运行请执行 `build --force`。 ")

        # 启动 Mapping 采集器
        if not os.path.exists(self.awesome_csv_show) or force:
            FindRelatedLink(review(self.awesome_csv), self.awesome_txt_cache).go(power=32)
            # 合并数据
            merge(self.awesome_csv, self.awesome_txt_cache, self.awesome_csv_show_cache)
        else:
            logger.warning(f"<ScaffoldBuild> FindRelatedLink 任务跳过，今日任务文件已存在{self.awesome_csv_show}。"
                           "若仍要运行请执行 `build --force`。 ")

        # 启动 Markdown 格式转换脚本
        format_conversion(self.awesome_csv_show_cache, self.awesome_csv_show)
        logger.success(f"Convert the format of the data table --> {self.awesome_csv_show}")

        # 启动排序脚本，可根据 stars 或 updated 进行（降序）排序
        table_sorted(input_path_csv=self.awesome_csv_show, by=key)
        logger.success(f"Rearrange table elements (key={key}) --> {self.awesome_csv_show}")

        # 启动 csv --> Markdown 映射脚本，自动生成 README 表格文件
        csv_to_markdown_table(self.awesome_csv_show, self.readme_md_cache)
        logger.success(f"Generate README.md table file --> {self.readme_md_cache}")

        # 写入其他数据，嵌入 README 表格，写回/覆盖 Project README
        generate_root_readme(self.readme_md_cache, build_path, key)
        logger.success(f"Generate complete README.md file of project --> {build_path}")

    def server(self):
        """
        部署定时器

        :return:
        """

    def deploy(self):
        """
        链接 GitHub Repository，定时推送

        :return:
        """
