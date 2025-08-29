# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

"""
Shared kernel32 DLL instance and function definitions.

This module provides a single kernel32 instance to avoid conflicts
between multiple modules defining the same DLL and function signatures.
"""

import ctypes
import sys
from ctypes.wintypes import (
    BOOL,
    DWORD,
    HANDLE,
    LPDWORD,
    LPVOID,
)
from ctypes import POINTER

# This assertion short-circuits mypy from type checking this module on platforms other than Windows
assert sys.platform == "win32"

# =======================
# Shared Kernel32 Instance
# =======================

# Single kernel32 instance to be used by all modules
kernel32 = ctypes.WinDLL("Kernel32.dll")

# =======================
# Function Signatures
# =======================

# https://learn.microsoft.com/en-us/windows/win32/api/errhandlingapi/nf-errhandlingapi-getlasterror
kernel32.GetLastError.restype = DWORD
kernel32.GetLastError.argtypes = []

# https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-formatmessagea
kernel32.FormatMessageA.restype = DWORD
kernel32.FormatMessageA.argtypes = [
    DWORD,  # [in] dwFlags
    ctypes.c_void_p,  # [in, optional] lpSource
    DWORD,  # [in] dwMessageId
    DWORD,  # [in] dwLanguageId
    ctypes.c_char_p,  # [out] lpBuffer
    DWORD,  # [in] nSize
    ctypes.c_void_p,  # [in, optional] Arguments
]

# https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-formatmessagew
kernel32.FormatMessageW.restype = DWORD
kernel32.FormatMessageW.argtypes = [
    DWORD,  # [in] dwFlags
    ctypes.c_void_p,  # [in, optional] lpSource
    DWORD,  # [in] dwMessageId
    DWORD,  # [in] dwLanguageId
    ctypes.c_wchar_p,  # [out] lpBuffer
    DWORD,  # [in] nSize
    ctypes.c_void_p,  # [in, optional] Arguments
]

# https://learn.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-closehandle
kernel32.CloseHandle.restype = BOOL
kernel32.CloseHandle.argtypes = [HANDLE]

# https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-readfile
kernel32.ReadFile.restype = BOOL
kernel32.ReadFile.argtypes = [
    HANDLE,  # [in] hFile
    LPVOID,  # [out] lpBuffer
    DWORD,   # [in] nNumberOfBytesToRead
    LPDWORD, # [out, optional] lpNumberOfBytesRead
    ctypes.c_void_p, # [in, out, optional] lpOverlapped (simplified)
]

# https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-writefile
kernel32.WriteFile.restype = BOOL
kernel32.WriteFile.argtypes = [
    HANDLE,  # [in] hFile
    LPVOID,  # [in] lpBuffer
    DWORD,   # [in] nNumberOfBytesToWrite
    LPDWORD, # [out, optional] lpNumberOfBytesWritten
    ctypes.c_void_p, # [in, out, optional] lpOverlapped (simplified)
]

# https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-flushfilebuffers
kernel32.FlushFileBuffers.restype = BOOL
kernel32.FlushFileBuffers.argtypes = [
    HANDLE,  # [in] hFile
]

# https://learn.microsoft.com/en-us/windows/win32/api/heapapi/nf-heapapi-localfree
kernel32.LocalFree.restype = ctypes.c_void_p
kernel32.LocalFree.argtypes = [ctypes.c_void_p]

# https://learn.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-connectnamedpipe
kernel32.ConnectNamedPipe.restype = BOOL
kernel32.ConnectNamedPipe.argtypes = [
    HANDLE, # [in] hNamedPipe
    ctypes.c_void_p, # [in, out, optional] lpOverlapped (simplified)
]

# learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilea
kernel32.CreateFileA.restype = HANDLE
kernel32.CreateFileA.argtypes = [
    ctypes.c_char_p, # [in] lpFileName
    DWORD, # [in] dwDesiredAccess
    DWORD, # [in] dwShareMode
    ctypes.c_void_p, # [in, optional] lpSecurityAttributes (simplified)
    DWORD, # [in] dwCreationDisposition
    DWORD, # [in] dwFlagsAndAttributes
    HANDLE, # [in, optional] hTemplateFile
]

# https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-createnamedpipea
kernel32.CreateNamedPipeA.restype = HANDLE
kernel32.CreateNamedPipeA.argtypes = [
    ctypes.c_char_p, # [in] lpName
    DWORD, # [in] dwOpenMode
    DWORD, # [in] dwPipeMode
    DWORD, # [in] nMaxInstances
    DWORD, # [in] nOutBufferSize
    DWORD, # [in] nInBufferSize
    DWORD, # [in] nDefaultTimeOut
    ctypes.c_void_p, # [in, optional] lpSecurityAttributes (simplified)
]

# https://learn.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-disconnectnamedpipe
kernel32.DisconnectNamedPipe.restype = BOOL
kernel32.DisconnectNamedPipe.argtypes = [
    HANDLE, # [in] hNamedPipe
]

# https://learn.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-setnamedpipehandlestate
kernel32.SetNamedPipeHandleState.restype = BOOL
kernel32.SetNamedPipeHandleState.argtypes = [
    HANDLE, # [in] hNamedPipe
    LPDWORD, # [in, optional] lpMode
    LPDWORD, # [in, optional] lpMaxCollectionCount
    LPDWORD, # [in, optional] lpCollectDataTimeout
]

# Export the shared kernel32 instance
__all__ = ["kernel32"]