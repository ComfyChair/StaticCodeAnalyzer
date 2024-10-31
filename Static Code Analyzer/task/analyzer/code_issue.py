import enum
from dataclasses import dataclass

class IssueType(enum.Enum):
    """Enum class for typesafe Issue codes
    referencing the analyzer method as value"""
    S001 = "Too long"
    S002 = "Indentation is not a multiple of four"
    S003 = "Unnecessary semicolon"
    S004 = "At least two spaces required before inline comments"
    S005 = "TODO found"
    S006 = "More than two blank lines preceding a code line"

@dataclass(frozen=True)
class CodeIssue:
    """Data class that wraps all relevant information of a Code Issue."""
    line: int
    type: IssueType
