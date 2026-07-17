"""Finding model — a security problem associated with a parent asset.

A finding cannot exist without a parent asset (asset_id). Field names
mirror the API contract.
"""

from dataclasses import dataclass
from enum import Enum


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
    severity: Severity
    asset_id: str
    description: str | None = None
    cve_id: str | None = None
    # Server-assigned: present on responses, not sent on create.
    id: str | None = None
    status: FindingStatus | None = None
    org_id: str | None = None

    def to_payload(self):
        """Build the request body for POST /findings (create fields only)."""
        return {
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
            "asset_id": self.asset_id,
            "cve_id": self.cve_id,
        }
