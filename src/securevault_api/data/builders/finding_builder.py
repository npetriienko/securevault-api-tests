"""Builder for Finding payloads."""

from faker import Faker

from securevault_api.models.finding import Finding, Severity


class FindingBuilder:
    """Generate valid, independent Finding payloads; accept overrides for focused tests.

    asset_id is required: a finding cannot exist without a parent asset, and the
    API validates it, so tests must pass the id of an asset they actually created.
    """

    def __init__(self, faker: Faker) -> None:
        self.faker = faker

    def build(self, asset_id: str, **overrides) -> Finding:
        values = {
            "title": self.faker.sentence(nb_words=4).rstrip("."),
            "severity": self.faker.random_element(list(Severity)),
            "asset_id": asset_id,
            "description": self.faker.sentence(),
            "cve_id": None,
        }
        values.update(overrides)
        return Finding(**values)
