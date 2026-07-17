"""Asset model — a cloud resource under SecureVault control.

Each asset is owned by an organization and may have multiple findings
attached.
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
    type: AssetType
    cloud_account: str
    region: str
    organization: str
    tags: dict = field(default_factory=dict)
