"""Output models for test discovery and generation tools."""

from typing import List, Optional
from pydantic import BaseModel, Field


class ExistingTest(BaseModel):
    """Information about an existing test file."""
    
    path: str = Field(..., description="Test file path")
    framework: Optional[str] = Field(None, description="Test framework (pytest, unittest, nose)")
    confidence: float = Field(..., description="Confidence score (0.0-1.0)")
    notes: Optional[str] = Field(None, description="Additional information")


class LocateForSourceOutput(BaseModel):
    """Output for test.locate_for_source tool."""
    
    source_path: str = Field(..., description="Source file path")
    existing_tests: List[ExistingTest] = Field(
        default_factory=list,
        description="List of found test files"
    )
    suggested_new_test_path: Optional[str] = Field(
        None,
        description="Suggested path for new test if none found"
    )
    notes: Optional[str] = Field(None, description="Additional information")


class TestFileModification(BaseModel):
    """Information about a test file modification."""
    
    path: str = Field(..., description="Test file path")
    changes_summary: str = Field(..., description="Summary of changes made")


class CreateOrUpdateForSymbolOutput(BaseModel):
    """Output for test.create_or_update_for_symbol tool."""
    
    status: str = Field(..., description="Status: 'ok' or 'failed'")
    test_files_modified: List[TestFileModification] = Field(
        default_factory=list,
        description="List of modified test files"
    )
    error: Optional[str] = Field(None, description="Error message if failed")
    notes: Optional[str] = Field(None, description="Additional information")
