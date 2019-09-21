import sys

from dupfilesremover.app import DuplicateImagesRemoverApplication

from loguru import logger


if __name__ == "__main__":
    logger.remove()
    logger.add(sys.stderr, format="{time} {level} {message}", level="DEBUG")

    logger.debug("DEBUG")
    logger.warning("WARNING")

    app = DuplicateImagesRemoverApplication(logger)
    app.run()

    logger.info("app finished")
