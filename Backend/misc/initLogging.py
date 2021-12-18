import logging
import os


def init_logging() -> None:
    def make_logger(log_name: str) -> None:
        logger = logging.getLogger(log_name)
        logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler(
            filename=f"./Logs/Backend/{log_name}.log",
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Initialize formatter
    formatter = logging.Formatter("%(asctime)s - %(levelname)s : %(message)s")

    # Initialize logging for incoming requests
    make_logger("requests")
    work = os.getcwd()
    print(work)
    for root, dirs, files in os.walk(work):
        level = root.replace(work, "").count(os.sep)
        indent = " " * 4 * (level)
        print("{}{}/".format(indent, os.path.basename(root)))
        subindent = " " * 4 * (level + 1)
        for f in files:
            print("{}{}".format(subindent, f))

    # Initialize logging for external api requests
    make_logger("bungieApi")
    make_logger("elevatorApi")

    # Initialize logging for Background Events
    make_logger("backgroundEvents")
    make_logger("updateActivityDb")
