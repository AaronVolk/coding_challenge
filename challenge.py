from validator import Validator
import sys
import logging
from config import LOG_LEVEL


def main():
    logging.basicConfig(
        level=LOG_LEVEL,
        format="%(name)s:%(levelname)s - %(message)s"
    )
    logger = logging.getLogger("Challenge")

    if len(sys.argv) < 2:
        logger.info(f"Usage: {sys.argv[0]} <file>")
        return

    filename = sys.argv[1]

    try:
        validator = Validator(filename)
    except Exception:
        logger.critical("Unexpected error:", exc_info=True)
        return

    if validator.data is None:
        logger.critical(f"Invalid file {filename}")
        return

    error = validator.validate()

    if error is not None:
        logger.info(
            f"Discrepancy found at {error.time} seconds:"
            f"\nPotentiometer position: {error.pot}°"
            f"\nEncoder position: {error.encoder}°"
        )
    else:
        logger.info(f"No discrepancy found in log {filename}")


if __name__ == "__main__":
    main()