# -*- coding: utf-8 -*-
# Time       : 2021/10/3 9:05
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
from __future__ import annotations

from gevent import monkey

monkey.patch_all()
import os
import typing

from explorer.builder import AwesomeThemesBuilder
from explorer.finder import LinkFinder
from explorer.render import MarkdownRender
from loguru import logger
from setting import project, Env, SortMethod


def _check_env_args(env: str | None, sort: str | None):
    if env in [Env.DEVELOPMENT, "dev", None]:
        env = Env.DEVELOPMENT
    elif env not in [Env.PRODUCTION]:
        logger.error(f"The `env` param[{env}] must be within [{Env.PRODUCTION}, {Env.DEVELOPMENT}]")
        return

    if sort in [SortMethod.BY_STARS, None]:
        sort = SortMethod.BY_STARS
    elif sort not in [SortMethod.BY_UPDATED]:
        logger.error(
            f"The `sort` param[{sort}] must be within [{SortMethod.BY_STARS}, {SortMethod.BY_UPDATED}]"
        )
        return

    os.environ["ENV"] = env
    os.environ["SORT"] = sort
    return True


class Scaffold:
    @staticmethod
    @logger.catch()
    def build(
        force: bool | None = False,
        sort: typing.Literal["stars", "updated"] = "stars",
        env: typing.Literal["development", "production"] = "development",
        prod: bool | None = None,
        dev: bool | None = None,
    ):
        """
        Run the collection task for the first time
        and use the full power crawler to initialize the local database.

        ——————————————————————————————————————————————————————————————
        Usage: python main.py build
             | python main.py build --key=stars
             | python main.py build --key=stars --env=development
        ——————————————————————————————————————————————————————————————

        :param env: default `development`, options: [development, production]
        :param force: default to `False`, Overwrite existing data if True
        :param sort: default to `stars`, optional ["stars", "updated"]
        :param dev:
        :param prod:
        :return:
        """
        if prod is True:
            env = Env.PRODUCTION
        if dev is True:
            env = Env.DEVELOPMENT
        if not _check_env_args(env, sort):
            return

        env, sort, _steps = os.environ["ENV"], os.environ["SORT"], 3
        logger.success(f"STARTUP HelloHugo - {env=} {sort=} {force=}")

        logger.info(f"[1/{_steps}] >>> RUN the AwesomeThemesBuilder")
        if not project.path_hugo_urls.exists() or force:
            builder = AwesomeThemesBuilder(output_path_csv=str(project.path_hugo_urls))
            builder.fire(power=project.BUILDER_POWER)
        else:
            logger.warning(f"任务已完成，如有需要请添加参数 `build --force` 强制运行")

        logger.info(f"[2/{_steps}] >>> RUN the LinkFinder")
        if not project.path_hugo_urls_plus.exists() or force:
            finder = LinkFinder.from_hugo_urls()
            finder.fire(power=project.FINDER_POWER)
            finder.merge(to=str(project.path_hugo_urls_plus))
        else:
            logger.warning(f"任务已完成，如有需要请添加参数 `build --force` 强制运行")

        logger.info(f"[3/{_steps}] >>> RUN the MarkdownRender")
        render = MarkdownRender.from_hugo_urls_plus()
        render.run(path_readme=project.get_readme_path(env), sort=sort)
