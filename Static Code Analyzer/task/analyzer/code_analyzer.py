# code_analyzer.py module
"""Functionality for running static code analysis of python scripts."""
import ast
import collections
import os.path
import argparse
import re
from typing import List, Optional, Set, Tuple, Any, Type
from typing_extensions import override

from code_analyzer_base import BaseCodeAnalyzer, IssueType, CodeIssue


class CodeAnalyzer(BaseCodeAnalyzer):
    """ Implementation of static code analysis methods. Inherits from BaseCodeAnalyzer. """

    # S001
    @override
    def long_line(self, line_no: int, line: str) -> Optional[CodeIssue]:
        """ Return a Style Issue if the input line exceeds the 79 characters limit.
        :param line: The line to analyze.
        :param line_no: The number of the line to analyze.
        :return: A :class:`CodeIssue` of Type S001 or :const:`None`.
        """
        if len(line) > self.MAX_LINES:
            return CodeIssue(self.path, line_no, IssueType.S001)

    # S002
    @override
    def indentation(self, line_no: int, line: str) -> Optional[CodeIssue]:
        """ Return a Style Issue if the input line is not indented by a multiple of four.
        :param line: The line to analyze.
        :param line_no: The number of the line to analyze.
         :return: A :class:`CodeIssue` of Type S002 or :const:`None`.
         """
        if not line.isspace() and (len(line) - len(line.lstrip())) % 4 != 0:
            return CodeIssue(self.path, line_no, IssueType.S002)

    # S003
    @override
    def semicolon(self, line_no: int, line: str) -> Optional[CodeIssue]:
        """ Return a Style Issue if the input line contains an unnecessary semicolon after a statement.
        :param line: The line to analyze.
        :param line_no: The number of the line to analyze.
        :return: A :class:`CodeIssue` of Type S003 or :const:`None`.
        """
        code, comment = super().split_at_comment(line)
        if code.strip().endswith(';'):
            return CodeIssue(self.path, line_no, IssueType.S003)

    # S004
    @override
    def missing_spaces(self, line_no: int, line: str) -> Optional[CodeIssue]:
        """ Return a Style Issue if the input line contains inline comment which is not separated with two spaces.
        :param line: The line to analyze.
        :param line_no: The number of the line to analyze.
        :return: A :class:`CodeIssue` of Type S004 or :const:`None`.
        """
        code, comment = super().split_at_comment(line)
        has_inline_comment = super().has_inline_comment(line)
        if has_inline_comment and len(code) - len(code.rstrip()) < 2:
            # less than 2 spaces before comment
            return CodeIssue(self.path, line_no, IssueType.S004)

    # S005
    @override
    def todo(self, line_no: int, line: str) -> Optional[CodeIssue]:
        """ Return a Style Issue if the input line contains a 'TODO' comment (any case).
        :param line: The line to analyze.
        :param line_no: The number of the line to analyze.
        :return: A :class:`CodeIssue` of Type S005 or :const:`None`.
        """
        code, comment = super().split_at_comment(line)
        if "TODO" in comment.upper():
            # we have a comment that contains a 'todo'
            return CodeIssue(self.path, line_no, IssueType.S005)

    # S006
    @override
    def blank_lines(self) -> List[CodeIssue]:
        """ Return a Style Issue for every code preceded by more than two empty lines.
        :return: The list of found :class:`CodeIssue` objects or an empty list.
        """
        found_issues: List[CodeIssue] = []
        count_blank = 0
        for line_no, line in enumerate(self.codebase.splitlines(), start=1):
            if line.strip() == "":
                count_blank += 1
            else:  # non-empty line
                if count_blank > 2:
                    found_issues.append(CodeIssue(self.path, line_no, IssueType.S006))
                count_blank = 0
        return found_issues

    # S007
    @override
    def too_many_spaces(self, node: ast.ClassDef | ast.FunctionDef) -> Optional[CodeIssue]:
        """ Return a Style Issue if the line contains a class or function definition keyword
        followed by more than one space.
        :param node: The class or function definition node that is being analyzed.
        :return: A :class:`CodeIssue` or :const:`None`.
        """
        line = ast.get_source_segment(self.codebase, node)
        pattern = re.compile(r"""
        (def|class)       # keyword
        \s{2}\s*        # 2 or more spaces
        (\w+)           # function name or class name
        """, re.VERBOSE)
        match = pattern.match(line.strip())
        if match:
            return CodeIssue(self.path, node.lineno, IssueType.S007, node.name)

    # S008
    @override
    def camel_case_check(self, node: ast.ClassDef) -> Optional[CodeIssue]:
        """ Return a Style Issue if the line contains a class name not written in CamelCase.
        :param node: The class definition node that is being analyzed.
        :return: A :class:`CodeIssue` or :const:`None`.
        """
        violation = re.match(self.camel_violation_pattern, node.name)
        if violation:
            return CodeIssue(self.path, node.lineno, IssueType.S008, node.name)

    # S009
    @override
    def snake_case_fct(self, node: ast.FunctionDef) -> Optional[CodeIssue]:
        """ Return a Style Issue if the line contains a function name not written in snake_case.
        :param node: The function definition node that is being analyzed.
        :return: A :class:`CodeIssue` or :const:`None`.
        """
        violation = re.match(self.snake_violation_pattern, node.name)
        if violation:
            return CodeIssue(self.path, node.lineno, IssueType.S009, node.name)

    # S010
    @override
    def snake_case_args(self, node: ast.FunctionDef) -> List[CodeIssue]:
        """ Return a Style Issue if the line contains a function definition
            where one or more arguments are not in snake_case.
        :param node: The function definition node whose arguments are being analyzed.
        :return: A list of :class:`CodeIssue` objects or an empty list.
        """
        violating_arg_names = []
        for arg in node.args.args:
            this_arg_name = arg.arg
            if re.match(self.snake_violation_pattern, this_arg_name):
                violating_arg_names.append(this_arg_name)
        return [CodeIssue(self.path, node.lineno, IssueType.S010, arg_name) for arg_name in violating_arg_names]

    # S011
    @override
    def snake_case_var(self, node: ast.Assign) -> List[CodeIssue]:
        """ Return a Style Issue if the line contains a variable definition,
            where the variable is not in snake_case.
        :param node: The assignment node that is being analyzed.
        :return: A list of :class:`CodeIssue` objects or an empty list.
        """

        is_value_mutable = node.value in self.mutable_types
        if is_value_mutable or type(node.parent) is ast.FunctionDef:
            violating_var_names = []
            for variable in node.targets:
                match variable:
                    case ast.Name():
                        variable: ast.Name
                        this_var_name : str = variable.id
                        if re.match(self.snake_violation_pattern, this_var_name):
                            violating_var_names.append(this_var_name)
                    case list() | tuple():
                        variable: collections.Iterable
                        for content in variable:
                            this_inner_name: str = content.id
                            if re.match(self.snake_violation_pattern, this_inner_name):
                                violating_var_names.append(this_inner_name)
            return [CodeIssue(self.path, node.lineno, IssueType.S011, var_name) for var_name in violating_var_names]

    # S012
    @override
    def mutable_default(self, node: ast.FunctionDef) -> Optional[CodeIssue]:
        """ Return a Style Issue if the line contains a function definition
            where a default value is mutable (list, dictionary, or set) .
        :param node: The function definition node whose argument default values are being analyzed.
        :return: A :class:`CodeIssue` or :const:`None` objects or an empty list.
        """
        defaults = node.args.defaults
        for default in defaults:
            if self.is_mutable_type(default):
                return CodeIssue(self.path, node.lineno, IssueType.S012)


def print_issues(issues: List[CodeIssue]):
    """ Print the provided list of issues.
    :param issues: The list of issues to print.
    """
    for issue in issues:
        if issue.str_arg:
            arg = f"'{issue.str_arg}'"
            print(f"{issue.path}: Line {issue.line}: {issue.type.name} {issue.type.value.format(arg)}")
        else:
            print(f"{issue.path}: Line {issue.line}: {issue.type.name} {issue.type.value}")

def analyze_single(path: str, issue_types: Set[IssueType]):
    """ Analyze a single .py file.
    :param issue_types: The list of :class:IssueType that should be checked.
    :param path: The path of the file to analyze.
    """
    analyzer = CodeAnalyzer(path)
    analyzer.analyze(issue_types)
    print_issues(analyzer.get_issues())

def analyze_multi(directory: str, issue_types: Set[IssueType]):
    """ Analyze all .py files in the given directory.
    :param issue_types: The list of :class:IssueType that should be checked.
    :param directory: The path to the directory to analyze.
    """
    issues: List[CodeIssue] = []
    for root, dirs, filenames in os.walk(directory, followlinks=True):
        for filename in filenames:
            if filename.endswith(".py"):
                file = os.path.join(root, filename)
                analyzer = CodeAnalyzer(file)
                analyzer.analyze(issue_types)
                issues.extend(analyzer.get_issues())
    issues.sort(key=lambda issue: issue.path)
    print_issues(issues)


def filter_issue_types(exclude_arg: str) -> Set[IssueType]:
    """ Filter all available IssueTypes by a list of codes and return the resulting set.

    :param exclude_arg: String of the form "S007, S009, S002" or similar representing a list of issue codes
            that should not be checked.
    :return:
    """
    issue_types: Set[IssueType] = set(IssueType)
    if exclude_arg:
        exclude_list: List[str] = exclude_arg.split(',')
        for exclude_str in exclude_list:
            issue_type_name : str = exclude_str.strip().upper()
            try:
                to_exclude: IssueType = IssueType[issue_type_name]
                print(f"Excluding issue type {to_exclude.name}")
                issue_types.remove(to_exclude)
            except KeyError:
                print(f"Invalid argument: There is no issue type with code {exclude_str.strip()}")
        print()
    return issue_types


def main():
    """ Main method. """
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--exclude", required=False,
                        help='exclude IssueTypes by providing a list of their codes, e.g. -- exclude "S001,S010,S006"')

    issue_types = filter_issue_types(parser.parse_args().exclude)
    path: str = parser.parse_args().path
    if os.path.isfile(path) and path.endswith(".py"):
        analyze_single(path, issue_types)
    elif os.path.isdir(path):
        analyze_multi(path, issue_types)
    else:
        print(f"Path '{path}' does not contain a valid .py script")


if __name__ == '__main__':
    main()
