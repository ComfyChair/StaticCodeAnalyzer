import os.path
from typing import List
from code_issue import IssueType, CodeIssue
from base_code_analyzer import BaseCodeAnalyzer


class CodeAnalyzer(BaseCodeAnalyzer):

    def long_line(self, line_no: int) -> CodeIssue | None:
        """Creates a Style Issue for every line that exceeds the 79 characters limit."""
        line = self.code_base[line_no]
        if len(line) > self.MAX_LINES:
            return CodeIssue(line_no, IssueType.S001)

    def indentation(self, line_no: int) -> CodeIssue | None:
        """Creates a Style Issue for every line that is not indented by a multiple of four."""
        line = self.code_base[line_no]
        if not line.isspace() and (len(line) - len(line.lstrip())) % 4 != 0:
            return CodeIssue(line_no, IssueType.S002)

    def semicolon(self, line_no: int) -> CodeIssue | None:
        """Creates a Style Issue for every line that contains an unnecessary semicolon after a statement."""
        line = self.code_base[line_no]
        code, comment = BaseCodeAnalyzer.split_at_comment(line)
        if code.strip().endswith(';'):
            return CodeIssue(line_no, IssueType.S003)

    def missing_spaces(self, line_no: int) -> CodeIssue | None:
        """Creates a Style Issue for every line that contains inline comment which is not separated with two spaces."""
        line = self.code_base[line_no]
        code, comment = BaseCodeAnalyzer.split_at_comment(line)
        has_inline_comment = BaseCodeAnalyzer.has_inline_comment(line)
        if has_inline_comment and len(code) - len(code.rstrip()) < 2:
            # less than 2 spaces before comment
            return CodeIssue(line_no, IssueType.S004)

    def todo(self, line_no: int) -> CodeIssue | None:
        code, comment = BaseCodeAnalyzer.split_at_comment(self.code_base[line_no])
        if "TODO" in comment.upper():
            # we have a comment that contains a 'todo'
            return CodeIssue(line_no, IssueType.S005)

    def blank_lines(self) -> List[CodeIssue]:
        found_issues = []
        count_blank = 0
        for line_no, line in enumerate(self.code_base, start=1):
            if line.strip() == "":
                count_blank += 1
            else:  # non-empty line
                if count_blank > 2:
                    found_issues.append(CodeIssue(line_no, IssueType.S006))
                count_blank = 0
        return found_issues


def main():
    """Main method."""
    path = input()
    if os.path.isfile(path):
        analyzer = CodeAnalyzer(path)
        analyzer.analyze(set(IssueType))
        analyzer.print_issues()
    else:
        print(f"File '{path}' does not exist")


if __name__ == '__main__':
    main()
