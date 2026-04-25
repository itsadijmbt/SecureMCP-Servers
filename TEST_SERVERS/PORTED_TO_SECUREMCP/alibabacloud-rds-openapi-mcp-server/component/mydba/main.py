# -*- coding: utf-8 -*-
import asyncio
import mydba.app.config.config_manager as config_manager
from mydba.common.logger import logger, init_logger
from mydba.app.config.settings import settings as app_settings
from mydba.common.global_settings import global_settings
from mydba.common.settings import settings as common_settings
from mydba.provider.command_line import CommandLineProvider

async def main():
    await config_manager.load_config(app_settings.CONFIG_FILE)
    init_logger(common_settings.LOG_CONSOLE_LEVEL, common_settings.LOG_FILE_LEVEL,
                common_settings.LOG_DIR, common_settings.LOG_NAME)
    logger.info("MyDBA starting...")
    command_line = CommandLineProvider()
    await command_line.run()
    # 标记服务退出
    global_settings.IS_EXIT = True
    logger.info("MyDBA exit")

if __name__ == "__main__":
    try:
        asyncio.run(main(), debug=common_settings.DEBUG)
    except KeyboardInterrupt:
        logger.error(f"keyboard interrupt, MyDBA exited")
    except Exception as e:
        logger.error(f"occour excetion, MyDBA exited: {str(e)}")
