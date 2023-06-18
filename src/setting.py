from __future__ import annotations

import os
import typing
from dataclasses import dataclass
from os.path import dirname
from pathlib import Path

from utils.toolbox import init_log, format_time


class Env:
    PRODUCTION: str = "production"
    DEVELOPMENT: str = "development"


class SortMethod:
    BY_STARS: str = "stars"
    BY_UPDATED: str = "updated"


@dataclass
class Project:
    src_root = Path(dirname(__file__))
    project_root = src_root.parent
    database = project_root.joinpath("database")

    cache = database.joinpath(format_time(pattern="file"))

    # ::path_hugo_urls:: 存放 hugo themes urls
    path_hugo_urls = cache.joinpath(f"hugo_urls.csv")

    # ::path_hugo_urls_plus:: 存放 theme-url 和 github-url 合并后的数据
    path_hugo_urls_plus = cache.joinpath(f"hugo_urls_plus.csv")

    logs = project_root.joinpath("logs")

    def __post_init__(self):
        for k in [self.cache]:
            os.makedirs(k, exist_ok=True)

    def get_readme_path(
        self, _env: typing.Literal["production", "development"] = Env.DEVELOPMENT
    ) -> typing.Optional[str]:
        env2readmd = {
            Env.PRODUCTION: self.project_root.joinpath("README.md"),
            Env.DEVELOPMENT: self.src_root.joinpath("README.dev.md"),
        }
        return str(env2readmd[_env])


project = Project()

logger = init_log(
    error=project.logs.joinpath("error.log"),
    runtime=project.logs.joinpath("runtime.log"),
    serialize=project.logs.joinpath("serialize.log"),
)
