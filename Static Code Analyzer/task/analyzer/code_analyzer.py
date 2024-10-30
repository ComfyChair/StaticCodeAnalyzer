from typing import List
from code_issue import IssueType, CodeIssue


class CodeAnalyzer:
    MAX_LINES = 79
    def __init__(self, path: str):
        with open(path, "r") as file:
            self.code_base = file.readlines()

    def analyze(self, types: List[IssueType]) -> List[CodeIssue]:
        """Initializes search for issues of the given types
        :returns a list of code issues, sorted by line number"""
        issues : List[CodeIssue] = []
        for issue_type in types:
            issues.extend(issue_type.value[0](self))
        issues.sort(key=lambda i: i.line)
        return issues

    def long_lines(self) -> List[CodeIssue]:
        """Creates a Style Issue for every line that exceeds the 79 characters limit."""
        issue_type = IssueType.S001
        return [CodeIssue(line_no, issue_type, issue_type.value[1])
                for line_no, line in enumerate(self.code_base, start=1)
                if len(line) > self.MAX_LINES]

    def indentation(self):
        """Creates a Style Issue for every line that is not indented by a multiple of four."""
        issue_type = IssueType.S002
        return [CodeIssue(line_no, issue_type, issue_type.value[1])
                for line_no, line in enumerate(self.code_base, start=1)
                if (len(line) - len(line.lstrip())) % 4 != 0]

    def semicolon(self):
        """Creates a Style Issue for every line that contains an unnecessary semicolon after a statement."""
        issue_type = IssueType.S003
        return [CodeIssue(line_no, issue_type, issue_type.value[1])
                for line_no, line in enumerate(self.code_base, start=1)
                if line.strip().endswith(";") and not line.strip().startswith("#")]

    def missing_spaces(self):
        """Creates a Style Issue for every line that contains inline comment which is not separated with two spaces."""
        issue_type = IssueType.S004
        found_issues = []
        for line_no, line in enumerate(self.code_base, start=1):
            comment_split = line.split("#")
            if len(comment_split) > 1 and comment_split[0].strip():
                # actual split and [0] part not empty: we have an inline comment
                if len(comment_split[0]) - len(comment_split[0].rstrip()) != 2:  # less than 2 spaces before #
                    found_issues.append(CodeIssue(line_no, issue_type, issue_type.value[1]))
        return found_issues


    def todo(self):
        issue_type = IssueType.S005
        found_issues = []
        for line_no, line in enumerate(self.code_base, start=1):
            comment_split = line.split("#")
            if len(comment_split) > 1 and "todo" in comment_split[1].lower():
                # we have a comment that contains a 'todo'
                found_issues.append(CodeIssue(line_no, issue_type, issue_type.value[1]))
        return found_issues

    def blank_lines(self):
        issue_type = IssueType.S006
        found_issues = []
        count_blank = 0
        for line_no, line in enumerate(self.code_base, start=1):
            if line.strip() == "":
                count_blank += 1
            else:  # non-empty line
                if count_blank > 2:
                    found_issues.append(CodeIssue(line_no, issue_type, issue_type.value[1]))
                count_blank = 0
        return found_issues


def print_issues(issue_list):
    """Convenience method to print all Issues in the order of occurrence."""
    for issue in issue_list:
        print(f"Line {issue.line}: {issue.type.value} {issue.msg}")


def main():
    """Main method."""
    path = input()
    analyzer = CodeAnalyzer(path)
    issues = analyzer.analyze(list(IssueType))
    print_issues(issues)


if __name__ == '__main__':
    main()
