# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

import ctypes
import sys

from ctypes.wintypes import (
    BOOL,
    DWORD,
    HANDLE,
    LONG,
    LPCSTR,
    LPCWSTR,
    LPDWORD,
    LPVOID,
    LPWSTR,
    PBYTE,
    PDWORD,
    PULONG,
    PHANDLE,
    ULONG,
    WORD,
)

from ctypes import POINTER, byref, c_byte, c_size_t, c_void_p, pointer  # type: ignore
from collections.abc import Sequence

# This assertion short-circuits mypy from type checking this module on platforms other than Windows
# https://mypy.readthedocs.io/en/stable/common_issues.html#python-version-and-system-platform-checks
assert sys.platform == "win32"

# Import constants from the centralized constants module
from ._constants import (
    INVALID_HANDLE_VALUE,
    ERROR_FILE_NOT_FOUND,
    ERROR_BROKEN_PIPE,
    ERROR_PIPE_NOT_CONNECTED,
    ERROR_PIPE_BUSY,
    ERROR_INVALID_HANDLE,
    GENERIC_WRITE,
    GENERIC_READ,
    OPEN_EXISTING,
    PIPE_ACCESS_DUPLEX,
    PIPE_TYPE_MESSAGE,
    PIPE_READMODE_MESSAGE,
    PIPE_WAIT,
)

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

# exports
CloseHandle = kernel32.CloseHandle
ConnectNamedPipe = kernel32.ConnectNamedPipe
CreateFileA = kernel32.CreateFileA
CreateNamedPipeA = kernel32.CreateNamedPipeA
DisconnectNamedPipe = kernel32.DisconnectNamedPipe
SetNamedPipeHandleState = kernel32.SetNamedPipeHandleState

# Export functions and constants
__all__ = [
    "CloseHandle",
    "ConnectNamedPipe", 
    "CreateFileA",
    "CreateNamedPipeA",
    "DisconnectNamedPipe",
    "SetNamedPipeHandleState",
    "INVALID_HANDLE_VALUE",
    "ERROR_FILE_NOT_FOUND",
    "ERROR_BROKEN_PIPE", 
    "ERROR_PIPE_NOT_CONNECTED",
    "ERROR_PIPE_BUSY",
    "ERROR_INVALID_HANDLE",
    "GENERIC_WRITE",
    "GENERIC_READ",
    "OPEN_EXISTING",
    "PIPE_ACCESS_DUPLEX",
    "PIPE_TYPE_MESSAGE",
    "PIPE_READMODE_MESSAGE",
    "PIPE_WAIT",
]
