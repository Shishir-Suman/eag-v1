import logging
import sys

def configure_logger(level=logging.INFO):
    """
    Configures a logger with ANSI color-coded stages for terminal output.

    Args:
        level (int): Logging level (default: logging.INFO).

    Returns:
        logging.Logger: Configured logger instance.
    """
    # Bright & distinct ANSI color codes for each stage
    stage_colors = {
        'AGENT':     '\033[1;95m',  # Bright Magenta
        'MEMORY':    '\033[1;94m',  # Bright Blue
        'PERCEPTION':'\033[1;96m',  # Bright Cyan
        'ACTION':    '\033[1;92m',  # Bright Green
        'DECISION':  '\033[1;93m',  # Bright Yellow
        'DEFAULT':   '\033[1;97m'   # Bright White
    }
    reset = '\033[0m'

    class StageFormatter(logging.Formatter):
        def format(self, record):
            stage = getattr(record, 'stage', 'DEFAULT').upper()
            color = stage_colors.get(stage, stage_colors['DEFAULT'])
            stage_tag = f"{color}[{stage}]{reset}"
            base_msg = super().format(record)
            return f"{stage_tag} {base_msg}"

    # Full log format (excluding stage which is added manually above)
    log_format = "%(asctime)s | %(levelname)-8s | %(module)s.%(funcName)s() | %(message)s"
    formatter = StageFormatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")

    logger = logging.getLogger()
    logger.setLevel(level)

    # Remove existing handlers to prevent duplicate log messages
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Output to stdout (can be changed to stderr if needed)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger
