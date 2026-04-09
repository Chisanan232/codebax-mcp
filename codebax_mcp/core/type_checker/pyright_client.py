"""Pyright CLI client for Python type checking."""

import json
import subprocess
from typing import List, Optional, Dict, Any
from .models import Diagnostic, TypeInfo


class PyrightClient:
    """Wrapper for Pyright CLI."""

    def __init__(self, workspace_root: str = "."):
        self.workspace_root = workspace_root

    def validate(self, file_path: str) -> List[Diagnostic]:
        """Run Pyright on a file and return diagnostics."""
        try:
            result = subprocess.run(
                ["pyright", "--outputjson", file_path],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 or result.stdout:
                try:
                    output = json.loads(result.stdout)
                    return self._parse_diagnostics(output)
                except json.JSONDecodeError:
                    return []
            return []
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []

    def _parse_diagnostics(self, output: Dict[str, Any]) -> List[Diagnostic]:
        """Parse Pyright JSON output into diagnostics."""
        diagnostics = []
        
        for diag in output.get('generalDiagnostics', []):
            diagnostics.append(Diagnostic(
                file=diag.get('file', ''),
                line=diag.get('range', {}).get('start', {}).get('line', 0),
                column=diag.get('range', {}).get('start', {}).get('character', 0),
                message=diag.get('message', ''),
                severity=diag.get('severity', 'information'),
                code=diag.get('rule', None)
            ))
        
        return diagnostics

    def get_type_info(self, file_path: str, line: int, column: int) -> Optional[TypeInfo]:
        """Get type information at a specific location."""
        # This would require LSP protocol or more advanced Pyright integration
        # For MVP, return None
        return None
