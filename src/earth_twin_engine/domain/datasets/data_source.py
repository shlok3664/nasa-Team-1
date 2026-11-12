"""Scientific data source domain entity."""

import re
from dataclasses import dataclass

_SOURCE_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


@dataclass(frozen=True, slots=True)
class DataSource:
    """Identifies a scientific data provider."""

    source_id: str
    name: str
    provider: str
    description: str = ""
    homepage_url: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.source_id, str):
            raise TypeError("source_id must be a string")

        if not _SOURCE_ID_PATTERN.fullmatch(self.source_id):
            raise ValueError(
                "source_id must use lowercase letters, numbers, "
                "and underscores, starting with a letter"
            )

        for field_name, value in (
            ("name", self.name),
            ("provider", self.provider),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")

        if not isinstance(self.description, str):
            raise TypeError("description must be a string")

        if self.homepage_url is not None:
            if not isinstance(self.homepage_url, str):
                raise TypeError("homepage_url must be a string")

            if not self.homepage_url.startswith(("https://", "http://")):
                raise ValueError("homepage_url must use HTTP or HTTPS")
