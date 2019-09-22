import datetime
import sys

from loguru import logger

from .app import DuplicateImagesRemoverApplication


if __name__ == "__main__":
    tm_begin = datetime.datetime.utcnow()
    logger.remove()
    logger.add(sys.stderr, format="{time} {level} {message}", level="INFO")

    app = DuplicateImagesRemoverApplication(logger)
    app.run()

    tm_end = datetime.datetime.utcnow()
    logger.info("app finished @ {}".format(tm_end - tm_begin))
