import datetime
import sys

from dupfilesremover.app import DuplicateImagesRemoverApplication

from loguru import logger


if __name__ == "__main__":
    tm_begin = datetime.datetime.utcnow()
    logger.remove()
    logger.add(sys.stderr, format="{time} {level} {message}", level="DEBUG")

    logger.debug("DEBUG")
    logger.warning("WARNING")

    app = DuplicateImagesRemoverApplication(logger)
    app.run()

    tm_end = datetime.datetime.utcnow()
    logger.info("app finished @ {}".format(tm_end - tm_begin))
