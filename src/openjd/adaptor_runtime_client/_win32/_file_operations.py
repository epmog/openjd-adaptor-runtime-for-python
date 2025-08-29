# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

import ctypes
import sys

from ctypes.wintypes import (
    BOOL,
    DWORD,
    HANDLE,
    LPDWORD,
    LPVOID,
    PBYTE,
)

from ctypes import POINTER, byref, c_byte, create_string_buffer  # type: ignore

# This assertion short-circuits mypy from type checking this module on platforms other than Windows
# https://mypy.readthedocs.io/en-stable/common_issues.html#python-version-and-system-platform-checks
assert sys.platform == "win32"

# =======================
# Constants
# =======================

# Ref: https://learn.microsoft.com/en-us/windows/win32/debug/system-error-codes--0-999-
ERROR_MORE_DATA = 234
NO_ERROR = 0

# =======================
# Structures/Types
# =======================

# https://learn.microsoft.com/en-us/windows/win32/api/minwinbase/ns-minwinbase-overlapped
class OVERLAPPED(ctypes.Structure):
    _fields_ = [
        ("Internal", ctypes.c_void_p),      # ULONG_PTR - pointer-sized integer
        ("InternalHigh", ctypes.c_void_p),  # ULONG_PTR - pointer-sized integer
        ("Offset", DWORD),
        ("OffsetHigh", DWORD),
        ("hEvent", HANDLE),
    ]

# Import shared kernel32 instance
from ._kernel32 import kernel32


def ReadFile(handle: HANDLE, buffer_size: int) -> tuple[int, bytes]:
    """
    Read data from a file handle using ctypes implementation of ReadFile.
    
    This function replaces win32file.ReadFile with equivalent ctypes functionality.
    
    Args:
        handle: The file handle to read from
        buffer_size: The maximum number of bytes to read
        
    Returns:
        tuple[int, bytes]: A tuple containing (error_code, data)
            - error_code: 0 for success, ERROR_MORE_DATA if more data available, other for errors
            - data: The bytes read from the file
            
    Raises:
        OSError: If the ReadFile operation fails
    """
    # Create buffer to receive data
    buffer = create_string_buffer(buffer_size)
    bytes_read = DWORD(0)
    
    # Call ReadFile
    success = kernel32.ReadFile(
        handle,
        buffer,
        buffer_size,
        byref(bytes_read),
        None  # No overlapped I/O
    )
    
    if success:
        # Success - return the data read
        return (NO_ERROR, buffer.raw[:bytes_read.value])
    else:
        # Check if it's ERROR_MORE_DATA (not a real error)
        error_code = kernel32.GetLastError()
        if error_code == ERROR_MORE_DATA:
            # More data available - return what we got
            return (ERROR_MORE_DATA, buffer.raw[:bytes_read.value])
        else:
            # Real error occurred
            raise OSError(f"ReadFile failed with error code: {error_code}")


def WriteFile(handle: HANDLE, data: bytes) -> int:
    """
    Write data to a file handle using ctypes implementation of WriteFile.
    
    This function replaces win32file.WriteFile with equivalent ctypes functionality.
    
    Args:
        handle: The file handle to write to
        data: The bytes to write to the file
        
    Returns:
        int: Error code (0 for success)
        
    Raises:
        OSError: If the WriteFile operation fails
    """
    bytes_written = DWORD(0)
    
    # Call WriteFile
    success = kernel32.WriteFile(
        handle,
        data,
        len(data),
        byref(bytes_written),
        None  # No overlapped I/O
    )
    
    if success:
        return NO_ERROR
    else:
        error_code = kernel32.GetLastError()
        raise OSError(f"WriteFile failed with error code: {error_code}")


# exports
__all__ = [
    "ReadFile",
    "WriteFile", 
    "ERROR_MORE_DATA",
    "NO_ERROR",
]