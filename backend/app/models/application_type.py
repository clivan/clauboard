from enum import Enum

class ApplicationType(str, Enum):
    SERVICE = "service"
    TOOLCHAIN = "toolchain"
    INFRASTRUCTURE = "infrastructure"