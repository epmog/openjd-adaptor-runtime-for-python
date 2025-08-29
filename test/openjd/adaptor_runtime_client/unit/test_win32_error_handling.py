# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

import pytest
import sys
from unittest.mock import patch, MagicMock

# Skip all tests if not on Windows
pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific tests")

if sys.platform == "win32":
    from openjd.adaptor_runtime_client._win32._error_handling import (
        WindowsError,
        GetLastError,
        FormatMessage,
        raise_windows_error,
        check_windows_error,
        ERROR_FILE_NOT_FOUND,
        ERROR_ACCESS_DENIED,
        ERROR_BROKEN_PIPE,
        ERROR_PIPE_NOT_CONNECTED,
        ERROR_INVALID_HANDLE,
    )


class TestWindowsError:
    """Test the WindowsError exception class."""
    
    def test_windows_error_initialization(self):
        """Test that WindowsError initializes correctly with all attributes."""
        # GIVEN
        winerror = 2
        funcname = "CreateFileA"
        strerror = "The system cannot find the file specified."
        
        # WHEN
        error = WindowsError(winerror, funcname, strerror)
        
        # THEN
        assert error.winerror == winerror
        assert error.funcname == funcname
        assert error.strerror == strerror
        assert str(error) == f"({winerror}, '{funcname}', '{strerror}')"
    
    def test_windows_error_str_representation(self):
        """Test the string representation of WindowsError."""
        # GIVEN
        error = WindowsError(5, "OpenFile", "Access is denied.")
        
        # WHEN
        str_repr = str(error)
        
        # THEN
        assert str_repr == "(5, 'OpenFile', 'Access is denied.')"
    
    def test_windows_error_repr_representation(self):
        """Test the repr representation of WindowsError."""
        # GIVEN
        error = WindowsError(5, "OpenFile", "Access is denied.")
        
        # WHEN
        repr_str = repr(error)
        
        # THEN
        assert repr_str == "WindowsError(5, 'OpenFile', 'Access is denied.')"
    
    def test_windows_error_inheritance(self):
        """Test that WindowsError inherits from Exception."""
        # GIVEN
        error = WindowsError(1, "TestFunc", "Test error")
        
        # THEN
        assert isinstance(error, Exception)
    
    def test_windows_error_compatibility_with_pywintypes_error(self):
        """Test that WindowsError has the same attributes as pywintypes.error."""
        # GIVEN
        error = WindowsError(109, "ReadFile", "The pipe has been ended.")
        
        # THEN - Should have the same attributes that pywintypes.error has
        assert hasattr(error, 'winerror')
        assert hasattr(error, 'funcname')
        assert hasattr(error, 'strerror')
        
        # Should be able to access attributes the same way
        assert error.winerror == 109
        assert error.funcname == "ReadFile"
        assert error.strerror == "The pipe has been ended."


class TestErrorConstants:
    """Test that error constants are defined correctly."""
    
    def test_error_constants_exist(self):
        """Test that common error constants are defined."""
        # THEN
        assert ERROR_FILE_NOT_FOUND == 2
        assert ERROR_ACCESS_DENIED == 5
        assert ERROR_BROKEN_PIPE == 109
        assert ERROR_PIPE_NOT_CONNECTED == 233
        assert ERROR_INVALID_HANDLE == 6


class TestGetLastError:
    """Test the GetLastError function."""
    
    @patch('openjd.adaptor_runtime_client._win32._error_handling.kernel32')
    def test_get_last_error_calls_kernel32(self, mock_kernel32):
        """Test that GetLastError calls the kernel32 function."""
        # GIVEN
        mock_kernel32.GetLastError.return_value = 123
        
        # WHEN
        result = GetLastError()
        
        # THEN
        assert result == 123
        mock_kernel32.GetLastError.assert_called_once()
    
    @patch('openjd.adaptor_runtime_client._win32._error_handling.kernel32')
    def test_get_last_error_returns_zero_on_success(self, mock_kernel32):
        """Test that GetLastError returns 0 when no error occurred."""
        # GIVEN
        mock_kernel32.GetLastError.return_value = 0
        
        # WHEN
        result = GetLastError()
        
        # THEN
        assert result == 0


class TestFormatMessage:
    """Test the FormatMessage function."""
    
    @patch('openjd.adaptor_runtime_client._win32._error_handling.kernel32')
    @patch('openjd.adaptor_runtime_client._win32._error_handling.ctypes.create_string_buffer')
    def test_format_message_success(self, mock_create_buffer, mock_kernel32):
        """Test FormatMessage when it successfully formats a message."""
        # GIVEN
        error_code = 2
        expected_message = "The system cannot find the file specified."
        
        # Mock the buffer
        mock_buffer = MagicMock()
        mock_buffer.value = expected_message.encode('ascii')
        mock_create_buffer.return_value = mock_buffer
        
        # Mock FormatMessageA to return success
        mock_kernel32.FormatMessageA.return_value = len(expected_message)
        
        # WHEN
        result = FormatMessage(error_code)
        
        # THEN
        assert result == expected_message
        mock_kernel32.FormatMessageA.assert_called_once()
    
    @patch('openjd.adaptor_runtime_client._win32._error_handling.kernel32')
    @patch('openjd.adaptor_runtime_client._win32._error_handling.ctypes.create_string_buffer')
    def test_format_message_failure(self, mock_create_buffer, mock_kernel32):
        """Test FormatMessage when it fails to format a message."""
        # GIVEN
        error_code = 99999  # Invalid error code
        
        # Mock FormatMessageA to return failure (0)
        mock_kernel32.FormatMessageA.return_value = 0
        
        # WHEN
        result = FormatMessage(error_code)
        
        # THEN
        assert result == f"Unknown error {error_code}"
    
    @patch('openjd.adaptor_runtime_client._win32._error_handling.kernel32')
    @patch('openjd.adaptor_runtime_client._win32._error_handling.ctypes.create_string_buffer')
    def test_format_message_strips_whitespace(self, mock_create_buffer, mock_kernel32):
        """Test that FormatMessage strips trailing whitespace from messages."""
        # GIVEN
        error_code = 5
        message_with_whitespace = "Access is denied.\r\n"
        expected_message = "Access is denied."
        
        # Mock the buffer
        mock_buffer = MagicMock()
        mock_buffer.value = message_with_whitespace.encode('ascii')
        mock_create_buffer.return_value = mock_buffer
        
        # Mock FormatMessageA to return success
        mock_kernel32.FormatMessageA.return_value = len(message_with_whitespace)
        
        # WHEN
        result = FormatMessage(error_code)
        
        # THEN
        assert result == expected_message


class TestRaiseWindowsError:
    """Test the raise_windows_error function."""
    
    @patch('openjd.adaptor_runtime_client._win32._error_handling.GetLastError')
    @patch('openjd.adaptor_runtime_client._win32._error_handling.FormatMessage')
    def test_raise_windows_error_with_current_error(self, mock_format_message, mock_get_last_error):
        """Test raise_windows_error when no error code is provided."""
        # GIVEN
        funcname = "CreateFileA"
        error_code = 2
        error_message = "The system cannot find the file specified."
        
        mock_get_last_error.return_value = error_code
        mock_format_message.return_value = error_message
        
        # WHEN/THEN
        with pytest.raises(WindowsError) as exc_info:
            raise_windows_error(funcname)
        
        error = exc_info.value
        assert error.winerror == error_code
        assert error.funcname == funcname
        assert error.strerror == error_message
    
    @patch('openjd.adaptor_runtime_client._win32._error_handling.FormatMessage')
    def test_raise_windows_error_with_specific_error(self, mock_format_message):
        """Test raise_windows_error when a specific error code is provided."""
        # GIVEN
        funcname = "WriteFile"
        error_code = 5
        error_message = "Access is denied."
        
        mock_format_message.return_value = error_message
        
        # WHEN/THEN
        with pytest.raises(WindowsError) as exc_info:
            raise_windows_error(funcname, error_code)
        
        error = exc_info.value
        assert error.winerror == error_code
        assert error.funcname == funcname
        assert error.strerror == error_message


class TestCheckWindowsError:
    """Test the check_windows_error function."""
    
    def test_check_windows_error_success(self):
        """Test check_windows_error when the result indicates success."""
        # GIVEN
        result = True  # Success
        funcname = "CreateFileA"
        
        # WHEN/THEN - Should not raise an exception
        check_windows_error(result, funcname)
    
    @patch('openjd.adaptor_runtime_client._win32._error_handling.raise_windows_error')
    def test_check_windows_error_failure_false(self, mock_raise_error):
        """Test check_windows_error when the result is False."""
        # GIVEN
        result = False  # Failure
        funcname = "CreateFileA"
        
        # WHEN
        check_windows_error(result, funcname)
        
        # THEN
        mock_raise_error.assert_called_once_with(funcname)
    
    @patch('openjd.adaptor_runtime_client._win32._error_handling.raise_windows_error')
    def test_check_windows_error_failure_zero(self, mock_raise_error):
        """Test check_windows_error when the result is 0."""
        # GIVEN
        result = 0  # Failure
        funcname = "WriteFile"
        
        # WHEN
        check_windows_error(result, funcname)
        
        # THEN
        mock_raise_error.assert_called_once_with(funcname)
    
    def test_check_windows_error_success_nonzero(self):
        """Test check_windows_error when the result is a non-zero number."""
        # GIVEN
        result = 42  # Success (non-zero)
        funcname = "ReadFile"
        
        # WHEN/THEN - Should not raise an exception
        check_windows_error(result, funcname)


class TestCompatibilityWithPywin32:
    """Test compatibility with existing pywintypes.error usage patterns."""
    
    def test_exception_handling_pattern(self):
        """Test that WindowsError can be used in the same exception handling patterns as pywintypes.error."""
        # GIVEN
        error = WindowsError(ERROR_BROKEN_PIPE, "ReadFile", "The pipe has been ended.")
        
        # WHEN/THEN - Should be able to catch and examine like pywintypes.error
        try:
            raise error
        except WindowsError as e:
            assert e.winerror == ERROR_BROKEN_PIPE
            assert e.funcname == "ReadFile"
            assert "pipe" in e.strerror.lower()
    
    def test_error_code_checking_pattern(self):
        """Test that error code checking works the same as with pywintypes.error."""
        # GIVEN
        error = WindowsError(ERROR_PIPE_NOT_CONNECTED, "WriteFile", "The pipe is not connected.")
        
        # WHEN/THEN - Should be able to check error codes like with pywintypes.error
        try:
            raise error
        except WindowsError as e:
            if e.winerror == ERROR_PIPE_NOT_CONNECTED:
                # This is the expected pattern from existing code
                assert True
            else:
                pytest.fail("Error code checking pattern failed")
    
    def test_multiple_error_code_checking(self):
        """Test checking multiple error codes like in existing codebase."""
        # GIVEN
        error = WindowsError(ERROR_BROKEN_PIPE, "ReadFile", "The pipe has been ended.")
        
        # WHEN/THEN - Should work with multiple error code checks
        try:
            raise error
        except WindowsError as e:
            if e.winerror in [ERROR_BROKEN_PIPE, ERROR_PIPE_NOT_CONNECTED]:
                # This pattern is used in the existing codebase
                assert True
            else:
                pytest.fail("Multiple error code checking pattern failed")