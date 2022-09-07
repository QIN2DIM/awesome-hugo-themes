import os
from os.path import join, dirname, exists

from services.utils import ToolBox

# ========================================
# TODO (✓) Project Paths
# ========================================
PROJECT_ROOT = dirname(dirname(__file__))

PROJECT_DATABASE = join(PROJECT_ROOT, "database")

DIR_CACHE = join(PROJECT_DATABASE, "cache")

DIR_CACHE_BUILDER = join(PROJECT_DATABASE, "awesome-hugo-themes")

DIR_CACHE_REPOS = join(PROJECT_DATABASE, "related_repo")

DIR_LOG = join(PROJECT_ROOT, "logs")

PATH_README = join(PROJECT_ROOT, "README.md")

# ---------------------------------------------------
# TODO [√]服务器日志配置
# ---------------------------------------------------
logger = ToolBox.init_log(error=join(DIR_LOG, "error.log"), runtime=join(DIR_LOG, "runtime.log"))
for _pending in [PROJECT_DATABASE, DIR_CACHE, DIR_CACHE_BUILDER, DIR_CACHE_REPOS, DIR_LOG]:
    if not exists(_pending):
        os.mkdir(_pending)
