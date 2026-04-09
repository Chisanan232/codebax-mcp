"""Python AST parser implementation."""

import ast

from .base import BaseParser
from .models import Range, Symbol, SymbolKind


class PythonParser(BaseParser):
    """Python parser using stdlib ast module."""

    def parse_file(self, file_path: str) -> list[Symbol]:
        """Parse a Python file and extract symbols."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
            return self.parse_content(content, file_path, "python")
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return []

    def parse_content(self, content: str, file_path: str, language: str) -> list[Symbol]:
        """Parse Python content and extract symbols."""
        if language != "python":
            return []

        try:
            tree = ast.parse(content)
            symbols = []
            self._extract_symbols(tree, symbols, file_path, content)
            return symbols
        except SyntaxError as e:
            print(f"Syntax error in {file_path}: {e}")
            return []

    def _extract_symbols(
        self, node: ast.AST, symbols: list[Symbol], file_path: str, content: str, parent_id: str | None = None
    ) -> None:
        """Recursively extract symbols from AST."""
        lines = content.split("\n")

        # Use iter_child_nodes instead of walk to maintain hierarchy
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                symbol_id = f"{file_path}:function:{child.name}:{child.lineno}"
                range_obj = self._get_range(child, lines)
                docstring = ast.get_docstring(child)

                symbols.append(
                    Symbol(
                        symbol_id=symbol_id,
                        name=child.name,
                        kind=SymbolKind.METHOD if parent_id else SymbolKind.FUNCTION,
                        language="python",
                        file=file_path,
                        range=range_obj,
                        parent_id=parent_id,
                        docstring=docstring,
                        signature=self._get_function_signature(child),
                    )
                )

            elif isinstance(child, ast.ClassDef):
                symbol_id = f"{file_path}:class:{child.name}:{child.lineno}"
                range_obj = self._get_range(child, lines)
                docstring = ast.get_docstring(child)

                symbols.append(
                    Symbol(
                        symbol_id=symbol_id,
                        name=child.name,
                        kind=SymbolKind.CLASS,
                        language="python",
                        file=file_path,
                        range=range_obj,
                        parent_id=parent_id,
                        docstring=docstring,
                    )
                )

                # Recursively extract methods from class
                self._extract_symbols(child, symbols, file_path, content, parent_id=symbol_id)
            else:
                # Continue recursion for other node types
                self._extract_symbols(child, symbols, file_path, content, parent_id)

    def _get_range(self, node: ast.AST, lines: list[str]) -> Range:
        """Get code range for AST node."""
        end_lineno = getattr(node, "end_lineno", node.lineno)
        end_col_offset = getattr(
            node, "end_col_offset", len(lines[node.lineno - 1]) if node.lineno <= len(lines) else 0
        )

        return Range(
            line_start=node.lineno, column_start=node.col_offset, line_end=end_lineno, column_end=end_col_offset
        )

    def _get_function_signature(self, node: ast.FunctionDef) -> str:
        """Extract function signature."""
        args = []
        for arg in node.args.args:
            args.append(arg.arg)
        return f"def {node.name}({', '.join(args)})"
