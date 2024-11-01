# code_analyzer_base.py module
"""Definition of the interface for static code analysis.
Implementation in code_analyzer.py."""
import ast
import enum
import re
import typing
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Tuple, Set, Optional, Type, Callable, Any


class IssueType(enum.Enum):
    """ Enum class for typesafe Issue codes. """
    S001 = "Too long"
    S002 = "Indentation is not a multiple of four"
    S003 = "Unnecessary semicolon"
    S004 = "At least two spaces required before inline comments"
    S005 = "TODO found"
    S006 = "More than two blank lines preceding a code line"
    S007 = "Too many spaces after {0}"
    S008 = "Class name {0} should use CamelCase"
    S009 = "Function name {0} should use snake_case"
    S010 = "Argument name {0} should be written in snake_case"
    S011 = "Variable {0} should be written in snake_case"
    S012 = "Default argument value is mutable"

@dataclass(frozen=True)
class CodeIssue:
    """Data class that wraps all relevant information of an issue detected in static code analysis.

    Attributes:
        path:    The path of the analyzed file.
        line:    The code line this issue occurred on.
        type:    The :class:`IssueType` of the issue.
        str_arg: Optional string argument for the message string.
    """
    path: str
    line: int
    type: IssueType
    str_arg: Optional[str] = None

    def has_msg_arg(self) -> bool:
        return self.str_arg is not None

class BaseCodeAnalyzer(ABC):
    """ Definition of an interface for static code analysis of python scripts.
    
    Attributes:
        path:                   The path to the file being analyzed.
        codebase:               The code being analyzed as a single string.
        single_line_analyzer:   A static dictionary mapping `IssueType`s that are recognized from
                                a single code line to their analyzing functions.
        bulk_analyzer:          A static dictionary mapping `IssueType`s that are recognized
                                while parsing multiple code lines to their analyzing function.
        ast_analyzers:          A static dictionary mapping `IssueType`s that are recognized while
                                inspecting nodes of the abstract syntax tree to their analyzing function.
        found_issues:           A list of collected :class:`.CodeIssue` instances.
    """
    MAX_LINES = 79
    snake_violation_pattern = re.compile("((\w*[A-Z]+\w*)+)")
    camel_violation_pattern = re.compile("((?!([A-Z]+[a-z]+))|\w+_\w+)")
    mutable_types = [ast.List, ast.Set, ast.Dict]

    def __init__(self, path: str):
        """ Initializer, encompasses reading code from file.
        :param path: The path to the file.
        """
        self.path = path
        with open(path, "r") as file:
            self.codebase: str = file.read()
        self.found_issues: List[CodeIssue] = []
        self.single_line_analyzer: Dict[IssueType, Callable[[int, str], Optional[CodeIssue]]] = {
            IssueType.S001: self.long_line,
            IssueType.S002: self.indentation,
            IssueType.S003: self.semicolon,
            IssueType.S004: self.missing_spaces,
            IssueType.S005: self.todo,
        }
        self.bulk_analyzer: Dict[IssueType, Callable[[], List[CodeIssue]]] = {
            IssueType.S006: self.blank_lines,
        }
        self.ast_analyzers: Dict[Type[ast.AST], Dict[
                                IssueType, Callable[[Any], Optional[CodeIssue]]]] = {
            ast.ClassDef: {
                IssueType.S007: self.too_many_spaces,
                IssueType.S008: self.camel_case_check,
            },
            ast.FunctionDef: {
                IssueType.S007: self.too_many_spaces,
                IssueType.S009: self.snake_case_fct,
                IssueType.S010: self.snake_case_args,
                IssueType.S012: self.mutable_default,
            },
            ast.Assign: {
                IssueType.S011: self.snake_case_var
            }
        }

    @classmethod
    def is_mutable_type(cls, var: Any) -> bool:
        return type(var) in cls.mutable_types

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
            split_at_first: List[str] = line.split('#', maxsplit=2)
            return split_at_first[0], split_at_first[1]
        else:
            return line, ""

    #..........................
    # Abstract analyzer methods
    #..........................
    # S001
    @abstractmethod
    def long_line(self, line_no: int, line: str) -> Optional[CodeIssue]:
        """ Create a Style Issue if the input line exceeds the 79 characters limit.
        :param line: The line to analyze.
        :param line_no: The number of the line to analyze.
        :return: A :class:`CodeIssue` object or :const:`None`.
        """
        pass

    # S002
    @abstractmethod
    def indentation(self, line_no: int, line: str) -> Optional[CodeIssue]:
        """ Create a Style Issue if the input line is not indented by a multiple of four.
        :param line: The line to analyze.
        :param line_no: The number of the line to analyze.
        :return: A :class:`CodeIssue` or :const:`None`.
        """
        ...

    # S003
    @abstractmethod
    def semicolon(self, line_no: int, line: str) -> Optional[CodeIssue]:
        """ Create a Style Issue if the input line contains an unnecessary semicolon after a statement.
        :param line: The line to analyze.
        :param line_no: The number of the line to analyze.
        :return: A :class:`CodeIssue` or :const:`None`.
        """
        ...

    # S004
    @abstractmethod
    def missing_spaces(self, line_no: int, line: str) -> Optional[CodeIssue]:
        """ Create a Style Issue if the input line contains an inline comment which is not separated with two spaces.
        :param line: The line to analyze.
        :param line_no: The line to analyze.
        :return: A :class:`CodeIssue` or :const:`None`.
        """
        ...

    # S005
    @abstractmethod
    def todo(self, line_no: int, line: str) -> Optional[CodeIssue]:
        """ Create a Style Issue if the input line contains a 'TODO' comment (any case).
        :param line: The line to analyze.
        :param line_no: The number of the line to analyze.
        :return: A :class:`CodeIssue` or :const:`None`.
        """
        ...

    # S006
    @abstractmethod
    def blank_lines(self) -> List[CodeIssue]:
        """ Create a Style Issue for every code line preceded by more than two empty lines.
         :return: A list of :class:`CodeIssue` objects for every code line preceded by more than two empty lines."""
        ...

    # S007
    @abstractmethod
    def too_many_spaces(self, node: ast.ClassDef | ast.FunctionDef)-> Optional[CodeIssue]:
        """ Create a Style Issue if the class or function definition keyword is followed by more than one space.
        :param node: The class or function definition node that is being analyzed
        :return: A :class:`CodeIssue` or :const:`None`.
        """
        ...

    # S008
    @abstractmethod
    def camel_case_check(self, node: ast.ClassDef)-> Optional[CodeIssue]:
        """ Create a Style Issue if class name of the class definition is not in CamelCase.
        :param node: The class definition node that is being analyzed.
        :return: A :class:`CodeIssue` or :const:`None`.
        """
        ...

    # S009
    @abstractmethod
    def snake_case_fct(self, node: ast.FunctionDef)-> Optional[CodeIssue]:
        """ Create a Style Issue if the function name in the function definition is not in snake_case.
        :param node: The function definition node that is being analyzed.
        :return: A :class:`CodeIssue` or :const:`None`.
        """
        ...

    # S010
    @abstractmethod
    def snake_case_args(self, node: ast.FunctionDef)-> List[CodeIssue]:
        """ Return a Style Issue for each argument in the function definition that is not in snake_case.
        :return: A list of :class:`CodeIssue` objects or an empty list.
        """
        ...

    # S011
    @abstractmethod
    def snake_case_var(self, node: ast.Assign) -> List[CodeIssue]:
        """ Return a Style Issue for each variable name in the assignment that is not in snake_case.
        :return: A list of :class:`CodeIssue` objects or an empty list.
        """
        ...

    # S012
    @abstractmethod
    def mutable_default(self, node: ast.FunctionDef)-> Optional[CodeIssue]:
        """ Return a Style Issue if the function definition contains
            a mutable default value (list, dictionary, or set) .
        :return: A :class:`CodeIssue` or :const:`None`.
        """
        ...

    # ....................
    # Coordination methods
    # ....................
    def analyze(self, requested_checks: Set[IssueType]):
        """ Initialize search for all possible IssueTypes.
        :param requested_checks: The set of :class:`IssueType` to analyze.
        """
        self.line_by_line_analysis(requested_checks)
        self.bulk_analysis(requested_checks)
        self.ast_node_analysis(requested_checks)

    def bulk_analysis(self, requested_checks: Set[IssueType]):
        """ Initialize search for IssueTypes that need to scan the whole file.
        Found issues are collected in ``found_issues``.
        :param requested_checks: The set of :class:`IssueType` to analyze.
        """
        selected_bulk_issues: Set[IssueType] = requested_checks.intersection(self.bulk_analyzer.keys())
        for issue_type in selected_bulk_issues:
            self.found_issues.extend(self.bulk_analyzer[issue_type]())

    def line_by_line_analysis(self, requested_checks: Set[IssueType]):
        """ Search codebase line by line for IssueTypes that are recognized from single code lines.
        Found issues are collected in ``found_issues``.
        :param requested_checks: The set of :class:`IssueType` to analyze.
        """
        selected_line_issues: Set[IssueType] = requested_checks.intersection(self.single_line_analyzer.keys())
        for line_no, line in enumerate(self.codebase.splitlines(), start=1):
            for issue_type in selected_line_issues:
                issue = self.single_line_analyzer[issue_type](line_no, line)
                if issue:
                    self.found_issues.append(issue)

    def ast_node_analysis(self, requested_checks: Set[IssueType]):
        """ Scan abstract syntax tree for nodes with possible issues and initiate their analysis.
        :param requested_checks: The set of :class:`IssueType` to analyze.
        """
        # print(f"AST query types: {query_types}")
        tree = ast.parse(self.codebase)
        for node in ast.walk(tree):
            # remember parent: relevant to filter out non-snake-case assignments of constants
            for child in ast.iter_child_nodes(node):
                child.parent = node
            # check nodes that have IssueTypes attached to them in the ast.analyzer dictionary
            node_type : Type[ast.AST] = type(node)
            if node_type in self.ast_analyzers:
                self.check_node(node, requested_checks)

    def check_node(self, node: ast.AST, requested_checks: Set[IssueType]):
        """ Search for the issues of an ast node. Found issues are collected in ``found_issues``.
        :param node: The node that is being analyzed.
        :param requested_checks: The set of :class:`IssueType` to analyze.
        """
        # filter IssueTypes according to user selection in issue_types
        node_analyzers: dict[IssueType, callable] = self.ast_analyzers[type(node)]
        selected_node_issues: Set[IssueType] = requested_checks.intersection(node_analyzers.keys())
        # analyze node for each IssueType and append issues to found_issues
        for issue_type in selected_node_issues:
            issue: CodeIssue | None | List[CodeIssue] = node_analyzers[issue_type](node)
            match issue:
                case CodeIssue():
                    self.found_issues.append(issue)
                case list():
                    self.found_issues.extend(issue)

    # Return the results
    def get_issues(self) -> List[CodeIssue]:
        """ Return a list of all :attr:`found_issues`, sorted by their line number and IssueCode
         :return: A sorted list of :class:`CodeIssue` objects.
         """
        self.found_issues.sort(key=lambda i: (i.line, i.type.name))
        return self.found_issues
