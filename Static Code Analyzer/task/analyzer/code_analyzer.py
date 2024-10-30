import enum
from dataclasses import dataclass
from typing import List

MAX_LINES = 79

class IssueCode(enum.Enum):
    STYLISTIC_ISSUE = "S001"

@dataclass(frozen=True)
class Issue:
    """Class to wrap detected Issues in."""
    line: int
    code: IssueCode
    msg: str

def analyze_line_length(lines: List[str]) -> List[Issue]:
    issues = []
    for line_no in range(len(lines)):
        if len(lines[line_no]) > MAX_LINES:
            issues.append(Issue(line_no + 1, IssueCode.STYLISTIC_ISSUE, "Too long"))
    return issues


def print_issues(line_issues):
    for issue in line_issues:
        print(f"Line {issue.line}: {issue.code.value} {issue.msg}")


def main():
    path = input()
    with open(path, "r") as file:
        file_contents = file.readlines()
    line_issues = analyze_line_length(file_contents)
    print_issues(line_issues)


if __name__ == '__main__':
    main()
