from enum import Enum


class SafetyLevel(str, Enum):
    safe = "safe"
    caution = "caution"
    danger = "danger"
    unknown = "unknown"
