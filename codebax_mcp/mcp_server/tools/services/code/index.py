"""code.index - Build or update codebase index."""

import os

from codebax_mcp.core.index import LockFileStore, SymbolIndex
from codebax_mcp.core.parser import PythonParser
from codebax_mcp.core.utils import find_python_files
from codebax_mcp.mcp_server.models.input import IndexCodebaseInput
from codebax_mcp.mcp_server.models.output import IndexCodebaseOutput


def index_codebase(input: IndexCodebaseInput) -> IndexCodebaseOutput:
    """Build or update codebase index."""
    indexed_files = 0
    skipped_files = 0

    try:
        # Initialize index
        index = SymbolIndex()
        store = LockFileStore(os.path.join(input.workspace_root, ".codebax_index.lock"))

        # Determine files to index
        if input.paths:
            files_to_index = input.paths
        else:
            files_to_index = find_python_files(input.workspace_root)

        # Parse files
        parser = PythonParser()
        for file_path in files_to_index:
            try:
                symbols = parser.parse_file(file_path)
                for symbol in symbols:
                    index.add_symbol(symbol)
                indexed_files += 1
            except Exception as e:
                print(f"Error indexing {file_path}: {e}")
                skipped_files += 1

        # Save index
        index_data = {
            "file_symbols": {k: [s.dict() for s in v] for k, v in index.file_symbols.items()},
            "symbol_definitions": {k: v.dict() for k, v in index.symbol_definitions.items()},
        }

        if store.save(index_data):
            return IndexCodebaseOutput(
                status="ok",
                indexed_files=indexed_files,
                skipped_files=skipped_files,
                notes=f"Index saved to {store.lock_file_path}",
            )
        return IndexCodebaseOutput(
            status="failed", indexed_files=indexed_files, skipped_files=skipped_files, error="Failed to save index"
        )

    except Exception as e:
        return IndexCodebaseOutput(
            status="failed", indexed_files=indexed_files, skipped_files=skipped_files, error=str(e)
        )
