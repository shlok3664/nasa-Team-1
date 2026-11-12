"""Metadata describing an acquired scientific dataset."""

import re
from dataclasses import dataclass

_CHECKSUM_PATTERN = re.compile(r"^[a-fA-F0-9]+$")


@dataclass(frozen=True, slots=True)
class DatasetMetadata:
    """Describes the identity and technical properties of a dataset."""

    title: str
    description: str = ""
    data_format: str | None = None
    license_id: str | None = None
    file_size_bytes: int | None = None
    checksum_sha256: str | None = None
    keywords: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError("title must be a non-empty string")

        if not isinstance(self.description, str):
            raise TypeError("description must be a string")

        for field_name, value in (
            ("data_format", self.data_format),
            ("license_id", self.license_id),
        ):
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{field_name} must be a non-empty string")

        if self.file_size_bytes is not None:
            if isinstance(self.file_size_bytes, bool) or not isinstance(self.file_size_bytes, int):
                raise TypeError("file_size_bytes must be an integer")

            if self.file_size_bytes < 0:
                raise ValueError("file_size_bytes cannot be negative")

        if self.checksum_sha256 is not None:
            if not isinstance(self.checksum_sha256, str):
                raise TypeError("checksum_sha256 must be a string")

            if len(self.checksum_sha256) != 64 or not _CHECKSUM_PATTERN.fullmatch(
                self.checksum_sha256
            ):
                raise ValueError("checksum_sha256 must be a 64-character SHA-256 hex digest")

        if not isinstance(self.keywords, tuple):
            raise TypeError("keywords must be a tuple")

        if any(not isinstance(keyword, str) or not keyword.strip() for keyword in self.keywords):
            raise ValueError("keywords must contain non-empty strings")

        if len(set(self.keywords)) != len(self.keywords):
            raise ValueError("keywords must not contain duplicates")
