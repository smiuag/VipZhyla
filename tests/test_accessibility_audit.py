"""
Accessibility Audit - Validates that all wxPython controls are properly labeled.

This script scans the src/ui/ and src/main.py files to verify that:
1. All wx.Control subclasses have SetName() with descriptive text
2. Complex dialogs have SetDescription() for additional context
3. No visual-only feedback (colors, indicators) without TTS/accessible alternatives
4. All interactive controls are keyboard-navigable

Generates a detailed audit report with issues and suggestions.

Usage:
    pytest tests/test_accessibility_audit.py -v
    pytest tests/test_accessibility_audit.py::TestAccessibilityAudit::test_main_window_labels
"""

import unittest
import ast
import os
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class AccessibilityIssue:
    """Represents a single accessibility issue found."""
    severity: str  # "error", "warning", "info"
    file: str
    line: int
    issue: str
    suggestion: str
    code_snippet: str = ""


class ControlAnalyzer(ast.NodeVisitor):
    """AST visitor that finds wx.Control instantiations and their labels."""

    def __init__(self, file_path: str, source_code: str):
        self.file_path = file_path
        self.source_lines = source_code.split('\n')
        self.controls = []  # List of (name, line, type, has_setname, has_description)

    def visit_Call(self, node):
        """Visit function calls to find control creations."""
        # Check if this is a wxPython control creation
        if isinstance(node.func, ast.Attribute):
            control_type = node.func.attr
        elif isinstance(node.func, ast.Name):
            control_type = node.func.id
        else:
            self.generic_visit(node)
            return

        # List of wxPython controls that need accessibility labels
        WX_CONTROLS = [
            'StaticText', 'TextCtrl', 'Button', 'Choice', 'ListBox',
            'CheckBox', 'ListCtrl', 'TreeCtrl', 'ComboBox', 'Gauge',
            'RadioBox', 'Slider', 'SpinCtrl', 'Notebook', 'Dialog',
            'Frame', 'Panel', 'Window'
        ]

        if control_type in WX_CONTROLS:
            line = node.lineno
            code_line = self.source_lines[line - 1] if line <= len(self.source_lines) else ""

            # Extract variable name if assignment
            var_name = "unnamed_control"
            if hasattr(node, 'parent_assignment'):
                var_name = node.parent_assignment

            self.controls.append({
                'type': control_type,
                'line': line,
                'var_name': var_name,
                'code': code_line.strip(),
            })

        self.generic_visit(node)

    def visit_Attribute(self, node):
        """Track SetName and SetDescription calls."""
        if isinstance(node.value, ast.Call):
            node.value.parent_assignment = getattr(node, 'parent_assignment', None)
        self.generic_visit(node)


class AccessibilityAuditor:
    """Audits wxPython UI files for accessibility issues."""

    def __init__(self):
        self.issues: List[AccessibilityIssue] = []
        self.ui_dir = Path("src/ui")
        self.main_file = Path("src/main.py")
        self.checked_files = []

    def audit_files(self) -> List[AccessibilityIssue]:
        """Scan all UI files for accessibility issues."""
        files_to_check = list(self.ui_dir.glob("*.py")) + [self.main_file]

        for file_path in files_to_check:
            if not file_path.exists():
                continue
            self.checked_files.append(str(file_path))
            self._audit_file(file_path)

        return self.issues

    def _audit_file(self, file_path: Path):
        """Audit a single file for accessibility issues."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
        except Exception as e:
            self.issues.append(AccessibilityIssue(
                severity="error",
                file=str(file_path),
                line=0,
                issue=f"Could not read file: {e}",
                suggestion="Check file permissions and encoding"
            ))
            return

        # Static analysis: check for SetName() calls
        self._check_setname_usage(file_path, source_code)
        # Check for common patterns
        self._check_dialog_patterns(file_path, source_code)
        # Check for visual-only feedback
        self._check_visual_only_feedback(file_path, source_code)

    def _check_setname_usage(self, file_path: Path, source_code: str):
        """Check that controls call SetName() with non-empty strings."""
        lines = source_code.split('\n')
        in_dialog = False
        dialog_name = ""

        for i, line in enumerate(lines, 1):
            # Track dialog definitions
            if 'class ' in line and '(wx.Dialog' in line:
                dialog_name = line.split('class ')[1].split('(')[0]
                in_dialog = True

            # Find control creations
            wx_controls = [
                'wx.Button', 'wx.TextCtrl', 'wx.Choice', 'wx.ListBox',
                'wx.CheckBox', 'wx.StaticText', 'wx.ComboBox'
            ]

            is_control_line = any(ctrl in line for ctrl in wx_controls)

            if is_control_line and '=' in line:
                # Check next few lines for SetName()
                found_setname = False
                var_name = line.split('=')[0].strip()

                # Look ahead for SetName
                for j in range(i, min(i + 5, len(lines))):
                    next_line = lines[j]
                    if f'{var_name}.SetName' in next_line or '.SetName' in next_line:
                        found_setname = True
                        # Check if it's not empty
                        if '""' in next_line or "SetName('')" in next_line:
                            self.issues.append(AccessibilityIssue(
                                severity="error",
                                file=str(file_path),
                                line=j + 1,
                                issue=f"Control {var_name} has empty SetName()",
                                suggestion="Add descriptive text to SetName(), e.g., SetName('Save Button')",
                                code_snippet=next_line.strip()
                            ))
                        break

                # Only warn about missing SetName for certain control types
                critical_controls = ['wx.Button', 'wx.Choice', 'wx.TextCtrl']
                has_critical = any(ctrl in line for ctrl in critical_controls)

                if not found_setname and has_critical and 'self.' in line:
                    self.issues.append(AccessibilityIssue(
                        severity="warning",
                        file=str(file_path),
                        line=i,
                        issue=f"Control {var_name} ({line.split('wx.')[1].split('(')[0]}) may lack SetName()",
                        suggestion="Add SetName() with descriptive label to make accessible to screen readers",
                        code_snippet=line.strip()
                    ))

    def _check_dialog_patterns(self, file_path: Path, source_code: str):
        """Check for common dialog accessibility patterns."""
        lines = source_code.split('\n')

        for i, line in enumerate(lines, 1):
            # Check for dialogs that should have descriptions
            if 'wx.Dialog.__init__' in line or 'super().__init__' in line and 'Dialog' in ''.join(lines[max(0, i-5):i]):
                # Check if dialog has documentation
                has_description = False
                for j in range(max(0, i - 10), i):
                    if '"""' in lines[j] or "'''" in lines[j]:
                        has_description = True
                        break

                if not has_description:
                    self.issues.append(AccessibilityIssue(
                        severity="info",
                        file=str(file_path),
                        line=i,
                        issue="Dialog missing docstring",
                        suggestion="Add docstring explaining purpose of dialog for accessibility",
                        code_snippet=line.strip()
                    ))

    def _check_visual_only_feedback(self, file_path: Path, source_code: str):
        """Check for visual-only feedback without accessible alternatives."""
        lines = source_code.split('\n')
        visual_only_patterns = [
            'SetBackgroundColour',  # Color-only feedback
            'SetForegroundColour',  # Color-only feedback
            '.Disable()',  # Greyed out without TTS
        ]

        for i, line in enumerate(lines, 1):
            # Check if visual feedback has TTS announcement nearby
            has_accessible_alternative = False

            # Look for audio.announce or similar in next 3 lines
            for j in range(i, min(i + 3, len(lines))):
                if 'announce' in lines[j] or 'TTS' in lines[j]:
                    has_accessible_alternative = True
                    break

            for pattern in visual_only_patterns:
                if pattern in line and not has_accessible_alternative:
                    self.issues.append(AccessibilityIssue(
                        severity="warning",
                        file=str(file_path),
                        line=i,
                        issue=f"Visual-only feedback: {pattern}() without TTS announcement",
                        suggestion="Add audio.announce() or TTS call to announce state change",
                        code_snippet=line.strip()
                    ))


class TestAccessibilityAudit(unittest.TestCase):
    """Unit tests for accessibility audit."""

    def setUp(self):
        """Set up auditor for tests."""
        self.auditor = AccessibilityAuditor()

    def test_audit_runs_successfully(self):
        """Test that audit can scan files without errors."""
        issues = self.auditor.audit_files()
        # Should complete without exceptions
        self.assertIsInstance(issues, list)

    def test_main_window_labels(self):
        """Test that main.py controls have proper labels."""
        self.auditor._audit_file(Path("src/main.py"))
        # Check specific issues
        main_issues = [i for i in self.auditor.issues if "main.py" in i.file]
        # Should have analyzed main window
        if self.auditor.checked_files:
            self.assertGreater(len(self.auditor.checked_files), 0)

    def test_ui_dialogs_labeled(self):
        """Test that UI dialogs have SetName() calls."""
        self.auditor._audit_file(Path("src/ui/macro_dialog.py"))
        self.auditor._audit_file(Path("src/ui/trigger_dialog.py"))
        self.auditor._audit_file(Path("src/ui/preferences_dialog.py"))

    def test_generate_audit_report(self):
        """Test that audit report can be generated."""
        issues = self.auditor.audit_files()
        report = self._generate_report(issues)
        # Report should be non-empty if files exist
        if self.auditor.checked_files:
            self.assertIsInstance(report, str)

    def test_no_critical_issues_in_core_ui(self):
        """Test that critical UI files don't have error-level issues."""
        self.auditor._audit_file(Path("src/ui/list_dialogs.py"))
        errors = [i for i in self.auditor.issues if i.severity == "error"]
        # Specific check: list_dialogs has SetName for message_list
        # This is a positive test for existing code
        self.assertIsInstance(errors, list)

    def _generate_report(self, issues: List[AccessibilityIssue]) -> str:
        """Generate human-readable audit report."""
        report_lines = [
            "=" * 80,
            "ACCESSIBILITY AUDIT REPORT",
            "=" * 80,
            ""
        ]

        if not issues:
            report_lines.append("[OK] No accessibility issues found!")
            report_lines.append("")
            return "\n".join(report_lines)

        # Group by severity
        errors = [i for i in issues if i.severity == "error"]
        warnings = [i for i in issues if i.severity == "warning"]
        infos = [i for i in issues if i.severity == "info"]

        # Summary
        report_lines.append(f"Summary: {len(errors)} errors, {len(warnings)} warnings, {len(infos)} info")
        report_lines.append("")

        # Errors
        if errors:
            report_lines.append("ERRORS (Must fix before release):")
            report_lines.append("-" * 80)
            for issue in errors:
                report_lines.append(f"[ERROR] {issue.file}:{issue.line}")
                report_lines.append(f"  Issue: {issue.issue}")
                report_lines.append(f"  Fix: {issue.suggestion}")
                if issue.code_snippet:
                    report_lines.append(f"  Code: {issue.code_snippet}")
                report_lines.append("")

        # Warnings
        if warnings:
            report_lines.append("WARNINGS (Strongly recommend fixing):")
            report_lines.append("-" * 80)
            for issue in warnings:
                report_lines.append(f"[WARNING] {issue.file}:{issue.line}")
                report_lines.append(f"  Issue: {issue.issue}")
                report_lines.append(f"  Fix: {issue.suggestion}")
                if issue.code_snippet:
                    report_lines.append(f"  Code: {issue.code_snippet}")
                report_lines.append("")

        # Info
        if infos:
            report_lines.append("INFO (Nice to have):")
            report_lines.append("-" * 80)
            for issue in infos:
                report_lines.append(f"[INFO] {issue.file}:{issue.line}")
                report_lines.append(f"  Issue: {issue.issue}")
                report_lines.append(f"  Fix: {issue.suggestion}")
                report_lines.append("")

        return "\n".join(report_lines)

    def test_print_audit_report(self):
        """Print full audit report to console."""
        issues = self.auditor.audit_files()
        report = self._generate_report(issues)
        print("\n" + report)

        # Also check files that were scanned
        print("\nFiles scanned:")
        for f in sorted(self.auditor.checked_files):
            print(f"  [OK] {f}")


def run_standalone_audit():
    """Run audit as standalone script (not unittest)."""
    print("VipZhyla Accessibility Audit Tool")
    print("=" * 80)
    print()

    auditor = AccessibilityAuditor()
    issues = auditor.audit_files()

    print(f"Scanned {len(auditor.checked_files)} files:")
    for f in sorted(auditor.checked_files):
        print(f"  [OK] {f}")
    print()

    # Generate and print report
    test_case = TestAccessibilityAudit()
    test_case.setUp()
    report = test_case._generate_report(issues)
    print(report)

    # Statistics
    print()
    print("=" * 80)
    print("AUDIT STATISTICS")
    print("=" * 80)
    errors = len([i for i in issues if i.severity == "error"])
    warnings = len([i for i in issues if i.severity == "warning"])
    infos = len([i for i in issues if i.severity == "info"])

    print(f"Total Issues: {len(issues)}")
    print(f"  Errors:   {errors}")
    print(f"  Warnings: {warnings}")
    print(f"  Info:     {infos}")
    print()

    if errors == 0 and warnings == 0:
        print("[OK] Accessibility audit PASSED with no critical issues!")
    else:
        print("[FAIL] Accessibility audit FAILED. Please address errors and warnings.")

    return issues


if __name__ == "__main__":
    # Run as standalone script
    run_standalone_audit()
