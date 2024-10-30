import enum
from dataclasses import dataclass
from code_analyzer import CodeAnalyzer

class IssueType(enum.Enum):
    """Enum class for typesafe Issue codes
    referencing the analyzer method as value"""
    S001 = (CodeAnalyzer.long_lines, "Too long")
    S002 = (CodeAnalyzer.indentation, "Indentation is not a multiple of four")
    S003 = (CodeAnalyzer.semicolon, "Unnecessary semicolon")
    S004 = (CodeAnalyzer.missing_spaces, "At least two spaces required before inline comments")
    S005 = (CodeAnalyzer.todo, "TODO found")
    S006 = (CodeAnalyzer.blank_lines, "More than two blank lines preceding a code line")

@dataclass(frozen=True)
class CodeIssue:
    """Data class that wraps all relevant information of a Code Issue."""
    line: int
    type: IssueType
    msg: str