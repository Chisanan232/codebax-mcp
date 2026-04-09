"""Path resolution utilities."""

import os
from pathlib import Path
from typing import Optional, List


def resolve_module_path(module_string: str, workspace_root: str) -> Optional[str]:
    """Resolve a module string (e.g., 'your_lib.sub_pck.module') to a file path."""
    parts = module_string.split('.')
    
    # Try different path combinations
    possible_paths = [
        os.path.join(workspace_root, *parts) + '.py',
        os.path.join(workspace_root, *parts, '__init__.py'),
        os.path.join(workspace_root, 'src', *parts) + '.py',
        os.path.join(workspace_root, 'src', *parts, '__init__.py'),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None


def find_python_files(directory: str) -> List[str]:
    """Find all Python files in a directory."""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Skip common non-source directories
        dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', '.venv', 'venv', 'node_modules', '.pytest_cache'}]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    return python_files


def get_relative_path(file_path: str, workspace_root: str) -> str:
    """Get relative path from workspace root."""
    try:
        return os.path.relpath(file_path, workspace_root)
    except ValueError:
        return file_path
