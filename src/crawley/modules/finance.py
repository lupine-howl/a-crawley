"""Finance/Taxes lite — local planning notes → non-advice Markdown."""

from __future__ import annotations

from crawley.data.paths import FINANCE_DIR
from crawley.modules.contract import ModuleKind, ModuleMeta
from crawley.modules.notes_lite import NotesLiteModule

NOTES_DIR = FINANCE_DIR


class FinanceModule(NotesLiteModule):
    meta = ModuleMeta(
        id="finance-taxes",
        title="Finance/Taxes",
        kind=ModuleKind.LIVE,
        nav_order=80,
        description="Personal planning notes → Markdown overview (not professional advice).",
    )
    default_notes = (
        "- Gather W-2 / interest statements\n"
        "- Review estimated quarterly payments\n"
        "- Questions for tax preparer this season"
    )
    system_attr = "finance_system"
    header_attr = "finance_user_header"
    busy_message = "Drafting planning overview…"
    done_message = "Done — planning overview ready."
    disclaimer = (
        "Not professional tax or financial advice. Personal planning only — "
        "confirm with a qualified advisor before acting."
    )

    def __init__(self) -> None:
        self.notes_dir = NOTES_DIR
        super().__init__()
