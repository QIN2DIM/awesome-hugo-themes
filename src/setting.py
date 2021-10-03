from os.path import join, dirname

import pytz
from loguru import logger

# ========================================
# TODO (✓) Global Config
# ========================================
# There are two options, development and production
AWESOME_ENVIRONMENT = "development"

# Time zone
TIME_ZONE_CODE = "Asia/Shanghai"
TIME_ZONE = pytz.timezone(TIME_ZONE_CODE)

# ========================================
# TODO (✓) Project Paths
# ========================================
SERVER_ROOT = dirname(__file__)

SERVER_DIR_DATABASE = join(SERVER_ROOT, "database")

SERVER_DIR_DATABASE_TEMP = join(SERVER_DIR_DATABASE, "cache")

SERVER_NAME_BUILD_CACHE = join(SERVER_DIR_DATABASE, "awesome-hugo-themes")

SERVER_PATH_RELATED_REPO = join(SERVER_DIR_DATABASE, "related_repo")

SERVER_DIR_DATABASE_LOG = join(SERVER_DIR_DATABASE, "logs")

SERVER_PATH_README = join(SERVER_ROOT, "README.md")

# ========================================
# TODO (✓) Logger Setting
# ========================================
logger.add(
    sink=join(SERVER_DIR_DATABASE_LOG, "runtime.log"),
    level="DEBUG",
    rotation="1 day",
    retention="20 days",
    encoding="utf8",
)
logger.add(
    sink=join(SERVER_DIR_DATABASE_LOG, "error.log"),
    level="ERROR",
    rotation="1 week",
    encoding="utf8",
)
