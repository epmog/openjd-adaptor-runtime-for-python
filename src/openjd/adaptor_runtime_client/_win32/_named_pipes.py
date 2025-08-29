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

# =======================
# Constants
# =======================

# Ref: https://learn.microsoft.com/en-us/windows/win32/winprog/windows-data-types
INVALID_HANDLE_VALUE = -1

# Ref: https://learn.microsoft.com/en-us/windows/win32/debug/system-error-codes--0-999-
ERROR_FILE_NOT_FOUND = 2
ERROR_BROKEN_PIPE = 109
ERROR_PIPE_NOT_CONNECTED = 233
ERROR_PIPE_BUSY = 231
ERROR_INVALID_HANDLE = 6

# Ref: https://learn.microsoft.com/en-us/windows/win32/secauthz/generic-access-rights
GENERIC_WRITE = 0x40000000
GENERIC_READ = 0x80000000

# Ref: https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilea
OPEN_EXISTING = 3

# Ref: https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-createnamedpipea
PIPE_ACCESS_DUPLEX = 0x00000003

PIPE_TYPE_MESSAGE = 0x00000004
PIPE_READMODE_MESSAGE = 0x00000002
PIPE_WAIT = 0x00000000

# =======================
# Structures/Types
# =======================

# https://learn.microsoft.com/en-us/windows/win32/api/wtypesbase/ns-wtypesbase-security_attributes
class SECURITY_ATTRIBUTES(ctypes.Structure):
    _fields_ = [("nLength", DWORD), ("lpSecurityDescriptor", LPVOID), ("bInheritHandle", BOOL)]

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

# Export constants
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
