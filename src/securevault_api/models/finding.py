"""Finding model — a security problem associated with a parent asset.

A finding cannot exist without a parent asset.
"""

from dataclasses import dataclass
from enum import Enum

from .asset import Asset


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class FindingStatus(str, Enum):
    OPEN = "open"
    MITIGATED = "mitigated"
    CLOSED = "closed"


@dataclass
class Finding:
    title: str
    description: str
    severity: Severity
    status: FindingStatus
    asset: Asset
    cve_id: str | None = None
