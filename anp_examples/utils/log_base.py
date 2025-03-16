import logging
import logging.handlers
import os
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class ColoredFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[94m",  # Blue
        "INFO": "\033[92m",  # Green
        "WARNING": "\033[93m",  # Yellow
        "ERROR": "\033[91m",  # Red
        "CRITICAL": "\033[95m",  # Magenta
        "RESET": "\033[0m",  # Reset
    }

    def format(self, record):
        levelname = record.levelname
        message = super().format(record)
        color = self.COLORS.get(levelname, self.COLORS["RESET"])
        return color + message + self.COLORS["RESET"]


def get_project_name():
    """
    Extract project name from the log file path or use the directory name as fallback.
    Returns:
        str: Project name
    """
    # Try to get from environment variable first
    log_file = os.getenv("LOG_FILE_PATH", "")
    if log_file:
        # Extract project name from log file path
        base_name = os.path.basename(log_file)
        project_name = base_name.split(".")[0]  # Remove extension
        if project_name:
            return project_name

    # Fallback: use the name of the project directory
    project_dir = os.path.basename(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    return project_dir


def setup_logging(level=logging.INFO):
    # Get project name
    project_name = get_project_name()

    # 获取日志文件路径，如果是mac电脑，则使用当前路径的父路径
    if os.uname().sysname == "Darwin":  # macOS
        log_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            f"{project_name}.log",
        )
    else:
        log_file = os.getenv("LOG_FILE_PATH", f"/var/log/did-server/{project_name}.log")

    log_dir = os.path.dirname(log_file)

    try:
        # 如果目录不存在，创建目录并设置权限
        if not os.path.exists(log_dir):
            os.system("sudo mkdir -p " + log_dir)
            os.system(
                f"sudo chown -R {os.getenv('USER')}:{os.getenv('USER')} " + log_dir
            )
        os.makedirs(log_dir, exist_ok=True)
    except Exception as e:
        print(f"Error setting up log directory: {e}")
        # 如果失败，使用备用的日志目录
        log_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs"
        )
        os.makedirs(log_dir, exist_ok=True)

    # 生成日志文件名（包含日期）
    log_file = os.path.join(
        log_dir, f"{project_name}_{datetime.now().strftime('%Y%m%d')}.log"
    )

    # 获取根日志记录器
    logger = logging.getLogger()
    logger.setLevel(level)

    # 清除现有的处理器
    logger.handlers.clear()

    # 配置带颜色的控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    colored_formatter = ColoredFormatter(
        "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s\n"
    )
    console_handler.setFormatter(colored_formatter)
    logger.addHandler(console_handler)

    # 配置文件处理器，使用相同的格式（但不带颜色）
    file_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=30,
        encoding="utf-8",
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(level)
    logger.addHandler(file_handler)

    # 防止日志消息向上传播到根日志器
    logger.propagate = False

    return logger


# 为了向后兼容，保留set_log_color_level函数，但让它调用setup_logging
def set_log_color_level(level):
    return setup_logging(level)
