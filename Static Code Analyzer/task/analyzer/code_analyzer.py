# code_analyzer.py module
"""Functionality for running static code analysis of python scripts."""

import os.path
from typing import List, Optional

from code_analyzer_base import BaseCodeAnalyzer, IssueType, CodeIssue


class CodeAnalyzer(BaseCodeAnalyzer):
    """ Implementation of static code analysis methods. """

    def long_line(self, line_no: int) -> Optional[CodeIssue]:
        """ Create a Style Issue if the input line exceeds the 79 characters limit.
        :param line_no: The line to analyze.
        :return: A :class:`CodeIssue` of Type S001 or :const:`None`.
        """
        line = self.codebase[line_no]
        if len(line) > self.MAX_LINES:
            return CodeIssue(line_no, IssueType.S001)

    def indentation(self, line_no: int) -> Optional[CodeIssue]:
        """ Create a Style Issue if the input line is not indented by a multiple of four.
         :param line_no: The line to analyze.
         :return: A :class:`CodeIssue` of Type S002 or :const:`None`.
         """
        line = self.codebase[line_no]
        if not line.isspace() and (len(line) - len(line.lstrip())) % 4 != 0:
            return CodeIssue(line_no, IssueType.S002)

    def semicolon(self, line_no: int) -> Optional[CodeIssue]:
        """ Create a Style Issue if the input line contains an unnecessary semicolon after a statement.
        :param line_no: The line to analyze.
        :return: A :class:`CodeIssue` of Type S003 or :const:`None`.
        """
        line = self.codebase[line_no]
        code, comment = BaseCodeAnalyzer.split_at_comment(line)
        if code.strip().endswith(';'):
            return CodeIssue(line_no, IssueType.S003)

    def missing_spaces(self, line_no: int) -> Optional[CodeIssue]:
        """ Create a Style Issue if the input line contains inline comment which is not separated with two spaces.
        :param line_no: The line to analyze.
        :return: A :class:`CodeIssue` of Type S004 or :const:`None`.
        """
        line = self.codebase[line_no]
        code, comment = BaseCodeAnalyzer.split_at_comment(line)
        has_inline_comment = BaseCodeAnalyzer.has_inline_comment(line)
        if has_inline_comment and len(code) - len(code.rstrip()) < 2:
            # less than 2 spaces before comment
            return CodeIssue(line_no, IssueType.S004)

    def todo(self, line_no: int) -> Optional[CodeIssue]:
        """ Create a Style Issue if the input line contains a 'TODO' comment (any case).
        :param line_no: The line to analyze.
        :return: A :class:`CodeIssue` of Type S005 or :const:`None`.
        """
        code, comment = BaseCodeAnalyzer.split_at_comment(self.codebase[line_no])
        if "TODO" in comment.upper():
            # we have a comment that contains a 'todo'
            return CodeIssue(line_no, IssueType.S005)

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
                    found_issues.append(CodeIssue(line_no, IssueType.S006))
                count_blank = 0
        return found_issues


def main():
    """ Main method. """
    path = input()
    if os.path.isfile(path):
        analyzer = CodeAnalyzer(path)
        analyzer.analyze(set(IssueType))
        analyzer.print_issues()
    else:
        print(f"File '{path}' does not exist")


if __name__ == '__main__':
    main()
