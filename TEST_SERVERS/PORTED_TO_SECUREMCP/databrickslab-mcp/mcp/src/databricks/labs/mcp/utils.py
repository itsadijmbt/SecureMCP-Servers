import logging
from pathlib import Path

from fastapi.staticfiles import StaticFiles

logger = logging.getLogger("databricks.labs.mcp")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
handler.setFormatter(formatter)

if not logger.hasHandlers():
    logger.addHandler(handler)


def get_app_index_route() -> StaticFiles:
    return StaticFiles(directory=Path(__file__).parent / "static", html=True)
