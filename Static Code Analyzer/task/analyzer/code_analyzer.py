import os.path
from typing import List
from code_issue import IssueType, CodeIssue
from base_code_analyzer import BaseCodeAnalyzer


class CodeAnalyzer(BaseCodeAnalyzer):

    def long_lines(self, issue_type: IssueType) -> List[CodeIssue]:
        """Creates a Style Issue for every line that exceeds the 79 characters limit."""
        issues = [CodeIssue(line_no, issue_type)
                  for line_no, line in enumerate(self.code_base, start=1)
                  if len(line) > self.MAX_LINES]
        return issues

    def indentation(self, issue_type: IssueType) -> List[CodeIssue]:
        """Creates a Style Issue for every line that is not indented by a multiple of four."""
        return [CodeIssue(line_no, issue_type)
                for line_no, line in enumerate(self.code_base, start=1)
                if not line.isspace() and (len(line) - len(line.lstrip())) % 4 != 0]

    def semicolon(self, issue_type: IssueType) -> List[CodeIssue]:
        """Creates a Style Issue for every line that contains an unnecessary semicolon after a statement."""
        found_issues = []
        for line_no, line in enumerate(self.code_base, start=1):
            code, comment = BaseCodeAnalyzer.split_at_comment(line)
            if code.strip().endswith(';'):
                found_issues.append(CodeIssue(line_no, issue_type))
        return found_issues

    def missing_spaces(self, issue_type: IssueType) -> List[CodeIssue]:
        """Creates a Style Issue for every line that contains inline comment which is not separated with two spaces."""
        found_issues = []
        for line_no, line in enumerate(self.code_base, start=1):
            code, comment = BaseCodeAnalyzer.split_at_comment(line)
            has_inline_comment = BaseCodeAnalyzer.has_inline_comment(line)
            if has_inline_comment and len(code) - len(code.rstrip()) < 2:
                # less than 2 spaces before comment
                found_issues.append(CodeIssue(line_no, issue_type))
        return found_issues

    def todo(self, issue_type: IssueType) -> List[CodeIssue]:
        found_issues = []
        for line_no, line in enumerate(self.code_base, start=1):
            code, comment = BaseCodeAnalyzer.split_at_comment(line)
            if "TODO" in comment.upper():
                # we have a comment that contains a 'todo'
                found_issues.append(CodeIssue(line_no, issue_type))
        return found_issues

    def blank_lines(self, issue_type: IssueType) -> List[CodeIssue]:
        found_issues = []
        count_blank = 0
        for line_no, line in enumerate(self.code_base, start=1):
            if line.strip() == "":
                count_blank += 1
            else:  # non-empty line
                if count_blank > 2:
                    found_issues.append(CodeIssue(line_no, issue_type))
                count_blank = 0
        return found_issues


def main():
    """Main method."""
    path = input()
    if os.path.isfile(path):
        analyzer = CodeAnalyzer(path)
        analyzer.analyze(list(IssueType))
        analyzer.print_issues()
    else:
        print(f"File '{path}' does not exist")


if __name__ == '__main__':
    main()
