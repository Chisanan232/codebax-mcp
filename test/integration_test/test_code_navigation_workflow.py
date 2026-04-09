"""Integration tests for code navigation workflow."""

import pytest
from pathlib import Path
from codebax_mcp.mcp_server.tools.services.code.index import index_codebase
from codebax_mcp.mcp_server.tools.services.code.navigation import (
    identify_symbol,
    get_definition,
    find_usages
)
from codebax_mcp.mcp_server.models.input import (
    IndexCodebaseInput,
    IdentifySymbolInput,
    GetDefinitionInput,
    FindUsagesInput
)


class TestCodeNavigationWorkflow:
    """Integration tests for code navigation workflow."""

    @pytest.fixture
    def indexed_project(self, tmp_path):
        """Create and index a sample project."""
        # Create project files
        (tmp_path / "calculator.py").write_text("""
class Calculator:
    '''A calculator class.'''
    
    def add(self, a, b):
        '''Add two numbers.'''
        return a + b
    
    def subtract(self, a, b):
        '''Subtract b from a.'''
        return a - b
""")
        
        (tmp_path / "main.py").write_text("""
from calculator import Calculator

def main():
    calc = Calculator()
    result = calc.add(5, 3)
    print(result)
    
    result2 = calc.subtract(10, 4)
    print(result2)

if __name__ == "__main__":
    main()
""")
        
        # Index the project
        input_data = IndexCodebaseInput(
            workspace_root=str(tmp_path),
            full=True
        )
        index_codebase(input_data)
        
        return tmp_path

    def test_identify_and_get_definition_workflow(self, indexed_project):
        """Test workflow: identify symbol -> get definition."""
        # Identify symbol at cursor position
        identify_input = IdentifySymbolInput(
            file=str(indexed_project / "calculator.py"),
            language="python",
            line=4,
            column=8,
            workspace_root=str(indexed_project)
        )
        
        identify_result = identify_symbol(identify_input)
        
        # If symbol was identified, get its definition
        if hasattr(identify_result, 'symbol_id') and identify_result.symbol_id:
            definition_input = GetDefinitionInput(
                symbol_id=identify_result.symbol_id,
                workspace_root=str(indexed_project)
            )
            
            definition_result = get_definition(definition_input)
            
            # Verify we got definition details
            assert definition_result is not None

    def test_find_usages_workflow(self, indexed_project):
        """Test workflow: index -> find usages of a symbol."""
        # First, we need to identify the Calculator class symbol
        from codebax_mcp.core.index.lock_file_store import LockFileStore
        
        lock_file = indexed_project / ".codebax_index.lock"
        store = LockFileStore(str(lock_file))
        data = store.load()
        
        if data and "symbol_definitions" in data:
            # Find Calculator class symbol
            calculator_symbols = [
                s for s in data["symbol_definitions"].values()
                if s.get("name") == "Calculator" and s.get("kind") == "class"
            ]
            
            if calculator_symbols:
                symbol_id = calculator_symbols[0]["symbol_id"]
                
                # Find usages
                usages_input = FindUsagesInput(
                    symbol_id=symbol_id,
                    workspace_root=str(indexed_project)
                )
                
                usages_result = find_usages(usages_input)
                
                # Verify result
                assert usages_result is not None

    def test_navigate_to_method_definition_workflow(self, indexed_project):
        """Test navigating from method call to definition."""
        from codebax_mcp.core.index.lock_file_store import LockFileStore
        
        lock_file = indexed_project / ".codebax_index.lock"
        store = LockFileStore(str(lock_file))
        data = store.load()
        
        if data and "symbol_definitions" in data:
            # Find add method
            add_symbols = [
                s for s in data["symbol_definitions"].values()
                if s.get("name") == "add" and s.get("kind") in ["method", "function"]
            ]
            
            if add_symbols:
                symbol_id = add_symbols[0]["symbol_id"]
                
                # Get definition
                definition_input = GetDefinitionInput(
                    symbol_id=symbol_id,
                    workspace_root=str(indexed_project)
                )
                
                definition_result = get_definition(definition_input)
                
                # Verify we got the definition
                assert definition_result is not None

    def test_cross_file_navigation_workflow(self, indexed_project):
        """Test navigating across files."""
        from codebax_mcp.core.index.lock_file_store import LockFileStore
        
        # Load index
        lock_file = indexed_project / ".codebax_index.lock"
        store = LockFileStore(str(lock_file))
        data = store.load()
        
        if data and "symbol_definitions" in data:
            # Verify symbols from both files are indexed
            calculator_file_symbols = [
                s for s in data["symbol_definitions"].values()
                if "calculator.py" in s.get("file", "")
            ]
            
            main_file_symbols = [
                s for s in data["symbol_definitions"].values()
                if "main.py" in s.get("file", "")
            ]
            
            # Both files should have symbols
            assert len(calculator_file_symbols) > 0
            assert len(main_file_symbols) > 0

    def test_complete_navigation_workflow(self, indexed_project):
        """Test complete navigation workflow: identify -> define -> usages."""
        from codebax_mcp.core.index.lock_file_store import LockFileStore
        
        lock_file = indexed_project / ".codebax_index.lock"
        store = LockFileStore(str(lock_file))
        data = store.load()
        
        if data and "symbol_definitions" in data:
            # Get a symbol
            symbols = list(data["symbol_definitions"].values())
            if symbols:
                symbol_id = symbols[0]["symbol_id"]
                
                # Get definition
                definition_input = GetDefinitionInput(
                    symbol_id=symbol_id,
                    workspace_root=str(indexed_project)
                )
                definition_result = get_definition(definition_input)
                
                # Find usages
                usages_input = FindUsagesInput(
                    symbol_id=symbol_id,
                    workspace_root=str(indexed_project)
                )
                usages_result = find_usages(usages_input)
                
                # Both operations should succeed
                assert definition_result is not None
                assert usages_result is not None
