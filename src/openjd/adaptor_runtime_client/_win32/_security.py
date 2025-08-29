# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

import ctypes
import sys
from ctypes.wintypes import (
    BOOL,
    BYTE,
    DWORD,
    HANDLE,
    LPCSTR,
    LPCWSTR,
    LPSTR,
    LPWSTR,
    PDWORD,
    PULONG,
    ULONG,
    WORD,
)
from ctypes import POINTER, Structure, Union, c_char_p, c_void_p, c_wchar_p, sizeof

from ._error_handling import WindowsError, GetLastError, FormatMessage, raise_windows_error

# This assertion short-circuits mypy from type checking this module on platforms other than Windows
# https://mypy.readthedocs.io/en/stable/common_issues.html#python-version-and-system-platform-checks
assert sys.platform == "win32"

# =======================
# Security Constants
# =======================

# Ref: https://learn.microsoft.com/en-us/windows/win32/secauthz/access-control-lists
ACL_REVISION = 2
ACL_REVISION_DS = 4

# Ref: https://learn.microsoft.com/en-us/windows/win32/secauthz/security-descriptor-definition-language
SECURITY_DESCRIPTOR_REVISION = 1

# Ref: https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-sid
SID_REVISION = 1
SID_MAX_SUB_AUTHORITIES = 15

# Ref: https://learn.microsoft.com/en-us/windows/win32/secauthz/sid-components
SECURITY_NULL_SID_AUTHORITY = 0
SECURITY_WORLD_SID_AUTHORITY = 1
SECURITY_LOCAL_SID_AUTHORITY = 2
SECURITY_CREATOR_SID_AUTHORITY = 3
SECURITY_NON_UNIQUE_AUTHORITY = 4
SECURITY_NT_AUTHORITY = 5

# Ref: https://learn.microsoft.com/en-us/windows/win32/api/accctrl/ne-accctrl-se_object_type
SE_FILE_OBJECT = 1
SE_SERVICE = 2
SE_PRINTER = 3
SE_REGISTRY_KEY = 4
SE_LMSHARE = 5
SE_KERNEL_OBJECT = 6
SE_WINDOW_OBJECT = 7
SE_DS_OBJECT = 8
SE_DS_OBJECT_ALL = 9
SE_PROVIDER_DEFINED_OBJECT = 10
SE_WMIGUID_OBJECT = 11
SE_REGISTRY_WOW64_32KEY = 12
SE_REGISTRY_WOW64_64KEY = 13

# Ref: https://learn.microsoft.com/en-us/windows/win32/secauthz/access-mask
OWNER_SECURITY_INFORMATION = 0x00000001
GROUP_SECURITY_INFORMATION = 0x00000002
DACL_SECURITY_INFORMATION = 0x00000004
SACL_SECURITY_INFORMATION = 0x00000008

# Ref: https://learn.microsoft.com/en-us/windows/win32/api/winnt/ne-winnt-sid_name_use
SidTypeUser = 1
SidTypeGroup = 2
SidTypeDomain = 3
SidTypeAlias = 4
SidTypeWellKnownGroup = 5
SidTypeDeletedAccount = 6
SidTypeInvalid = 7
SidTypeUnknown = 8
SidTypeComputer = 9
SidTypeLabel = 10

# =======================
# Security Structures
# =======================

# Ref: https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-sid_identifier_authority
class SID_IDENTIFIER_AUTHORITY(Structure):
    _fields_ = [
        ("Value", ctypes.c_ubyte * 6),  # BYTE should be unsigned
    ]

# Ref: https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-sid
class SID(Structure):
    _pack_ = 1  # Pack structure to avoid padding
    _fields_ = [
        ("Revision", ctypes.c_ubyte),        # BYTE should be unsigned
        ("SubAuthorityCount", ctypes.c_ubyte), # BYTE should be unsigned
        ("IdentifierAuthority", SID_IDENTIFIER_AUTHORITY),
        ("SubAuthority", DWORD * SID_MAX_SUB_AUTHORITIES),
    ]

# Ref: https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-acl
class ACL(Structure):
    _pack_ = 1  # Pack structure to avoid padding
    _fields_ = [
        ("AclRevision", ctypes.c_ubyte),  # BYTE should be unsigned
        ("Sbz1", ctypes.c_ubyte),         # BYTE should be unsigned
        ("AclSize", WORD),
        ("AceCount", WORD),
        ("Sbz2", WORD),
    ]

# Ref: https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-security_descriptor
class SECURITY_DESCRIPTOR(Structure):
    _pack_ = 1  # Pack structure to avoid padding
    _fields_ = [
        ("Revision", ctypes.c_ubyte),  # BYTE should be unsigned
        ("Sbz1", ctypes.c_ubyte),      # BYTE should be unsigned
        ("Control", WORD),
        ("Owner", POINTER(SID)),
        ("Group", POINTER(SID)),
        ("Sacl", POINTER(ACL)),
        ("Dacl", POINTER(ACL)),
    ]

# Ref: https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-access_allowed_ace
class ACCESS_ALLOWED_ACE(Structure):
    _pack_ = 1  # Pack structure to avoid padding
    _fields_ = [
        ("Header", ctypes.c_ubyte * 4),  # ACE_HEADER - BYTE should be unsigned
        ("Mask", DWORD),
        ("SidStart", DWORD),  # First DWORD of SID
    ]

# Ref: https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-access_denied_ace
class ACCESS_DENIED_ACE(Structure):
    _pack_ = 1  # Pack structure to avoid padding
    _fields_ = [
        ("Header", ctypes.c_ubyte * 4),  # ACE_HEADER - BYTE should be unsigned
        ("Mask", DWORD),
        ("SidStart", DWORD),  # First DWORD of SID
    ]

# =======================
# Type Aliases
# =======================

PSID = POINTER(SID)
PACL = POINTER(ACL)
PSECURITY_DESCRIPTOR = POINTER(SECURITY_DESCRIPTOR)
PSID_NAME_USE = POINTER(DWORD)

# =======================
# Windows API Functions
# =======================

# ---------
# From: Advapi32.dll
# ---------
advapi32 = ctypes.WinDLL("Advapi32.dll")

# https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-lookupaccountnamea
advapi32.LookupAccountNameA.restype = BOOL
advapi32.LookupAccountNameA.argtypes = [
    LPCSTR,  # [in, optional] lpSystemName
    LPCSTR,  # [in] lpAccountName
    PSID,    # [out, optional] Sid
    PDWORD,  # [in, out] cbSid
    LPSTR,   # [out, optional] ReferencedDomainName
    PDWORD,  # [in, out] cchReferencedDomainName
    PSID_NAME_USE,  # [out] peUse
]

# https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-lookupaccountnamew
advapi32.LookupAccountNameW.restype = BOOL
advapi32.LookupAccountNameW.argtypes = [
    LPCWSTR,  # [in, optional] lpSystemName
    LPCWSTR,  # [in] lpAccountName
    PSID,     # [out, optional] Sid
    PDWORD,   # [in, out] cbSid
    LPWSTR,   # [out, optional] ReferencedDomainName
    PDWORD,   # [in, out] cchReferencedDomainName
    PSID_NAME_USE,  # [out] peUse
]

# https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-lookupaccountsida
advapi32.LookupAccountSidA.restype = BOOL
advapi32.LookupAccountSidA.argtypes = [
    LPCSTR,  # [in, optional] lpSystemName
    PSID,    # [in] lpSid
    LPSTR,   # [out, optional] lpName
    PDWORD,  # [in, out] cchName
    LPSTR,   # [out, optional] lpReferencedDomainName
    PDWORD,  # [in, out] cchReferencedDomainName
    PSID_NAME_USE,  # [out] peUse
]

# https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-lookupaccountsidw
advapi32.LookupAccountSidW.restype = BOOL
advapi32.LookupAccountSidW.argtypes = [
    LPCWSTR,  # [in, optional] lpSystemName
    PSID,     # [in] lpSid
    LPWSTR,   # [out, optional] lpName
    PDWORD,   # [in, out] cchName
    LPWSTR,   # [out, optional] lpReferencedDomainName
    PDWORD,   # [in, out] cchReferencedDomainName
    PSID_NAME_USE,  # [out] peUse
]

# https://learn.microsoft.com/en-us/windows/win32/api/sddl/nf-sddl-convertstringsidtosida
advapi32.ConvertStringSidToSidA.restype = BOOL
advapi32.ConvertStringSidToSidA.argtypes = [
    LPCSTR,  # [in] StringSid
    POINTER(ctypes.c_void_p),  # [out] Sid - pointer to receive allocated SID
]

# https://learn.microsoft.com/en-us/windows/win32/api/sddl/nf-sddl-convertstringsidtosidw
advapi32.ConvertStringSidToSidW.restype = BOOL
advapi32.ConvertStringSidToSidW.argtypes = [
    LPCWSTR,  # [in] StringSid
    POINTER(ctypes.c_void_p),  # [out] Sid - pointer to receive allocated SID
]

# https://learn.microsoft.com/en-us/windows/win32/api/sddl/nf-sddl-convertsidtostringsida
advapi32.ConvertSidToStringSidA.restype = BOOL
advapi32.ConvertSidToStringSidA.argtypes = [
    PSID,  # [in] Sid
    POINTER(LPSTR),  # [out] StringSid
]

# https://learn.microsoft.com/en-us/windows/win32/api/sddl/nf-sddl-convertsidtostringsidw
advapi32.ConvertSidToStringSidW.restype = BOOL
advapi32.ConvertSidToStringSidW.argtypes = [
    PSID,  # [in] Sid
    POINTER(LPWSTR),  # [out] StringSid
]

# https://learn.microsoft.com/en-us/windows/win32/api/aclapi/nf-aclapi-getfilesecuritya
advapi32.GetFileSecurityA.restype = BOOL
advapi32.GetFileSecurityA.argtypes = [
    LPCSTR,  # [in] lpFileName
    DWORD,   # [in] RequestedInformation
    PSECURITY_DESCRIPTOR,  # [out, optional] pSecurityDescriptor
    DWORD,   # [in] nLength
    PDWORD,  # [out] lpnLengthNeeded
]

# https://learn.microsoft.com/en-us/windows/win32/api/aclapi/nf-aclapi-getfilesecurityw
advapi32.GetFileSecurityW.restype = BOOL
advapi32.GetFileSecurityW.argtypes = [
    LPCWSTR,  # [in] lpFileName
    DWORD,    # [in] RequestedInformation
    PSECURITY_DESCRIPTOR,  # [out, optional] pSecurityDescriptor
    DWORD,    # [in] nLength
    PDWORD,   # [out] lpnLengthNeeded
]

# https://learn.microsoft.com/en-us/windows/win32/api/aclapi/nf-aclapi-setfilesecuritya
advapi32.SetFileSecurityA.restype = BOOL
advapi32.SetFileSecurityA.argtypes = [
    LPCSTR,  # [in] lpFileName
    DWORD,   # [in] SecurityInformation
    PSECURITY_DESCRIPTOR,  # [in] pSecurityDescriptor
]

# https://learn.microsoft.com/en-us/windows/win32/api/aclapi/nf-aclapi-setfilesecurityw
advapi32.SetFileSecurityW.restype = BOOL
advapi32.SetFileSecurityW.argtypes = [
    LPCWSTR,  # [in] lpFileName
    DWORD,    # [in] SecurityInformation
    PSECURITY_DESCRIPTOR,  # [in] pSecurityDescriptor
]

# https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-addaccessallowedace
advapi32.AddAccessAllowedAce.restype = BOOL
advapi32.AddAccessAllowedAce.argtypes = [
    PACL,   # [in, out] pAcl
    DWORD,  # [in] dwAceRevision
    DWORD,  # [in] AccessMask
    PSID,   # [in] pSid
]

# https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-addaccessdeniedace
advapi32.AddAccessDeniedAce.restype = BOOL
advapi32.AddAccessDeniedAce.argtypes = [
    PACL,   # [in, out] pAcl
    DWORD,  # [in] dwAceRevision
    DWORD,  # [in] AccessMask
    PSID,   # [in] pSid
]

# https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-initializeacl
advapi32.InitializeAcl.restype = BOOL
advapi32.InitializeAcl.argtypes = [
    PACL,   # [out] pAcl
    DWORD,  # [in] nAclLength
    DWORD,  # [in] dwAclRevision
]

# Import shared kernel32 instance
from ._kernel32 import kernel32

# =======================
# High-Level Functions
# =======================

def LookupAccountName(account_name: str, system_name: str = None) -> tuple[bytes, str, int]:
    """
    Look up the SID for a given account name.
    
    Args:
        account_name: The account name to look up
        system_name: The system name (None for local system)
        
    Returns:
        A tuple of (sid_bytes, domain_name, sid_name_use)
        
    Raises:
        WindowsError: If the lookup fails
    """
    # Convert strings to bytes for the A version
    account_name_bytes = account_name.encode('utf-8')
    system_name_bytes = system_name.encode('utf-8') if system_name else None
    
    # First call to get required buffer sizes
    sid_size = DWORD(0)
    domain_size = DWORD(0)
    sid_name_use = DWORD(0)
    
    result = advapi32.LookupAccountNameA(
        system_name_bytes,
        account_name_bytes,
        None,  # Sid buffer (None to get size)
        ctypes.byref(sid_size),
        None,  # Domain buffer (None to get size)
        ctypes.byref(domain_size),
        ctypes.byref(sid_name_use)
    )
    
    # The first call should fail with ERROR_INSUFFICIENT_BUFFER
    if result:
        raise WindowsError(0, "LookupAccountNameA", "Unexpected success on size query")
    
    error_code = GetLastError()
    if error_code != 122:  # ERROR_INSUFFICIENT_BUFFER
        raise_windows_error("LookupAccountNameA", error_code)
    
    # Allocate buffers and make the actual call
    sid_buffer = ctypes.create_string_buffer(sid_size.value)
    domain_buffer = ctypes.create_string_buffer(domain_size.value)
    
    result = advapi32.LookupAccountNameA(
        system_name_bytes,
        account_name_bytes,
        ctypes.cast(sid_buffer, PSID),
        ctypes.byref(sid_size),
        domain_buffer,
        ctypes.byref(domain_size),
        ctypes.byref(sid_name_use)
    )
    
    if not result:
        raise_windows_error("LookupAccountNameA")
    
    # Return the SID as bytes, domain name as string, and SID name use
    return (
        sid_buffer.raw[:sid_size.value],
        domain_buffer.value.decode('utf-8'),
        sid_name_use.value
    )

def LookupAccountSid(sid_bytes: bytes, system_name: str = None) -> tuple[str, str, int]:
    """
    Look up the account name for a given SID.
    
    Args:
        sid_bytes: The SID as bytes
        system_name: The system name (None for local system)
        
    Returns:
        A tuple of (account_name, domain_name, sid_name_use)
        
    Raises:
        WindowsError: If the lookup fails
    """
    system_name_bytes = system_name.encode('utf-8') if system_name else None
    
    # Create a SID structure from the bytes
    sid_buffer = ctypes.create_string_buffer(sid_bytes)
    sid_ptr = ctypes.cast(sid_buffer, PSID)
    
    # First call to get required buffer sizes
    name_size = DWORD(0)
    domain_size = DWORD(0)
    sid_name_use = DWORD(0)
    
    result = advapi32.LookupAccountSidA(
        system_name_bytes,
        sid_ptr,
        None,  # Name buffer (None to get size)
        ctypes.byref(name_size),
        None,  # Domain buffer (None to get size)
        ctypes.byref(domain_size),
        ctypes.byref(sid_name_use)
    )
    
    # The first call should fail with ERROR_INSUFFICIENT_BUFFER
    if result:
        raise WindowsError(0, "LookupAccountSidA", "Unexpected success on size query")
    
    error_code = GetLastError()
    if error_code != 122:  # ERROR_INSUFFICIENT_BUFFER
        raise_windows_error("LookupAccountSidA", error_code)
    
    # Allocate buffers and make the actual call
    name_buffer = ctypes.create_string_buffer(name_size.value)
    domain_buffer = ctypes.create_string_buffer(domain_size.value)
    
    result = advapi32.LookupAccountSidA(
        system_name_bytes,
        sid_ptr,
        name_buffer,
        ctypes.byref(name_size),
        domain_buffer,
        ctypes.byref(domain_size),
        ctypes.byref(sid_name_use)
    )
    
    if not result:
        raise_windows_error("LookupAccountSidA")
    
    # Return the account name, domain name, and SID name use
    return (
        name_buffer.value.decode('utf-8'),
        domain_buffer.value.decode('utf-8'),
        sid_name_use.value
    )

def ConvertStringSidToSid(string_sid: str) -> bytes:
    """
    Convert a string SID to a SID structure.
    
    Args:
        string_sid: The SID in string format (e.g., "S-1-5-21-...")
        
    Returns:
        The SID as bytes
        
    Raises:
        WindowsError: If the conversion fails
    """
    string_sid_bytes = string_sid.encode('utf-8')
    # Use c_void_p for the raw SID pointer that the API will allocate
    sid_ptr = ctypes.c_void_p()
    
    result = advapi32.ConvertStringSidToSidA(
        string_sid_bytes,
        ctypes.byref(sid_ptr)
    )
    
    if not result:
        raise_windows_error("ConvertStringSidToSidA")
    
    try:
        # Cast the raw pointer to a SID structure to access its fields
        sid_struct = ctypes.cast(sid_ptr, POINTER(SID)).contents
        sid_size = 8 + (sid_struct.SubAuthorityCount * 4)  # Base size + sub-authorities
        
        # Copy the SID data to bytes
        sid_bytes = ctypes.string_at(sid_ptr, sid_size)
        
        return sid_bytes
    finally:
        # Free the allocated SID
        kernel32.LocalFree(sid_ptr)

def ConvertSidToStringSid(sid_bytes: bytes) -> str:
    """
    Convert a SID structure to a string SID.
    
    Args:
        sid_bytes: The SID as bytes
        
    Returns:
        The SID in string format (e.g., "S-1-5-21-...")
        
    Raises:
        WindowsError: If the conversion fails
    """
    # Create a SID structure from the bytes
    sid_buffer = ctypes.create_string_buffer(sid_bytes)
    sid_ptr = ctypes.cast(sid_buffer, PSID)
    
    string_sid_ptr = LPSTR()
    
    result = advapi32.ConvertSidToStringSidA(
        sid_ptr,
        ctypes.byref(string_sid_ptr)
    )
    
    if not result:
        raise_windows_error("ConvertSidToStringSidA")
    
    try:
        # Convert the string pointer to a Python string
        string_sid = ctypes.string_at(string_sid_ptr).decode('utf-8')
        return string_sid
    finally:
        # Free the allocated string
        kernel32.LocalFree(string_sid_ptr)

def GetFileSecurity(file_name: str, requested_information: int) -> bytes:
    """
    Get security information for a file.
    
    Args:
        file_name: The path to the file
        requested_information: The type of security information to retrieve
        
    Returns:
        The security descriptor as bytes
        
    Raises:
        WindowsError: If the operation fails
    """
    file_name_bytes = file_name.encode('utf-8')
    
    # First call to get required buffer size
    length_needed = DWORD(0)
    
    result = advapi32.GetFileSecurityA(
        file_name_bytes,
        requested_information,
        None,  # Security descriptor buffer (None to get size)
        0,     # Buffer size
        ctypes.byref(length_needed)
    )
    
    # The first call should fail with ERROR_INSUFFICIENT_BUFFER
    if result:
        raise WindowsError(0, "GetFileSecurityA", "Unexpected success on size query")
    
    error_code = GetLastError()
    if error_code != 122:  # ERROR_INSUFFICIENT_BUFFER
        raise_windows_error("GetFileSecurityA", error_code)
    
    # Allocate buffer and make the actual call
    security_descriptor_buffer = ctypes.create_string_buffer(length_needed.value)
    
    result = advapi32.GetFileSecurityA(
        file_name_bytes,
        requested_information,
        ctypes.cast(security_descriptor_buffer, PSECURITY_DESCRIPTOR),
        length_needed.value,
        ctypes.byref(length_needed)
    )
    
    if not result:
        raise_windows_error("GetFileSecurityA")
    
    return security_descriptor_buffer.raw

def SetFileSecurity(file_name: str, security_information: int, security_descriptor_bytes: bytes) -> None:
    """
    Set security information for a file.
    
    Args:
        file_name: The path to the file
        security_information: The type of security information to set
        security_descriptor_bytes: The security descriptor as bytes
        
    Raises:
        WindowsError: If the operation fails
    """
    file_name_bytes = file_name.encode('utf-8')
    
    # Create a security descriptor structure from the bytes
    security_descriptor_buffer = ctypes.create_string_buffer(security_descriptor_bytes)
    security_descriptor_ptr = ctypes.cast(security_descriptor_buffer, PSECURITY_DESCRIPTOR)
    
    result = advapi32.SetFileSecurityA(
        file_name_bytes,
        security_information,
        security_descriptor_ptr
    )
    
    if not result:
        raise_windows_error("SetFileSecurityA")

def InitializeAcl(acl_size: int, acl_revision: int = ACL_REVISION) -> bytes:
    """
    Initialize a new ACL structure.
    
    Args:
        acl_size: The size of the ACL buffer in bytes
        acl_revision: The ACL revision (default: ACL_REVISION)
        
    Returns:
        The initialized ACL as bytes
        
    Raises:
        WindowsError: If the initialization fails
    """
    # Create an ACL buffer
    acl_buffer = ctypes.create_string_buffer(acl_size)
    acl_ptr = ctypes.cast(acl_buffer, PACL)
    
    result = advapi32.InitializeAcl(
        acl_ptr,
        acl_size,
        acl_revision
    )
    
    if not result:
        raise_windows_error("InitializeAcl")
    
    return acl_buffer.raw

def AddAccessAllowedAce(acl_bytes: bytes, ace_revision: int, access_mask: int, sid_bytes: bytes) -> bytes:
    """
    Add an access-allowed ACE to an ACL.
    
    Args:
        acl_bytes: The ACL as bytes
        ace_revision: The ACE revision (typically ACL_REVISION)
        access_mask: The access rights to grant
        sid_bytes: The SID to grant access to, as bytes
        
    Returns:
        The modified ACL as bytes
        
    Raises:
        WindowsError: If the operation fails
    """
    # Create ACL and SID structures from bytes
    acl_buffer = ctypes.create_string_buffer(acl_bytes)
    acl_ptr = ctypes.cast(acl_buffer, PACL)
    
    sid_buffer = ctypes.create_string_buffer(sid_bytes)
    sid_ptr = ctypes.cast(sid_buffer, PSID)
    
    result = advapi32.AddAccessAllowedAce(
        acl_ptr,
        ace_revision,
        access_mask,
        sid_ptr
    )
    
    if not result:
        raise_windows_error("AddAccessAllowedAce")
    
    return acl_buffer.raw

def AddAccessDeniedAce(acl_bytes: bytes, ace_revision: int, access_mask: int, sid_bytes: bytes) -> bytes:
    """
    Add an access-denied ACE to an ACL.
    
    Args:
        acl_bytes: The ACL as bytes
        ace_revision: The ACE revision (typically ACL_REVISION)
        access_mask: The access rights to deny
        sid_bytes: The SID to deny access to, as bytes
        
    Returns:
        The modified ACL as bytes
        
    Raises:
        WindowsError: If the operation fails
    """
    # Create ACL and SID structures from bytes
    acl_buffer = ctypes.create_string_buffer(acl_bytes)
    acl_ptr = ctypes.cast(acl_buffer, PACL)
    
    sid_buffer = ctypes.create_string_buffer(sid_bytes)
    sid_ptr = ctypes.cast(sid_buffer, PSID)
    
    result = advapi32.AddAccessDeniedAce(
        acl_ptr,
        ace_revision,
        access_mask,
        sid_ptr
    )
    
    if not result:
        raise_windows_error("AddAccessDeniedAce")
    
    return acl_buffer.raw

# =======================
# Exports
# =======================

# Export the main functions and classes
__all__ = [
    # Structures
    'SID',
    'ACL', 
    'SECURITY_DESCRIPTOR',
    'SID_IDENTIFIER_AUTHORITY',
    'ACCESS_ALLOWED_ACE',
    'ACCESS_DENIED_ACE',
    # Type aliases
    'PSID',
    'PACL',
    'PSECURITY_DESCRIPTOR',
    # Functions
    'LookupAccountName',
    'LookupAccountSid',
    'ConvertStringSidToSid',
    'ConvertSidToStringSid',
    'GetFileSecurity',
    'SetFileSecurity',
    'InitializeAcl',
    'AddAccessAllowedAce',
    'AddAccessDeniedAce',
    # Constants
    'ACL_REVISION',
    'ACL_REVISION_DS',
    'SECURITY_DESCRIPTOR_REVISION',
    'SID_REVISION',
    'SID_MAX_SUB_AUTHORITIES',
    'SE_FILE_OBJECT',
    'OWNER_SECURITY_INFORMATION',
    'GROUP_SECURITY_INFORMATION',
    'DACL_SECURITY_INFORMATION',
    'SACL_SECURITY_INFORMATION',
    'SidTypeUser',
    'SidTypeGroup',
    'SidTypeDomain',
    'SidTypeAlias',
    'SidTypeWellKnownGroup',
    'SidTypeDeletedAccount',
    'SidTypeInvalid',
    'SidTypeUnknown',
    'SidTypeComputer',
    'SidTypeLabel',
]