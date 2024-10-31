from abc import ABC, abstractmethod
from pprint import pprint
from typing import List, Dict, Tuple

from code_issue import IssueType, CodeIssue


class BaseCodeAnalyzer(ABC):
    MAX_LINES = 79

    def __init__(self, path: str):
        with open(path, "r") as file:
            self.code_base : List[str] = file.readlines()
        self.found_issues : List[CodeIssue] = []
        self.issue_methods : Dict[str, callable] = {
            "S001": self.long_lines,
            "S002": self.indentation,
            "S003": self.semicolon,
            "S004": self.missing_spaces,
            "S005": self.todo,
            "S006": self.blank_lines,
        }

    @classmethod
    def has_inline_comment(cls, line: str) -> bool:
        comment_split = line.split("#")
        return len(comment_split) > 1 and comment_split[0].strip()

    @classmethod
    def split_at_comment(cls, line: str) -> Tuple[str, str]:
        if '#' in line:
            split_at_first = line.split("#", maxsplit= 2)
            return split_at_first[0], split_at_first[1]
        else:
            return line, ""

    @abstractmethod
    def long_lines(self, issue_type: IssueType) -> List[CodeIssue]:
        """Creates a Style Issue for every line that exceeds the 79 characters limit."""
        ...

    @abstractmethod
    def indentation(self, issue_type: IssueType) -> List[CodeIssue]:
        """Creates a Style Issue for every line that is not indented by a multiple of four."""
        ...

    @abstractmethod
    def semicolon(self, issue_type: IssueType) -> List[CodeIssue]:
        """Creates a Style Issue for every line that contains an unnecessary semicolon after a statement."""
        ...

    @abstractmethod
    def missing_spaces(self, issue_type: IssueType) -> List[CodeIssue]:
        """Creates a Style Issue for every line that contains inline comment which is not separated with two spaces."""
        ...

    @abstractmethod
    def todo(self, issue_type: IssueType) -> List[CodeIssue]:
        ...

    @abstractmethod
    def blank_lines(self, issue_type: IssueType) -> List[CodeIssue]:
        ...

    def analyze(self, types: List[IssueType]):
        """Initializes search for issues of the given types
        :returns a list of code issues, sorted by line number"""
        for issue_type in types:
            self.found_issues.extend(self.issue_methods[issue_type.name](issue_type))

    def print_issues(self):
        self.found_issues.sort(key=lambda i: i.line)
        for issue in self.found_issues:
            print(f"Line {issue.line}: {issue.type.name} {issue.type.value}")
