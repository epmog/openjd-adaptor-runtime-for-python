# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

import sys
import pytest

# Only run these tests on Windows
pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific tests")

if sys.platform == "win32":
    from openjd.adaptor_runtime_client._win32._constants import (
        # File access constants
        GENERIC_READ,
        GENERIC_WRITE,
        GENERIC_ALL,
        FILE_GENERIC_READ,
        FILE_GENERIC_WRITE,
        DELETE,
        
        # Security constants
        ACL_REVISION,
        SidTypeUser,
        SidTypeDomain,
        DACL_SECURITY_INFORMATION,
        
        # Named pipe constants
        PIPE_ACCESS_DUPLEX,
        PIPE_TYPE_MESSAGE,
        PIPE_READMODE_MESSAGE,
        PIPE_WAIT,
        OPEN_EXISTING,
        
        # Error constants
        ERROR_SUCCESS,
        ERROR_FILE_NOT_FOUND,
        ERROR_BROKEN_PIPE,
        ERROR_PIPE_NOT_CONNECTED,
        ERROR_MORE_DATA,
        ERROR_INSUFFICIENT_BUFFER,
        ERROR_NONE_MAPPED,
        ERROR_INVALID_SID,
        NO_ERROR,
        WAIT_TIMEOUT,
        
        # Handle constants
        INVALID_HANDLE_VALUE,
    )


class TestWindowsConstants:
    """Test Windows constants module."""

    def test_file_access_constants(self):
        """Test that file access constants have correct values."""
        # Test generic access rights
        assert GENERIC_READ == 0x80000000
        assert GENERIC_WRITE == 0x40000000
        assert GENERIC_ALL == 0x10000000
        
        # Test DELETE constant
        assert DELETE == 0x00010000
        
        # Test composite constants are properly calculated
        assert FILE_GENERIC_READ & GENERIC_READ != 0
        assert FILE_GENERIC_WRITE & GENERIC_WRITE != 0

    def test_security_constants(self):
        """Test that security constants have correct values."""
        assert ACL_REVISION == 2
        assert SidTypeUser == 1
        assert SidTypeDomain == 3
        assert DACL_SECURITY_INFORMATION == 0x00000004

    def test_named_pipe_constants(self):
        """Test that named pipe constants have correct values."""
        assert PIPE_ACCESS_DUPLEX == 0x00000003
        assert PIPE_TYPE_MESSAGE == 0x00000004
        assert PIPE_READMODE_MESSAGE == 0x00000002
        assert PIPE_WAIT == 0x00000000
        assert OPEN_EXISTING == 3

    def test_error_constants(self):
        """Test that error constants have correct values."""
        assert ERROR_SUCCESS == 0
        assert NO_ERROR == 0
        assert ERROR_FILE_NOT_FOUND == 2
        assert ERROR_BROKEN_PIPE == 109
        assert ERROR_PIPE_NOT_CONNECTED == 233
        assert ERROR_MORE_DATA == 234
        assert ERROR_INSUFFICIENT_BUFFER == 122
        assert ERROR_NONE_MAPPED == 1332
        assert ERROR_INVALID_SID == 1337
        assert WAIT_TIMEOUT == 258

    def test_handle_constants(self):
        """Test that handle constants have correct values."""
        assert INVALID_HANDLE_VALUE == -1

    def test_constants_are_integers(self):
        """Test that all constants are integers."""
        constants_to_test = [
            GENERIC_READ, GENERIC_WRITE, GENERIC_ALL,
            FILE_GENERIC_READ, FILE_GENERIC_WRITE, DELETE,
            ACL_REVISION, SidTypeUser, SidTypeDomain,
            PIPE_ACCESS_DUPLEX, PIPE_TYPE_MESSAGE, OPEN_EXISTING,
            ERROR_SUCCESS, ERROR_FILE_NOT_FOUND, ERROR_BROKEN_PIPE,
            INVALID_HANDLE_VALUE
        ]
        
        for constant in constants_to_test:
            assert isinstance(constant, int), f"Constant {constant} is not an integer"

    def test_error_constants_compatibility(self):
        """Test that error constants match expected winerror values."""
        # These are the key error constants used in the existing codebase
        # that need to match winerror module values
        expected_errors = {
            'ERROR_FILE_NOT_FOUND': 2,
            'ERROR_BROKEN_PIPE': 109,
            'ERROR_PIPE_NOT_CONNECTED': 233,
            'ERROR_MORE_DATA': 234,
            'ERROR_PIPE_BUSY': 231,
            'ERROR_INSUFFICIENT_BUFFER': 122,
        }
        
        # Import our constants
        from openjd.adaptor_runtime_client._win32._constants import (
            ERROR_FILE_NOT_FOUND as OUR_ERROR_FILE_NOT_FOUND,
            ERROR_BROKEN_PIPE as OUR_ERROR_BROKEN_PIPE,
            ERROR_PIPE_NOT_CONNECTED as OUR_ERROR_PIPE_NOT_CONNECTED,
            ERROR_MORE_DATA as OUR_ERROR_MORE_DATA,
            ERROR_PIPE_BUSY as OUR_ERROR_PIPE_BUSY,
            ERROR_INSUFFICIENT_BUFFER as OUR_ERROR_INSUFFICIENT_BUFFER,
        )
        
        # Verify they match expected values
        assert OUR_ERROR_FILE_NOT_FOUND == expected_errors['ERROR_FILE_NOT_FOUND']
        assert OUR_ERROR_BROKEN_PIPE == expected_errors['ERROR_BROKEN_PIPE']
        assert OUR_ERROR_PIPE_NOT_CONNECTED == expected_errors['ERROR_PIPE_NOT_CONNECTED']
        assert OUR_ERROR_MORE_DATA == expected_errors['ERROR_MORE_DATA']
        assert OUR_ERROR_PIPE_BUSY == expected_errors['ERROR_PIPE_BUSY']
        assert OUR_ERROR_INSUFFICIENT_BUFFER == expected_errors['ERROR_INSUFFICIENT_BUFFER']