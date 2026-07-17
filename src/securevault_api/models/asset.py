"""Asset model — a cloud resource under SecureVault control.

Each asset is owned by an organization and may have multiple findings
attached. Field names mirror the API contract (asset_type, org_id).
"""

from dataclasses import dataclass, field
from enum import Enum


class AssetType(str, Enum):
    EC2 = "EC2"
    S3 = "S3"
    RDS = "RDS"
    LAMBDA = "Lambda"
    EKS = "EKS"
    VPC = "VPC"


@dataclass
class Asset:
    name: str
    asset_type: AssetType
    cloud_account: str
    region: str
    tags: dict = field(default_factory=dict)
    # Server-assigned: present on responses, not sent on create.
    id: str | None = None
    org_id: str | None = None

    def to_payload(self):
        """Build the request body for POST/PUT /assets (create/update fields only)."""
        return {
            "name": self.name,
            "asset_type": self.asset_type,
            "cloud_account": self.cloud_account,
            "region": self.region,
            "tags": self.tags,
        }
