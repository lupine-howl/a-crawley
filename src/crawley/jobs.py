"""Simple in-module job status for panel UX."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

JobStatus = Literal["idle", "busy", "done", "error"]


@dataclass
class JobState:
    status: JobStatus = "idle"
    message: str = ""
    summary: str = ""
    details: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "message": self.message,
            "summary": self.summary,
            "details": self.details,
        }
