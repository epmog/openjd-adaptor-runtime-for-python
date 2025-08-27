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

from ctypes import POINTER, WinError, byref, c_byte, c_size_t, c_void_p, pointer  # type: ignore
from collections.abc import Sequence

# This assertion short-circuits mypy from type checking this module on platforms other than Windows
# https://mypy.readthedocs.io/en/stable/common_issues.html#python-version-and-system-platform-checks
assert sys.platform == "win32"

# =======================
# Constants
# =======================

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
        ("Internal", PULONG),
        ("InternalHigh", PULONG),
        ("Offset", DWORD),
        ("OffsetHigh", DWORD),
        ("hEvent", HANDLE),
    ]

# ---------
# From: Kernel32.dll
# ---------
kernel32 = ctypes.WinDLL("Kernel32.dll")

# https://learn.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-closehandle
kernel32.CloseHandle.restype = BOOL
kernel32.CloseHandle.argtypes = [HANDLE]  # [in] hObject

# https://learn.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-connectnamedpipe
kernel32.ConnectNamedPipe.restype = BOOL
kernel32.ConnectNamedPipe.argtypes = [
    HANDLE, # [in] hNamedPipe
    POINTER(OVERLAPPED), # [in, out, optional] lpOverlapped
]

# https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-createnamedpipea
kernel32.CreateNamedPipeA.restype = HANDLE
kernel32.CreateNamedPipeA.argtypes = [
    LPCSTR, # [in] lpName
    DWORD, # [in] dwOpenMode
    DWORD, # [in] dwPipeMode
    DWORD, # [in] nMaxInstances
    DWORD, # [in] nOutBufferSize
    DWORD, # [in] nInBufferSize
    DWORD, # [in] nDefaultTimeOut
    POINTER(SECURITY_ATTRIBUTES), # [in, optional] lpSecurityAttributes
]

# https://learn.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-disconnectnamedpipe
kernel32.DisconnectNamedPipe.restype = BOOL
kernel32.DisconnectNamedPipe.argtypes = [
    HANDLE, # [in] hNamedPipe
]

# exports
CloseHandle = kernel32.CloseHandle
ConnectNamedPipe = kernel32.ConnectNamedPipe
CreateNamedPipeA = kernel32.CreateNamedPipeA
DisconnectNamedPipe = kernel32.DisconnectNamedPipe
