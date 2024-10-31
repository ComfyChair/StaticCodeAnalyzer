# code_analyzer.py module
"""Functionality for running static code analysis of python scripts."""

import os.path
import argparse
import re
from typing import List, Optional, Set

from code_analyzer_base import BaseCodeAnalyzer, IssueType, CodeIssue


class CodeAnalyzer(BaseCodeAnalyzer):
    """ Implementation of static code analysis methods. Inherits from BaseCodeAnalyzer. """

    def long_line(self, line_no: int, line: str) -> Optional[CodeIssue]:
        """ Create a Style Issue if the input line exceeds the 79 characters limit.
        :param line: The line to analyze.
        :param line_no: The number of the line to analyze.
        :return: A :class:`CodeIssue` of Type S001 or :const:`None`.
        """
        if len(line) > self.MAX_LINES:
            return CodeIssue(self.path, line_no, IssueType.S001)

    def indentation(self, line_no: int, line: str) -> Optional[CodeIssue]:
        """ Create a Style Issue if the input line is not indented by a multiple of four.
        :param line: The line to analyze.
        :param line_no: The number of the line to analyze.
         :return: A :class:`CodeIssue` of Type S002 or :const:`None`.
         """
        if not line.isspace() and (len(line) - len(line.lstrip())) % 4 != 0:
            return CodeIssue(self.path, line_no, IssueType.S002)

    def semicolon(self, line_no: int, line: str) -> Optional[CodeIssue]:
        """ Create a Style Issue if the input line contains an unnecessary semicolon after a statement.
        :param line: The line to analyze.
        :param line_no: The number of the line to analyze.
        :return: A :class:`CodeIssue` of Type S003 or :const:`None`.
        """
        code, comment = BaseCodeAnalyzer.split_at_comment(line)
        if code.strip().endswith(';'):
            return CodeIssue(self.path, line_no, IssueType.S003)

    def missing_spaces(self, line_no: int, line: str) -> Optional[CodeIssue]:
        """ Create a Style Issue if the input line contains inline comment which is not separated with two spaces.
        :param line: The line to analyze.
        :param line_no: The number of the line to analyze.
        :return: A :class:`CodeIssue` of Type S004 or :const:`None`.
        """
        code, comment = BaseCodeAnalyzer.split_at_comment(line)
        has_inline_comment = BaseCodeAnalyzer.has_inline_comment(line)
        if has_inline_comment and len(code) - len(code.rstrip()) < 2:
            # less than 2 spaces before comment
            return CodeIssue(self.path, line_no, IssueType.S004)

    def todo(self, line_no: int, line: str) -> Optional[CodeIssue]:
        """ Create a Style Issue if the input line contains a 'TODO' comment (any case).
        :param line: The line to analyze.
        :param line_no: The number of the line to analyze.
        :return: A :class:`CodeIssue` of Type S005 or :const:`None`.
        """
        code, comment = BaseCodeAnalyzer.split_at_comment(line)
        if "TODO" in comment.upper():
            # we have a comment that contains a 'todo'
            return CodeIssue(self.path, line_no, IssueType.S005)

    def too_many_spaces(self, line_no: int, line: str) -> Optional[CodeIssue]:
        """ Create a Style Issue if the line contains a class or function definition
            keyword followed by more than one space.
        :param line: The line to analyze.
        :param line_no: The number of the line to analyze.
        :return: A :class:`CodeIssue` or :const:`None`.
        """
        pattern = re.compile(r"""
        (def|class)       # keyword
        \s{2}\s*        # 2 or more spaces
        (\w+)           # function name or class name
        """, re.VERBOSE)
        match = pattern.match(line.strip())
        if match:
            name = match.groups()[1]
            return CodeIssue(self.path, line_no, IssueType.S007, name)

    def camel_case_class(self, line_no: int, line: str) -> Optional[CodeIssue]:
        class_match = re.compile(r"class\s+(\w+)\(").match(line.strip())
        if class_match:
            class_name = class_match.groups()[0]
            no_camel_match = re.compile(r"([^A-Z][a-z]+)+")
            if no_camel_match:
                return CodeIssue(self.path, line_no, IssueType.S008, class_name)

    def snake_case_fct(self, line_no: int, line: str) -> Optional[CodeIssue]:
        pattern = re.compile(r"def\s+(^[_a-z]+)")
        match = pattern.match(line.strip())
        if match:
            name = match.groups()[0]
            return CodeIssue(self.path, line_no, IssueType.S009, name)

    def blank_lines(self) -> List[CodeIssue]:
        """ Create a Style Issue for every code preceded by more than two empty lines.
        :return: The list of found :class:`CodeIssue` objects.
        """
        found_issues : List[CodeIssue] = []
        count_blank = 0
        for line_no, line in enumerate(self.codebase, start=1):
            if line.strip() == "":
                count_blank += 1
            else:  # non-empty line
                if count_blank > 2:
                    found_issues.append(CodeIssue(self.path, line_no, IssueType.S006))
                count_blank = 0
        return found_issues

def print_issues(issues: List[CodeIssue]):
    """ Print the provided list of issues.
    :param issues: The list of issues to print.
    """
    for issue in issues:
        if issue.str_arg:
            print(f"arg = {issue.str_arg}")
            print(f"{issue.path}: Line {issue.line}: {issue.type.name} {(issue.type.value).format(issue.str_arg)}")
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


def main():
    """ Main method. """
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    path: str = parser.parse_args().path
    issue_types : Set[IssueType] = {IssueType.S007, IssueType.S008, IssueType.S009}
    if os.path.isfile(path) and path.endswith(".py"):
        analyze_single(path, issue_types)
    elif os.path.isdir(path):
        analyze_multi(path, issue_types)
    else:
        print(f"Path '{path}' does not contain a valid .py script")


if __name__ == '__main__':
    main()
