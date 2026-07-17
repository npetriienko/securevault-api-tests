"""Builder for Asset payloads."""

from faker import Faker

from securevault_api.models.asset import Asset, AssetType

REGIONS = (
    "us-east-1",
    "us-east-2",
    "us-west-2",
    "eu-west-1",
    "eu-central-1",
    "ap-southeast-1",
    "ap-northeast-1",
)


class AssetBuilder:
    """Generate valid, independent Asset payloads; accept overrides for focused tests."""

    def __init__(self, faker: Faker) -> None:
        self.faker = faker

    def build(self, **overrides) -> Asset:
        values = {
            "name": f"{self.faker.word()}-{self.faker.random_int(1, 9999)}",
            "asset_type": self.faker.random_element(list(AssetType)),
            "cloud_account": self.faker.numerify("############"),
            "region": self.faker.random_element(REGIONS),
            "tags": {"env": self.faker.random_element(("dev", "staging", "prod"))},
        }
        values.update(overrides)
        return Asset(**values)
