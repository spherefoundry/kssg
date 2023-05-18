import os
import re
from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class PostFilenameParser:
    year: int
    month: int
    day: int
    slug: str

    @classmethod
    def parse(cls, name: str) -> Optional['PostFilenameParser']:
        pattern = r"^(\d{4})-(\d{2})-(\d{2})-([\w\d-]+)$"
        match = re.fullmatch(pattern, name)
        if not match:
            return None

        return cls(
            year=int(match.group(1)),
            month=int(match.group(2)),
            day=int(match.group(3)),
            slug=match.group(4)
        )

    @property
    def link(self) -> str:
        return os.path.join(
            '/',
            str(self.year).zfill(4),
            str(self.month).zfill(2),
            str(self.day).zfill(2),
            str(self.slug)
        )

    @property
    def date(self) -> date:
        return date(year=self.year, month=self.month, day=self.day)