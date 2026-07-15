"""DIY projects lite — local project notes → LLM next steps."""

from __future__ import annotations

from crawley.data.paths import DIY_DIR
from crawley.modules.contract import ModuleKind, ModuleMeta
from crawley.modules.notes_lite import NotesLiteModule

NOTES_DIR = DIY_DIR


class DiyModule(NotesLiteModule):
    meta = ModuleMeta(
        id="diy",
        title="DIY",
        kind=ModuleKind.LIVE,
        nav_order=60,
        description="Local project notes with LLM next-steps (manual action only).",
    )
    default_notes = (
        "# Shelf repair\n"
        "- Measure shelf brackets\n"
        "- Buy wood screws\n"
        "- Sand and refinish weekend"
    )
    system_attr = "diy_system"
    header_attr = "diy_user_header"
    busy_message = "Planning next steps…"
    done_message = "Done — next steps ready."

    def __init__(self) -> None:
        self.notes_dir = NOTES_DIR
        super().__init__()
