from enum import Enum


class ApplicationStatus(str, Enum):
    UNKNOWN = "unknown"
    NOT_INSTALLED = "not_installed"
    STOPPED = "stopped"
    RUNNING = "running"