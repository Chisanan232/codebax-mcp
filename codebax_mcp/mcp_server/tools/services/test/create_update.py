"""test.create_or_update_for_symbol - Create or update tests for a symbol."""

import os
from typing import Dict, Any, List
from codebax_mcp.mcp_server.models.input import CreateOrUpdateForSymbolInput
from codebax_mcp.mcp_server.models.output import CreateOrUpdateForSymbolOutput, TestFileModification


def create_or_update_for_symbol(input: CreateOrUpdateForSymbolInput) -> CreateOrUpdateForSymbolOutput:
    """Create or update test for a specific symbol."""
    
    # Validate intent
    if input.intent not in ["add_or_update", "delete"]:
        return CreateOrUpdateForSymbolOutput(
            status="failed",
            test_files_modified=[],
            error=f"Invalid intent: {input.intent}"
        )
    
    # Find or create test file
    test_file = _find_or_create_test_file(input.source_path, input.workspace_root)
    
    if not test_file:
        return CreateOrUpdateForSymbolOutput(
            status="failed",
            test_files_modified=[],
            error="Could not find or create test file"
        )
    
    # Generate test code
    test_code = _generate_test_code(input.symbol, input.language, input.behavior_description, input.intent)
    
    # Apply changes
    test_files_modified = []
    if input.intent == "add_or_update":
        _add_or_update_test(test_file, input.symbol, test_code)
        test_files_modified.append(TestFileModification(
            path=os.path.relpath(test_file, input.workspace_root),
            changes_summary=f"Added/updated test for {input.symbol}"
        ))
    elif input.intent == "delete":
        _delete_test(test_file, input.symbol)
        test_files_modified.append(TestFileModification(
            path=os.path.relpath(test_file, input.workspace_root),
            changes_summary=f"Deleted test for {input.symbol}"
        ))
    
    return CreateOrUpdateForSymbolOutput(
        status="ok",
        test_files_modified=test_files_modified
    )


def _find_or_create_test_file(source_path: str, workspace_root: str) -> str:
    """Find or create a test file."""
    source_name = os.path.splitext(os.path.basename(source_path))[0]
    test_file = os.path.join(workspace_root, "tests", f"test_{source_name}.py")
    
    # Create tests directory if needed
    os.makedirs(os.path.dirname(test_file), exist_ok=True)
    
    # Create test file if it doesn't exist
    if not os.path.exists(test_file):
        with open(test_file, 'w') as f:
            f.write("import pytest\n\n")
    
    return test_file


def _generate_test_code(symbol: str, language: str, behavior_description: str, intent: str) -> str:
    """Generate test code for a symbol."""
    
    if language == "python":
        test_name = f"test_{symbol.lower()}"
        return f"""
def {test_name}():
    \"\"\"Test {symbol}: {behavior_description}\"\"\"
    # TODO: Implement test
    pass
"""
    
    return ""


def _add_or_update_test(test_file: str, symbol: str, test_code: str) -> None:
    """Add or update test in test file."""
    try:
        with open(test_file, 'r') as f:
            content = f.read()
        
        # Check if test already exists
        test_name = f"test_{symbol.lower()}"
        if f"def {test_name}" in content:
            # Update existing test
            lines = content.split('\n')
            new_lines = []
            skip = False
            for i, line in enumerate(lines):
                if f"def {test_name}" in line:
                    skip = True
                    new_lines.append(test_code.strip())
                elif skip and line and not line[0].isspace():
                    skip = False
                    new_lines.append(line)
                elif not skip:
                    new_lines.append(line)
            
            with open(test_file, 'w') as f:
                f.write('\n'.join(new_lines))
        else:
            # Add new test
            with open(test_file, 'a') as f:
                f.write('\n' + test_code)
    except Exception as e:
        print(f"Error updating test file: {e}")


def _delete_test(test_file: str, symbol: str) -> None:
    """Delete test from test file."""
    try:
        with open(test_file, 'r') as f:
            content = f.read()
        
        test_name = f"test_{symbol.lower()}"
        lines = content.split('\n')
        new_lines = []
        skip = False
        
        for line in lines:
            if f"def {test_name}" in line:
                skip = True
            elif skip and line and not line[0].isspace():
                skip = False
                new_lines.append(line)
            elif not skip:
                new_lines.append(line)
        
        with open(test_file, 'w') as f:
            f.write('\n'.join(new_lines))
    except Exception as e:
        print(f"Error deleting test: {e}")
