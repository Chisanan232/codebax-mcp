"""In-memory symbol index."""

from codebax_mcp.core.parser.models import Symbol


class SymbolIndex:
    """In-memory symbol index with dirty file tracking."""

    def __init__(self):
        self.file_symbols: dict[str, list[Symbol]] = {}
        self.symbol_definitions: dict[str, Symbol] = {}
        self.dirty_files: set = set()
        self.file_timestamps: dict[str, float] = {}

    def add_symbol(self, symbol: Symbol) -> None:
        """Add a symbol to the index."""
        if symbol.file not in self.file_symbols:
            self.file_symbols[symbol.file] = []

        self.file_symbols[symbol.file].append(symbol)
        self.symbol_definitions[symbol.symbol_id] = symbol

    def get_symbol(self, symbol_id: str) -> Symbol | None:
        """Get a symbol by ID."""
        return self.symbol_definitions.get(symbol_id)

    def get_file_symbols(self, file_path: str) -> list[Symbol]:
        """Get all symbols in a file."""
        return self.file_symbols.get(file_path, [])

    def mark_dirty(self, file_path: str) -> None:
        """Mark a file as dirty (needs re-indexing)."""
        self.dirty_files.add(file_path)

    def clear_dirty(self, file_path: str) -> None:
        """Clear dirty flag for a file."""
        self.dirty_files.discard(file_path)

    def clear_file(self, file_path: str) -> None:
        """Clear all symbols for a file."""
        if file_path in self.file_symbols:
            symbols = self.file_symbols[file_path]
            for symbol in symbols:
                del self.symbol_definitions[symbol.symbol_id]
            del self.file_symbols[file_path]

    def search_by_name(self, name: str) -> list[Symbol]:
        """Search symbols by name."""
        results = []
        for symbol in self.symbol_definitions.values():
            if name.lower() in symbol.name.lower():
                results.append(symbol)
        return results

    def get_dirty_files(self) -> list[str]:
        """Get list of dirty files."""
        return list(self.dirty_files)
