from validator import Validator
from sys import argv
import logging
import logging.handlers
from config import LOG_LEVEL


def main():
    logging.basicConfig(level=LOG_LEVEL, format="%(name)s:%(levelname)s - %(message)s")
    logger = logging.getLogger("Challenge")

    try:
        validator = Validator(argv[1])
        if validator.data is None:
            logger.critical(f"Invalid file {argv[1]}")
            exit()
    except IndexError:
        logger.info(f"usage: {argv[0]} <file>")
        exit()
    except:
        logger.critical(f"unexpected error:", exc_info=True)
        exit()

    if (error := validator.validate()) is not None:
        logger.info(
            f"discrepancy found in sensor readings at {error.time} seconds:"
            f"\npotentiometer reports shaft position: {error.pot}°\nencoder reports shaft position: {error.encoder}°"
        )
    else:
        logger.info(f"no discrepancy found in log {argv[1]}")


if __name__ == "__main__":
    main()
