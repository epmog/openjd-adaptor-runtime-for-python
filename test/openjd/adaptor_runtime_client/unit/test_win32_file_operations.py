# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

import pytest
import sys
from unittest.mock import MagicMock, patch, call
import ctypes
from ctypes.wintypes import HANDLE, DWORD

# Skip all tests if not on Windows
pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific tests")

if sys.platform == "win32":
    from openjd.adaptor_runtime_client._win32._file_operations import (
        ReadFile,
        WriteFile,
        ERROR_MORE_DATA,
        NO_ERROR,
    )


class TestFileOperations:
    """Test suite for Windows file operations using ctypes."""

    @patch("openjd.adaptor_runtime_client._win32._file_operations.kernel32")
    def test_read_file_success(self, mock_kernel32):
        """Test successful ReadFile operation."""
        # GIVEN
        mock_handle = MagicMock(spec=HANDLE)
        buffer_size = 1024
        test_data = b"Hello, World!"
        
        # Mock successful ReadFile call
        mock_kernel32.ReadFile.return_value = True
        
        def mock_read_file_side_effect(handle, buffer, size, bytes_read_ptr, overlapped):
            # Simulate writing data to the buffer
            ctypes.memmove(buffer, test_data, len(test_data))
            # Set bytes read - bytes_read_ptr is a byref() object, access its _obj
            bytes_read_ptr._obj.value = len(test_data)
            return True
            
        mock_kernel32.ReadFile.side_effect = mock_read_file_side_effect
        
        # WHEN
        error_code, data = ReadFile(mock_handle, buffer_size)
        
        # THEN
        assert error_code == NO_ERROR
        assert data == test_data
        mock_kernel32.ReadFile.assert_called_once()

    @patch("openjd.adaptor_runtime_client._win32._file_operations.kernel32")
    def test_read_file_more_data(self, mock_kernel32):
        """Test ReadFile operation with ERROR_MORE_DATA."""
        # GIVEN
        mock_handle = MagicMock(spec=HANDLE)
        buffer_size = 1024
        test_data = b"Partial data"
        
        # Mock ReadFile call that returns False with ERROR_MORE_DATA
        mock_kernel32.ReadFile.return_value = False
        mock_kernel32.GetLastError.return_value = ERROR_MORE_DATA
        
        def mock_read_file_side_effect(handle, buffer, size, bytes_read_ptr, overlapped):
            # Simulate writing partial data to the buffer
            ctypes.memmove(buffer, test_data, len(test_data))
            # Set bytes read - bytes_read_ptr is a byref() object, access its _obj
            bytes_read_ptr._obj.value = len(test_data)
            return False
            
        mock_kernel32.ReadFile.side_effect = mock_read_file_side_effect
        
        # WHEN
        error_code, data = ReadFile(mock_handle, buffer_size)
        
        # THEN
        assert error_code == ERROR_MORE_DATA
        assert data == test_data
        mock_kernel32.ReadFile.assert_called_once()
        mock_kernel32.GetLastError.assert_called_once()

    @patch("openjd.adaptor_runtime_client._win32._file_operations.kernel32")
    def test_read_file_error(self, mock_kernel32):
        """Test ReadFile operation with error."""
        # GIVEN
        mock_handle = MagicMock(spec=HANDLE)
        buffer_size = 1024
        error_code = 5  # ACCESS_DENIED
        
        # Mock ReadFile call that returns False with error
        mock_kernel32.ReadFile.return_value = False
        mock_kernel32.GetLastError.return_value = error_code
        
        # WHEN/THEN
        with pytest.raises(OSError) as exc_info:
            ReadFile(mock_handle, buffer_size)
            
        assert f"ReadFile failed with error code: {error_code}" in str(exc_info.value)
        mock_kernel32.ReadFile.assert_called_once()
        mock_kernel32.GetLastError.assert_called_once()

    @patch("openjd.adaptor_runtime_client._win32._file_operations.kernel32")
    def test_write_file_success(self, mock_kernel32):
        """Test successful WriteFile operation."""
        # GIVEN
        mock_handle = MagicMock(spec=HANDLE)
        test_data = b"Hello, World!"
        
        # Mock successful WriteFile call
        mock_kernel32.WriteFile.return_value = True
        
        def mock_write_file_side_effect(handle, data, size, bytes_written_ptr, overlapped):
            # Set bytes written - bytes_written_ptr is a byref() object, access its _obj
            bytes_written_ptr._obj.value = len(test_data)
            return True
            
        mock_kernel32.WriteFile.side_effect = mock_write_file_side_effect
        
        # WHEN
        result = WriteFile(mock_handle, test_data)
        
        # THEN
        assert result == NO_ERROR
        mock_kernel32.WriteFile.assert_called_once()

    @patch("openjd.adaptor_runtime_client._win32._file_operations.kernel32")
    def test_write_file_error(self, mock_kernel32):
        """Test WriteFile operation with error."""
        # GIVEN
        mock_handle = MagicMock(spec=HANDLE)
        test_data = b"Hello, World!"
        error_code = 5  # ACCESS_DENIED
        
        # Mock WriteFile call that returns False with error
        mock_kernel32.WriteFile.return_value = False
        mock_kernel32.GetLastError.return_value = error_code
        
        # WHEN/THEN
        with pytest.raises(OSError) as exc_info:
            WriteFile(mock_handle, test_data)
            
        assert f"WriteFile failed with error code: {error_code}" in str(exc_info.value)
        mock_kernel32.WriteFile.assert_called_once()
        mock_kernel32.GetLastError.assert_called_once()

    def test_constants_defined(self):
        """Test that required constants are properly defined."""
        # THEN
        assert ERROR_MORE_DATA == 234
        assert NO_ERROR == 0

    @patch("openjd.adaptor_runtime_client._win32._file_operations.kernel32")
    def test_read_file_empty_data(self, mock_kernel32):
        """Test ReadFile operation with empty data."""
        # GIVEN
        mock_handle = MagicMock(spec=HANDLE)
        buffer_size = 1024
        
        # Mock successful ReadFile call with no data
        mock_kernel32.ReadFile.return_value = True
        
        def mock_read_file_side_effect(handle, buffer, size, bytes_read_ptr, overlapped):
            # Set bytes read to 0 - bytes_read_ptr is a byref() object, access its _obj
            bytes_read_ptr._obj.value = 0
            return True
            
        mock_kernel32.ReadFile.side_effect = mock_read_file_side_effect
        
        # WHEN
        error_code, data = ReadFile(mock_handle, buffer_size)
        
        # THEN
        assert error_code == NO_ERROR
        assert data == b""
        mock_kernel32.ReadFile.assert_called_once()

    @patch("openjd.adaptor_runtime_client._win32._file_operations.kernel32")
    def test_write_file_empty_data(self, mock_kernel32):
        """Test WriteFile operation with empty data."""
        # GIVEN
        mock_handle = MagicMock(spec=HANDLE)
        test_data = b""
        
        # Mock successful WriteFile call
        mock_kernel32.WriteFile.return_value = True
        
        def mock_write_file_side_effect(handle, data, size, bytes_written_ptr, overlapped):
            # Set bytes written to 0 - bytes_written_ptr is a byref() object, access its _obj
            bytes_written_ptr._obj.value = 0
            return True
            
        mock_kernel32.WriteFile.side_effect = mock_write_file_side_effect
        
        # WHEN
        result = WriteFile(mock_handle, test_data)
        
        # THEN
        assert result == NO_ERROR
        mock_kernel32.WriteFile.assert_called_once()

    @patch("openjd.adaptor_runtime_client._win32._file_operations.kernel32")
    def test_read_file_large_buffer(self, mock_kernel32):
        """Test ReadFile operation with large buffer size."""
        # GIVEN
        mock_handle = MagicMock(spec=HANDLE)
        buffer_size = 65536  # 64KB
        test_data = b"A" * 1000  # 1KB of data
        
        # Mock successful ReadFile call
        mock_kernel32.ReadFile.return_value = True
        
        def mock_read_file_side_effect(handle, buffer, size, bytes_read_ptr, overlapped):
            # Simulate writing data to the buffer
            ctypes.memmove(buffer, test_data, len(test_data))
            # Set bytes read - bytes_read_ptr is a byref() object, access its _obj
            bytes_read_ptr._obj.value = len(test_data)
            return True
            
        mock_kernel32.ReadFile.side_effect = mock_read_file_side_effect
        
        # WHEN
        error_code, data = ReadFile(mock_handle, buffer_size)
        
        # THEN
        assert error_code == NO_ERROR
        assert data == test_data
        mock_kernel32.ReadFile.assert_called_once()

    @patch("openjd.adaptor_runtime_client._win32._file_operations.kernel32")
    def test_write_file_large_data(self, mock_kernel32):
        """Test WriteFile operation with large data."""
        # GIVEN
        mock_handle = MagicMock(spec=HANDLE)
        test_data = b"B" * 10000  # 10KB of data
        
        # Mock successful WriteFile call
        mock_kernel32.WriteFile.return_value = True
        
        def mock_write_file_side_effect(handle, data, size, bytes_written_ptr, overlapped):
            # Set bytes written - bytes_written_ptr is a byref() object, access its _obj
            bytes_written_ptr._obj.value = len(test_data)
            return True
            
        mock_kernel32.WriteFile.side_effect = mock_write_file_side_effect
        
        # WHEN
        result = WriteFile(mock_handle, test_data)
        
        # THEN
        assert result == NO_ERROR
        mock_kernel32.WriteFile.assert_called_once()