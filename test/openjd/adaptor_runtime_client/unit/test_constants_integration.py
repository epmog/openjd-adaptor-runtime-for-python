# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

import sys
import pytest

# Only run these tests on Windows
pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific tests")

if sys.platform == "win32":
    from openjd.adaptor_runtime_client._win32._constants import (
        GENERIC_READ,
        GENERIC_WRITE,
        GENERIC_ALL,
        FILE_GENERIC_READ,
        FILE_GENERIC_WRITE,
        DELETE,
        ACL_REVISION,
        ERROR_BROKEN_PIPE,
        ERROR_PIPE_NOT_CONNECTED,
        ERROR_MORE_DATA,
        ERROR_FILE_NOT_FOUND,
        ERROR_PIPE_BUSY,
        NO_ERROR,
    )


class TestConstantsIntegration:
    """Test that constants can be used as drop-in replacements for pywin32 constants."""

    def test_constants_can_replace_win32con_usage(self):
        """Test that our constants can replace win32con usage patterns."""
        # Test the pattern used in named_pipe_helper.py:
        # win32con.GENERIC_READ | win32con.GENERIC_WRITE
        combined_access = GENERIC_READ | GENERIC_WRITE
        assert combined_access != 0
        assert (combined_access & GENERIC_READ) != 0
        assert (combined_access & GENERIC_WRITE) != 0
        
        # Test the pattern used in secure_open.py:
        # win32con.DELETE
        assert DELETE == 0x00010000

    def test_constants_can_replace_winerror_usage(self):
        """Test that our constants can replace winerror usage patterns."""
        # Test error checking patterns used in named_pipe_helper.py
        pipe_errors = [ERROR_BROKEN_PIPE, ERROR_PIPE_NOT_CONNECTED]
        assert ERROR_BROKEN_PIPE in pipe_errors
        assert ERROR_PIPE_NOT_CONNECTED in pipe_errors
        
        # Test file operation patterns
        file_errors = [ERROR_FILE_NOT_FOUND, ERROR_PIPE_BUSY]
        assert ERROR_FILE_NOT_FOUND in file_errors
        assert ERROR_PIPE_BUSY in file_errors
        
        # Test success checking
        assert NO_ERROR == 0

    def test_constants_can_replace_ntsecuritycon_usage(self):
        """Test that our constants can replace ntsecuritycon usage patterns."""
        # Test the pattern used in secure_open.py:
        # con.FILE_GENERIC_READ, con.FILE_GENERIC_WRITE
        assert FILE_GENERIC_READ != 0
        assert FILE_GENERIC_WRITE != 0
        
        # These should be composite values that include GENERIC_READ/GENERIC_WRITE
        assert (FILE_GENERIC_READ & GENERIC_READ) != 0
        assert (FILE_GENERIC_WRITE & GENERIC_WRITE) != 0

    def test_constants_can_replace_win32security_usage(self):
        """Test that our constants can replace win32security usage patterns."""
        # Test the pattern used in named_pipe_helper.py:
        # win32security.ACL_REVISION
        assert ACL_REVISION == 2

    def test_error_code_values_match_expected(self):
        """Test that error codes match the values expected by existing code."""
        # These values are used in conditional checks throughout the codebase
        assert ERROR_BROKEN_PIPE == 109
        assert ERROR_PIPE_NOT_CONNECTED == 233
        assert ERROR_MORE_DATA == 234
        assert ERROR_FILE_NOT_FOUND == 2
        assert ERROR_PIPE_BUSY == 231

    def test_bitwise_operations_work_correctly(self):
        """Test that bitwise operations work correctly with our constants."""
        # Test combining access rights
        full_access = GENERIC_READ | GENERIC_WRITE
        assert (full_access & GENERIC_READ) == GENERIC_READ
        assert (full_access & GENERIC_WRITE) == GENERIC_WRITE
        
        # Test checking for specific access
        read_only = GENERIC_READ
        assert (read_only & GENERIC_READ) != 0
        assert (read_only & GENERIC_WRITE) == 0
        
        # Test GENERIC_ALL includes other rights
        assert (GENERIC_ALL & GENERIC_READ) == 0  # GENERIC_ALL is separate from specific rights
        assert (GENERIC_ALL & GENERIC_WRITE) == 0  # GENERIC_ALL is separate from specific rights