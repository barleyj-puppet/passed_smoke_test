import sys

from logbook import Logger, LoggerGroup, StreamHandler
from logbook import WARNING, DEBUG

logger_group = LoggerGroup()
logger_group.level = WARNING
StreamHandler(sys.stdout).push_application()

