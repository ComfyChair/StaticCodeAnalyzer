from abc import ABC, abstractmethod
from pprint import pprint
from typing import List, Dict, Tuple, Set

from code_issue import IssueType, CodeIssue


class BaseCodeAnalyzer(ABC):
    MAX_LINES = 79

    def __init__(self, path: str):
        with open(path, "r") as file:
            self.code_base : List[str] = file.readlines()
        self.total_lines = len(self.code_base)
        self.found_issues : List[CodeIssue] = []
        self.single_line_methods : Dict[IssueType, callable] = {
            IssueType.S001: self.long_line,
            IssueType.S002: self.indentation,
            IssueType.S003: self.semicolon,
            IssueType.S004: self.missing_spaces,
            IssueType.S005: self.todo,
        }
        self.bulk_methods : Dict[IssueType, callable] = {
            IssueType.S006: self.blank_lines,
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
    def long_line(self, line_no: int) -> CodeIssue | None:
        """Creates a Style Issue for every line that exceeds the 79 characters limit."""
        ...

    @abstractmethod
    def indentation(self, line_no: int) -> CodeIssue | None:
        """Creates a Style Issue for every line that is not indented by a multiple of four."""
        ...

    @abstractmethod
    def semicolon(self, line_no: int) -> CodeIssue | None:
        """Creates a Style Issue for every line that contains an unnecessary semicolon after a statement."""
        ...

    @abstractmethod
    def missing_spaces(self, line_no: int) -> CodeIssue | None:
        """Creates a Style Issue for every line that contains inline comment which is not separated with two spaces."""
        ...

    @abstractmethod
    def todo(self, line_no: int) -> CodeIssue | None:
        ...

    @abstractmethod
    def blank_lines(self) -> List[CodeIssue]:
        ...

    def analyze(self, issue_types: Set[IssueType]):
        """Initializes search for issues of the given types
        :returns a list of code issues, sorted by line number"""
        line_by_line_types : Set[IssueType] = issue_types.intersection(self.single_line_methods.keys())
        bulk_types = issue_types.intersection(self.bulk_methods.keys())
        for line_no in range(self.total_lines):
            for issue_type in line_by_line_types:
                issue = self.single_line_methods[issue_type](line_no)
                if issue:
                    self.found_issues.append(issue)
        for issue_type in bulk_types:
            self.found_issues.extend(self.bulk_methods[issue_type]())


    def print_issues(self):
        self.found_issues.sort(key=lambda i: i.line)
        for issue in self.found_issues:
            print(f"Line {issue.line}: {issue.type.name} {issue.type.value}")
