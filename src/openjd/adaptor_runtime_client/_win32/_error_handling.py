# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

import ctypes
import sys
from ctypes.wintypes import DWORD, LPSTR, LPWSTR
from ctypes import POINTER, c_char_p, c_wchar_p

# This assertion short-circuits mypy from type checking this module on platforms other than Windows
# https://mypy.readthedocs.io/en/stable/common_issues.html#python-version-and-system-platform-checks
assert sys.platform == "win32"

# =======================
# Windows Error Constants
# =======================

# Ref: https://learn.microsoft.com/en-us/windows/win32/debug/system-error-codes--0-499-
ERROR_SUCCESS = 0
ERROR_INVALID_FUNCTION = 1
ERROR_FILE_NOT_FOUND = 2
ERROR_PATH_NOT_FOUND = 3
ERROR_TOO_MANY_OPEN_FILES = 4
ERROR_ACCESS_DENIED = 5
ERROR_INVALID_HANDLE = 6
ERROR_NOT_ENOUGH_MEMORY = 8
ERROR_INVALID_DATA = 13
ERROR_OUTOFMEMORY = 14
ERROR_INVALID_DRIVE = 15
ERROR_NO_MORE_FILES = 18
ERROR_WRITE_PROTECT = 19
ERROR_BAD_UNIT = 20
ERROR_NOT_READY = 21
ERROR_BAD_COMMAND = 22
ERROR_CRC = 23
ERROR_BAD_LENGTH = 24
ERROR_SEEK = 25
ERROR_NOT_DOS_DISK = 26
ERROR_SECTOR_NOT_FOUND = 27
ERROR_OUT_OF_PAPER = 28
ERROR_WRITE_FAULT = 29
ERROR_READ_FAULT = 30
ERROR_GEN_FAILURE = 31
ERROR_SHARING_VIOLATION = 32
ERROR_LOCK_VIOLATION = 33
ERROR_WRONG_DISK = 34
ERROR_SHARING_BUFFER_EXCEEDED = 36
ERROR_HANDLE_EOF = 38
ERROR_HANDLE_DISK_FULL = 39
ERROR_NOT_SUPPORTED = 50
ERROR_REM_NOT_LIST = 51
ERROR_DUP_NAME = 52
ERROR_BAD_NETPATH = 53
ERROR_NETWORK_BUSY = 54
ERROR_DEV_NOT_EXIST = 55
ERROR_TOO_MANY_CMDS = 56
ERROR_ADAP_HDW_ERR = 57
ERROR_BAD_NET_RESP = 58
ERROR_UNEXP_NET_ERR = 59
ERROR_BAD_REM_ADAP = 60
ERROR_PRINTQ_FULL = 61
ERROR_NO_SPOOL_SPACE = 62
ERROR_PRINT_CANCELLED = 63
ERROR_NETNAME_DELETED = 64
ERROR_NETWORK_ACCESS_DENIED = 65
ERROR_BAD_DEV_TYPE = 66
ERROR_BAD_NET_NAME = 67
ERROR_TOO_MANY_NAMES = 68
ERROR_TOO_MANY_SESS = 69
ERROR_SHARING_PAUSED = 70
ERROR_REQ_NOT_ACCEP = 71
ERROR_REDIR_PAUSED = 72
ERROR_FILE_EXISTS = 80
ERROR_CANNOT_MAKE = 82
ERROR_FAIL_I24 = 83
ERROR_OUT_OF_STRUCTURES = 84
ERROR_ALREADY_ASSIGNED = 85
ERROR_INVALID_PASSWORD = 86
ERROR_INVALID_PARAMETER = 87
ERROR_NET_WRITE_FAULT = 88
ERROR_NO_PROC_SLOTS = 89
ERROR_TOO_MANY_SEMAPHORES = 100
ERROR_EXCL_SEM_ALREADY_OWNED = 101
ERROR_SEM_IS_SET = 102
ERROR_TOO_MANY_SEM_REQUESTS = 103
ERROR_INVALID_AT_INTERRUPT_TIME = 104
ERROR_SEM_OWNER_DIED = 105
ERROR_SEM_USER_LIMIT = 106
ERROR_DISK_CHANGE = 107
ERROR_DRIVE_LOCKED = 108
ERROR_BROKEN_PIPE = 109
ERROR_OPEN_FAILED = 110
ERROR_BUFFER_OVERFLOW = 111
ERROR_DISK_FULL = 112
ERROR_NO_MORE_SEARCH_HANDLES = 113
ERROR_INVALID_TARGET_HANDLE = 114
ERROR_INVALID_CATEGORY = 117
ERROR_INVALID_VERIFY_SWITCH = 118
ERROR_BAD_DRIVER_LEVEL = 119
ERROR_CALL_NOT_IMPLEMENTED = 120
ERROR_SEM_TIMEOUT = 121
ERROR_INSUFFICIENT_BUFFER = 122
ERROR_INVALID_NAME = 123
ERROR_INVALID_LEVEL = 124
ERROR_NO_VOLUME_LABEL = 125
ERROR_MOD_NOT_FOUND = 126
ERROR_PROC_NOT_FOUND = 127
ERROR_WAIT_NO_CHILDREN = 128
ERROR_CHILD_NOT_COMPLETE = 129
ERROR_DIRECT_ACCESS_HANDLE = 130
ERROR_NEGATIVE_SEEK = 131
ERROR_SEEK_ON_DEVICE = 132
ERROR_IS_JOIN_TARGET = 133
ERROR_IS_JOINED = 134
ERROR_IS_SUBSTED = 135
ERROR_NOT_JOINED = 136
ERROR_NOT_SUBSTED = 137
ERROR_JOIN_TO_JOIN = 138
ERROR_SUBST_TO_SUBST = 139
ERROR_JOIN_TO_SUBST = 140
ERROR_SUBST_TO_JOIN = 141
ERROR_BUSY_DRIVE = 142
ERROR_SAME_DRIVE = 143
ERROR_DIR_NOT_ROOT = 144
ERROR_DIR_NOT_EMPTY = 145
ERROR_IS_SUBST_PATH = 146
ERROR_IS_JOIN_PATH = 147
ERROR_PATH_BUSY = 148
ERROR_IS_SUBST_TARGET = 149
ERROR_SYSTEM_TRACE = 150
ERROR_INVALID_EVENT_COUNT = 151
ERROR_TOO_MANY_MUXWAITERS = 152
ERROR_INVALID_LIST_FORMAT = 153
ERROR_LABEL_TOO_LONG = 154
ERROR_TOO_MANY_TCBS = 155
ERROR_SIGNAL_REFUSED = 156
ERROR_DISCARDED = 157
ERROR_NOT_LOCKED = 158
ERROR_BAD_THREADID_ADDR = 159
ERROR_BAD_ARGUMENTS = 160
ERROR_BAD_PATHNAME = 161
ERROR_SIGNAL_PENDING = 162
ERROR_MAX_THRDS_REACHED = 164
ERROR_LOCK_FAILED = 167
ERROR_BUSY = 170
ERROR_DEVICE_SUPPORT_IN_PROGRESS = 171
ERROR_CANCEL_VIOLATION = 173
ERROR_ATOMIC_LOCKS_NOT_SUPPORTED = 174
ERROR_INVALID_SEGMENT_NUMBER = 180
ERROR_INVALID_ORDINAL = 182
ERROR_ALREADY_EXISTS = 183
ERROR_INVALID_FLAG_NUMBER = 186
ERROR_SEM_NOT_FOUND = 187
ERROR_INVALID_STARTING_CODESEG = 188
ERROR_INVALID_STACKSEG = 189
ERROR_INVALID_MODULETYPE = 190
ERROR_INVALID_EXE_SIGNATURE = 191
ERROR_EXE_MARKED_INVALID = 192
ERROR_BAD_EXE_FORMAT = 193
ERROR_ITERATED_DATA_EXCEEDS_64k = 194
ERROR_INVALID_MINALLOCSIZE = 195
ERROR_DYNLINK_FROM_INVALID_RING = 196
ERROR_IOPL_NOT_ENABLED = 197
ERROR_INVALID_SEGDPL = 198
ERROR_AUTODATASEG_EXCEEDS_64k = 199
ERROR_RING2SEG_MUST_BE_MOVABLE = 200
ERROR_RELOC_CHAIN_XEEDS_SEGLIM = 201
ERROR_INFLOOP_IN_RELOC_CHAIN = 202
ERROR_ENVVAR_NOT_FOUND = 203
ERROR_NO_SIGNAL_SENT = 205
ERROR_FILENAME_EXCED_RANGE = 206
ERROR_RING2_STACK_IN_USE = 207
ERROR_META_EXPANSION_TOO_LONG = 208
ERROR_INVALID_SIGNAL_NUMBER = 209
ERROR_THREAD_1_INACTIVE = 210
ERROR_LOCKED = 212
ERROR_TOO_MANY_MODULES = 214
ERROR_NESTING_NOT_ALLOWED = 215
ERROR_EXE_MACHINE_TYPE_MISMATCH = 216
ERROR_EXE_CANNOT_MODIFY_SIGNED_BINARY = 217
ERROR_EXE_CANNOT_MODIFY_STRONG_SIGNED_BINARY = 218
ERROR_FILE_CHECKED_OUT = 220
ERROR_CHECKOUT_REQUIRED = 221
ERROR_BAD_FILE_TYPE = 222
ERROR_FILE_TOO_LARGE = 223
ERROR_FORMS_AUTH_REQUIRED = 224
ERROR_VIRUS_INFECTED = 225
ERROR_VIRUS_DELETED = 226
ERROR_PIPE_LOCAL = 229
ERROR_BAD_PIPE = 230
ERROR_PIPE_BUSY = 231
ERROR_NO_DATA = 232
ERROR_PIPE_NOT_CONNECTED = 233
ERROR_MORE_DATA = 234
ERROR_VC_DISCONNECTED = 240
ERROR_INVALID_EA_NAME = 254
ERROR_EA_LIST_INCONSISTENT = 255
WAIT_TIMEOUT = 258
ERROR_NO_MORE_ITEMS = 259

# =======================
# Windows API Functions
# =======================

# Import shared kernel32 instance
from ._kernel32 import kernel32

# FormatMessage flags
# Ref: https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-formatmessagea
FORMAT_MESSAGE_ALLOCATE_BUFFER = 0x00000100
FORMAT_MESSAGE_FROM_SYSTEM = 0x00001000
FORMAT_MESSAGE_IGNORE_INSERTS = 0x00000200

# =======================
# Exception Classes
# =======================

class WindowsError(Exception):
    """
    Custom exception class to replace pywintypes.error.
    
    This class maintains compatibility with existing code that catches
    pywintypes.error and accesses its attributes.
    
    Attributes:
        winerror (int): The Windows error code
        funcname (str): The name of the function that caused the error
        strerror (str): The error message string
    """
    
    def __init__(self, winerror: int, funcname: str, strerror: str):
        """
        Initialize a WindowsError exception.
        
        Args:
            winerror: The Windows error code
            funcname: The name of the function that caused the error
            strerror: The error message string
        """
        self.winerror = winerror
        self.funcname = funcname
        self.strerror = strerror
        
        # Call parent constructor with the error message
        super().__init__(strerror)
    
    def __str__(self) -> str:
        """Return a string representation of the error."""
        return f"({self.winerror}, '{self.funcname}', '{self.strerror}')"
    
    def __repr__(self) -> str:
        """Return a detailed string representation of the error."""
        return f"WindowsError({self.winerror}, '{self.funcname}', '{self.strerror}')"

# =======================
# Utility Functions
# =======================

def GetLastError() -> int:
    """
    Get the last Windows error code.
    
    Returns:
        The last error code set by a Windows API function.
    """
    return kernel32.GetLastError()

def FormatMessage(error_code: int) -> str:
    """
    Format a Windows error code into a human-readable message.
    
    Args:
        error_code: The Windows error code to format
        
    Returns:
        A human-readable error message string
    """
    # Buffer to hold the formatted message
    buffer = ctypes.create_string_buffer(1024)
    
    # Call FormatMessageA to get the error message
    length = kernel32.FormatMessageA(
        FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS,
        None,  # lpSource
        error_code,  # dwMessageId
        0,  # dwLanguageId (0 = default)
        buffer,  # lpBuffer
        len(buffer),  # nSize
        None  # Arguments
    )
    
    if length == 0:
        # If FormatMessage fails, return a generic message
        return f"Unknown error {error_code}"
    
    # Decode the message and strip trailing whitespace
    message = buffer.value.decode('ascii', errors='replace').strip()
    return message

def raise_windows_error(funcname: str, error_code: int = None) -> None:
    """
    Raise a WindowsError with the current or specified error code.
    
    Args:
        funcname: The name of the function that caused the error
        error_code: The error code to use (if None, uses GetLastError())
        
    Raises:
        WindowsError: Always raises this exception
    """
    if error_code is None:
        error_code = GetLastError()
    
    error_message = FormatMessage(error_code)
    raise WindowsError(error_code, funcname, error_message)

def check_windows_error(result, funcname: str) -> None:
    """
    Check if a Windows API call failed and raise WindowsError if it did.
    
    This is a helper function for Windows API calls that return 0 on failure.
    
    Args:
        result: The return value from a Windows API call
        funcname: The name of the function that was called
        
    Raises:
        WindowsError: If the API call failed (result is 0 or False)
    """
    if not result:
        raise_windows_error(funcname)

# Export the main functions and classes
__all__ = [
    'WindowsError',
    'GetLastError', 
    'FormatMessage',
    'raise_windows_error',
    'check_windows_error',
    # Error constants
    'ERROR_SUCCESS',
    'ERROR_INVALID_FUNCTION',
    'ERROR_FILE_NOT_FOUND',
    'ERROR_PATH_NOT_FOUND',
    'ERROR_ACCESS_DENIED',
    'ERROR_INVALID_HANDLE',
    'ERROR_NOT_ENOUGH_MEMORY',
    'ERROR_INVALID_DATA',
    'ERROR_BROKEN_PIPE',
    'ERROR_BUFFER_OVERFLOW',
    'ERROR_INSUFFICIENT_BUFFER',
    'ERROR_PIPE_NOT_CONNECTED',
    'ERROR_MORE_DATA',
    'ERROR_NO_DATA',
    'ERROR_PIPE_BUSY',
    'ERROR_PIPE_LOCAL',
    'ERROR_BAD_PIPE',
    'WAIT_TIMEOUT',
]