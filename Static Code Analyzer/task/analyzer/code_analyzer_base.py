# code_analyzer_base.py module
"""Definition of the interface for static code analysis.
Implementation: code_analyzer.py."""

import enum
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Set, Optional
from dataclasses import dataclass


class IssueType(enum.Enum):
    """ Enum class for typesafe Issue codes. """
    S001 = "Too long"
    S002 = "Indentation is not a multiple of four"
    S003 = "Unnecessary semicolon"
    S004 = "At least two spaces required before inline comments"
    S005 = "TODO found"
    S006 = "More than two blank lines preceding a code line"


@dataclass(frozen=True)
class CodeIssue:
    """Data class that wraps all relevant information of an issue detected in static code analysis.

    Attributes:
        path:    The path of the analyzed file.
        line:    The code line this issue occurred on.
        type:    The :class:`IssueType` of the issue.
    """
    path: str
    line: int
    type: IssueType

class BaseCodeAnalyzer(ABC):
    """ Definition of an interface for static code analysis of python scripts.
    
    Attributes:
        path:                   The path to the file being analyzed.
        codebase:               The codebase that is being analyzed.
        total_lines:            The number of lines in the codebase.
        single_line_analyzer:    A static dictionary mapping each :class:`IssueType` that can be detected from a single
                                line to its analyzing function. 
        bulk_analyzer:           A static dictionary mapping each :class:`IssueType` that can only be detected
                                when analyzing multiple lines to its analyzing function. 
        found_issues:           A list of collected :class:`.CodeIssue` instances.
    """
    MAX_LINES = 79

    def __init__(self, path: str):
        """ Initializer, encompasses reading code from file.
        :param path: The path to the file.
        """
        self.path = path
        with open(path, "r") as file:
            self.codebase: List[str] = file.readlines()
        self.total_lines = len(self.codebase)
        self.found_issues: List[CodeIssue] = []
        self.single_line_analyzer: Dict[IssueType, callable] = {
            IssueType.S001: self.long_line,
            IssueType.S002: self.indentation,
            IssueType.S003: self.semicolon,
            IssueType.S004: self.missing_spaces,
            IssueType.S005: self.todo,
        }
        self.bulk_analyzer: Dict[IssueType, callable] = {
            IssueType.S006: self.blank_lines,
        }

    @classmethod
    def has_inline_comment(cls, line: str) -> bool:
        """ Return true if input line contains an inline comment.
         :param line: The line to check.
         :return: :const:`True` if line contains inline comment.
         """
        comment_split = line.split("#")
        return len(comment_split) > 1 and comment_split[0].strip()

    @classmethod
    def split_at_comment(cls, line: str) -> Tuple[str, str]:
        """ Split an input line into code and comment.
        :param line: The line to split.
        :return: A :py:type:`tuple` containing the code and comment. """
        if '#' in line:
            split_at_first = line.split("#", maxsplit=2)
            return split_at_first[0], split_at_first[1]
        else:
            return line, ""

    @abstractmethod
    def long_line(self, line_no: int, line: str) -> Optional[CodeIssue]:
        """ Create a Style Issue if the input line exceeds the 79 characters limit.
        :param line: The line to analyze.
        :param line_no: The number of the line to analyze.
        :return: A :class:`CodeIssue` object or :const:`None`.
        """
        pass

    @abstractmethod
    def indentation(self, line_no: int, line: str) -> Optional[CodeIssue]:
        """ Create a Style Issue if the input line is not indented by a multiple of four.
        :param line: The line to analyze.
        :param line_no: The number of the line to analyze.
        :return: A :class:`CodeIssue` or :const:`None`.
        """
        ...

    @abstractmethod
    def semicolon(self, line_no: int, line: str) -> Optional[CodeIssue]:
        """ Create a Style Issue if the input line contains an unnecessary semicolon after a statement.
        :param line: The line to analyze.
        :param line_no: The number of the line to analyze.
        :return: A :class:`CodeIssue` or :const:`None`.
        """
        ...

    @abstractmethod
    def missing_spaces(self, line_no: int, line: str) -> Optional[CodeIssue]:
        """ Create a Style Issue if the input line contains an inline comment which is not separated with two spaces.
        :param line_no: The line to analyze.
        :return: A :class:`CodeIssue` or :const:`None`.
        """
        ...

    @abstractmethod
    def todo(self, line_no: int, line: str) -> Optional[CodeIssue]:
        """ Create a Style Issue if the input line contains a 'TODO' comment (any case).
        :param line: The line to analyze.
        :param line_no: The number of the line to analyze.
        :return: A :class:`CodeIssue` or :const:`None`.
        """
        ...

    @abstractmethod
    def blank_lines(self) -> List[CodeIssue]:
        """ Create a Style Issue for every code line preceded by more than two empty lines.
         :return: A list of :class:`CodeIssue` objects for every code line preceded by more than two empty lines."""
        ...

    def analyze(self, issue_types: Set[IssueType]):
        """ Initialize search for issues of the given types.
        Found issues are collected in ``found_issues``.
        :param issue_types: The :class:`IssueType` to analyze.
        """
        line_by_line_types: Set[IssueType] = issue_types.intersection(self.single_line_analyzer.keys())
        bulk_types = issue_types.intersection(self.bulk_analyzer.keys())
        for line_no, line in enumerate(self.codebase, start = 1):
            for issue_type in line_by_line_types:
                issue = self.single_line_analyzer[issue_type](line_no, line)
                if issue:
                    self.found_issues.append(issue)
        for issue_type in bulk_types:
            self.found_issues.extend(self.bulk_analyzer[issue_type]())


    def get_issues(self) -> List[CodeIssue]:
        """ Return a list of all :attr:`found_issues`, sorted by their line number and IssueCode
         :return: A sorted list of :class:`CodeIssue` objects.
         """
        self.found_issues.sort(key=lambda i: (i.line, i.type.name))
        return self.found_issues
