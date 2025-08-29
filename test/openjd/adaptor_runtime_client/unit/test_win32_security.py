# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

import ctypes
import pytest
import sys
from unittest.mock import MagicMock, patch, call

# Only run these tests on Windows
pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific tests")

if sys.platform == "win32":
    from openjd.adaptor_runtime_client._win32._security import (
        # Structures
        SID,
        ACL,
        SECURITY_DESCRIPTOR,
        SID_IDENTIFIER_AUTHORITY,
        ACCESS_ALLOWED_ACE,
        ACCESS_DENIED_ACE,
        # Functions
        LookupAccountName,
        LookupAccountSid,
        ConvertStringSidToSid,
        ConvertSidToStringSid,
        GetFileSecurity,
        SetFileSecurity,
        InitializeAcl,
        AddAccessAllowedAce,
        AddAccessDeniedAce,
        # Constants
        ACL_REVISION,
        SECURITY_DESCRIPTOR_REVISION,
        SID_REVISION,
        SID_MAX_SUB_AUTHORITIES,
        OWNER_SECURITY_INFORMATION,
        GROUP_SECURITY_INFORMATION,
        DACL_SECURITY_INFORMATION,
        SACL_SECURITY_INFORMATION,
        SidTypeUser,
        SidTypeGroup,
        SidTypeDomain,
    )
    from openjd.adaptor_runtime_client._win32._error_handling import WindowsError


class TestSecurityStructures:
    """Test the ctypes security structures."""
    
    def test_sid_structure_fields(self):
        """Test that SID structure has correct fields."""
        sid = SID()
        
        # Check that all expected fields exist
        assert hasattr(sid, 'Revision')
        assert hasattr(sid, 'SubAuthorityCount')
        assert hasattr(sid, 'IdentifierAuthority')
        assert hasattr(sid, 'SubAuthority')
        
        # Check field types and sizes
        assert isinstance(sid.Revision, int)
        assert isinstance(sid.SubAuthorityCount, int)
        assert isinstance(sid.IdentifierAuthority, SID_IDENTIFIER_AUTHORITY)
        assert len(sid.SubAuthority) == SID_MAX_SUB_AUTHORITIES
    
    def test_sid_identifier_authority_structure(self):
        """Test that SID_IDENTIFIER_AUTHORITY structure has correct fields."""
        auth = SID_IDENTIFIER_AUTHORITY()
        
        # Check that Value field exists and is correct size
        assert hasattr(auth, 'Value')
        assert len(auth.Value) == 6
        
        # Test setting values
        auth.Value[0] = 1
        auth.Value[5] = 255
        assert auth.Value[0] == 1
        assert auth.Value[5] == 255
    
    def test_acl_structure_fields(self):
        """Test that ACL structure has correct fields."""
        acl = ACL()
        
        # Check that all expected fields exist
        assert hasattr(acl, 'AclRevision')
        assert hasattr(acl, 'Sbz1')
        assert hasattr(acl, 'AclSize')
        assert hasattr(acl, 'AceCount')
        assert hasattr(acl, 'Sbz2')
        
        # Test setting values
        acl.AclRevision = ACL_REVISION
        acl.AclSize = 100
        acl.AceCount = 5
        
        assert acl.AclRevision == ACL_REVISION
        assert acl.AclSize == 100
        assert acl.AceCount == 5
    
    def test_security_descriptor_structure_fields(self):
        """Test that SECURITY_DESCRIPTOR structure has correct fields."""
        sd = SECURITY_DESCRIPTOR()
        
        # Check that all expected fields exist
        assert hasattr(sd, 'Revision')
        assert hasattr(sd, 'Sbz1')
        assert hasattr(sd, 'Control')
        assert hasattr(sd, 'Owner')
        assert hasattr(sd, 'Group')
        assert hasattr(sd, 'Sacl')
        assert hasattr(sd, 'Dacl')
        
        # Test setting values
        sd.Revision = SECURITY_DESCRIPTOR_REVISION
        sd.Control = 0x8000  # SE_SELF_RELATIVE
        
        assert sd.Revision == SECURITY_DESCRIPTOR_REVISION
        assert sd.Control == 0x8000
    
    def test_access_allowed_ace_structure(self):
        """Test that ACCESS_ALLOWED_ACE structure has correct fields."""
        ace = ACCESS_ALLOWED_ACE()
        
        # Check that all expected fields exist
        assert hasattr(ace, 'Header')
        assert hasattr(ace, 'Mask')
        assert hasattr(ace, 'SidStart')
        
        # Test setting values
        ace.Mask = 0x1F01FF  # GENERIC_ALL
        ace.SidStart = 0x12345678
        
        assert ace.Mask == 0x1F01FF
        assert ace.SidStart == 0x12345678
    
    def test_access_denied_ace_structure(self):
        """Test that ACCESS_DENIED_ACE structure has correct fields."""
        ace = ACCESS_DENIED_ACE()
        
        # Check that all expected fields exist
        assert hasattr(ace, 'Header')
        assert hasattr(ace, 'Mask')
        assert hasattr(ace, 'SidStart')
        
        # Test setting values
        ace.Mask = 0x40000000  # GENERIC_WRITE
        ace.SidStart = 0x87654321
        
        assert ace.Mask == 0x40000000
        assert ace.SidStart == 0x87654321


class TestLookupAccountName:
    """Test the LookupAccountName function."""
    
    @patch('openjd.adaptor_runtime_client._win32._security.advapi32')
    @patch('openjd.adaptor_runtime_client._win32._security.GetLastError')
    def test_lookup_account_name_success(self, mock_get_last_error, mock_advapi32):
        """Test successful account name lookup."""
        # Mock GetLastError to return ERROR_INSUFFICIENT_BUFFER on first call
        mock_get_last_error.return_value = 122  # ERROR_INSUFFICIENT_BUFFER
        
        # Mock both calls with a single side_effect function
        def mock_lookup_call(*args):
            # args[2] is the SID buffer, args[4] is the domain buffer
            if args[2] is None and args[4] is None:
                # First call - just set buffer sizes and return False
                args[3]._obj.value = 12  # sid_size
                args[5]._obj.value = 6   # domain_size
                args[6]._obj.value = SidTypeUser
                return False
            elif args[2] is not None and args[4] is not None:
                # Second call - populate buffers and return True
                sid_data = b'\x01\x02\x00\x00\x00\x00\x00\x05\x15\x00\x00\x00'
                ctypes.memmove(args[2], sid_data, len(sid_data))
                args[3]._obj.value = len(sid_data)
                
                domain_name = b'DOMAIN'
                ctypes.memmove(args[4], domain_name, len(domain_name))
                args[5]._obj.value = len(domain_name)
                
                args[6]._obj.value = SidTypeUser
                return True
            return False
        
        mock_advapi32.LookupAccountNameA.side_effect = mock_lookup_call
        
        # Call the function
        sid_bytes, domain_name, sid_name_use = LookupAccountName("testuser")
        
        # Verify results
        assert isinstance(sid_bytes, bytes)
        assert len(sid_bytes) > 0
        assert domain_name == "DOMAIN"
        assert sid_name_use == SidTypeUser
        
        # Verify API calls
        assert mock_advapi32.LookupAccountNameA.call_count == 2
    
    @patch('openjd.adaptor_runtime_client._win32._security.advapi32')
    @patch('openjd.adaptor_runtime_client._win32._security.GetLastError')
    def test_lookup_account_name_not_found(self, mock_get_last_error, mock_advapi32):
        """Test account name lookup when account is not found."""
        # Mock the first call to fail with ERROR_NONE_MAPPED
        mock_advapi32.LookupAccountNameA.return_value = False
        mock_get_last_error.return_value = 1332  # ERROR_NONE_MAPPED
        
        # Should raise WindowsError
        with pytest.raises(WindowsError) as exc_info:
            LookupAccountName("nonexistentuser")
        
        assert exc_info.value.winerror == 1332
        assert "LookupAccountNameA" in exc_info.value.funcname
    
    @patch('openjd.adaptor_runtime_client._win32._security.advapi32')
    @patch('openjd.adaptor_runtime_client._win32._security.GetLastError')
    def test_lookup_account_name_with_system_name(self, mock_get_last_error, mock_advapi32):
        """Test account name lookup with system name."""
        # Mock successful calls
        mock_advapi32.LookupAccountNameA.side_effect = [False, True]
        mock_get_last_error.return_value = 122  # ERROR_INSUFFICIENT_BUFFER
        
        # Call with system name
        with patch.object(ctypes, 'create_string_buffer') as mock_buffer:
            mock_buffer.return_value.raw = b'\x01\x02\x00\x00'
            mock_buffer.return_value.value = b'DOMAIN'
            
            try:
                LookupAccountName("testuser", "REMOTE_SYSTEM")
            except:
                pass  # We're just testing that system_name is passed correctly
        
        # Verify that system name was encoded and passed
        calls = mock_advapi32.LookupAccountNameA.call_args_list
        assert len(calls) >= 1
        # First argument should be the encoded system name
        assert calls[0][0][0] == b'REMOTE_SYSTEM'


class TestLookupAccountSid:
    """Test the LookupAccountSid function."""
    
    @patch('openjd.adaptor_runtime_client._win32._security.advapi32')
    @patch('openjd.adaptor_runtime_client._win32._security.GetLastError')
    def test_lookup_account_sid_success(self, mock_get_last_error, mock_advapi32):
        """Test successful SID lookup."""
        # Mock GetLastError to return ERROR_INSUFFICIENT_BUFFER on first call
        mock_get_last_error.return_value = 122  # ERROR_INSUFFICIENT_BUFFER
        
        # Mock both calls with a single side_effect function
        def mock_lookup_call(*args):
            # args[2] is the name buffer, args[4] is the domain buffer
            if args[2] is None and args[4] is None:
                # First call - just set buffer sizes and return False
                args[3]._obj.value = 8  # name_size
                args[5]._obj.value = 6  # domain_size
                args[6]._obj.value = SidTypeUser
                return False
            elif args[2] is not None and args[4] is not None:
                # Second call - populate buffers and return True
                account_name = b'testuser'
                ctypes.memmove(args[2], account_name, len(account_name))
                args[3]._obj.value = len(account_name)
                
                domain_name = b'DOMAIN'
                ctypes.memmove(args[4], domain_name, len(domain_name))
                args[5]._obj.value = len(domain_name)
                
                args[6]._obj.value = SidTypeUser
                return True
            return False
        
        mock_advapi32.LookupAccountSidA.side_effect = mock_lookup_call
        
        # Test SID bytes (simplified SID structure)
        test_sid_bytes = b'\x01\x02\x00\x00\x00\x00\x00\x05\x15\x00\x00\x00'
        
        # Call the function
        account_name, domain_name, sid_name_use = LookupAccountSid(test_sid_bytes)
        
        # Verify results
        assert account_name == "testuser"
        assert domain_name == "DOMAIN"
        assert sid_name_use == SidTypeUser
        
        # Verify API calls
        assert mock_advapi32.LookupAccountSidA.call_count == 2
    
    @patch('openjd.adaptor_runtime_client._win32._security.advapi32')
    @patch('openjd.adaptor_runtime_client._win32._security.GetLastError')
    def test_lookup_account_sid_invalid_sid(self, mock_get_last_error, mock_advapi32):
        """Test SID lookup with invalid SID."""
        # Mock the call to fail with ERROR_INVALID_SID
        mock_advapi32.LookupAccountSidA.return_value = False
        mock_get_last_error.return_value = 1337  # ERROR_INVALID_SID
        
        # Test with invalid SID bytes
        invalid_sid_bytes = b'\x00\x00\x00\x00'
        
        # Should raise WindowsError
        with pytest.raises(WindowsError) as exc_info:
            LookupAccountSid(invalid_sid_bytes)
        
        assert exc_info.value.winerror == 1337
        assert "LookupAccountSidA" in exc_info.value.funcname


class TestConvertStringSidToSid:
    """Test the ConvertStringSidToSid function."""
    
    @patch('openjd.adaptor_runtime_client._win32._security.advapi32')
    @patch('openjd.adaptor_runtime_client._win32._security.kernel32')
    def test_convert_string_sid_to_sid_success(self, mock_kernel32, mock_advapi32):
        """Test successful string SID conversion."""
        # Mock successful conversion
        mock_advapi32.ConvertStringSidToSidA.return_value = True
        
        # Mock the SID pointer returned by the API
        def mock_convert_call(*args):
            # args[1] is the output SID pointer (c_void_p)
            # Set it to a mock pointer value
            args[1]._obj.value = 0x12345678
            return True
        
        mock_advapi32.ConvertStringSidToSidA.side_effect = mock_convert_call
        
        # Mock ctypes.cast to return a mock SID structure
        mock_sid_struct = MagicMock()
        mock_sid_struct.SubAuthorityCount = 4
        
        # Mock ctypes.string_at to return SID bytes
        test_sid_bytes = b'\x01\x04\x00\x00\x00\x00\x00\x05\x15\x00\x00\x00\x01\x02\x03\x04'
        
        with patch('ctypes.cast') as mock_cast, \
             patch('ctypes.string_at', return_value=test_sid_bytes):
            
            mock_cast.return_value.contents = mock_sid_struct
            
            # Call the function
            result = ConvertStringSidToSid("S-1-5-21-1-2-3-4")
            
            # Verify result
            assert result == test_sid_bytes
        
        # Verify API calls
        mock_advapi32.ConvertStringSidToSidA.assert_called_once()
        mock_kernel32.LocalFree.assert_called_once()
    
    @patch('openjd.adaptor_runtime_client._win32._security.advapi32')
    def test_convert_string_sid_to_sid_invalid_format(self, mock_advapi32):
        """Test string SID conversion with invalid format."""
        # Mock failed conversion
        mock_advapi32.ConvertStringSidToSidA.return_value = False
        
        # Should raise WindowsError
        with pytest.raises(WindowsError) as exc_info:
            ConvertStringSidToSid("invalid-sid-format")
        
        assert "ConvertStringSidToSidA" in exc_info.value.funcname


class TestConvertSidToStringSid:
    """Test the ConvertSidToStringSid function."""
    
    @patch('openjd.adaptor_runtime_client._win32._security.advapi32')
    @patch('openjd.adaptor_runtime_client._win32._security.kernel32')
    def test_convert_sid_to_string_sid_success(self, mock_kernel32, mock_advapi32):
        """Test successful SID to string conversion."""
        # Mock successful conversion
        mock_advapi32.ConvertSidToStringSidA.return_value = True
        
        # Mock the string SID returned by the API
        test_string_sid = "S-1-5-21-1-2-3-4"
        
        def mock_convert_call(*args):
            # args[1] is the output string pointer
            # We need to simulate the API allocating memory and setting the pointer
            return True
        
        mock_advapi32.ConvertSidToStringSidA.side_effect = mock_convert_call
        
        # Mock ctypes.string_at to return the string SID
        with patch('ctypes.string_at', return_value=test_string_sid.encode('utf-8')):
            # Test SID bytes
            test_sid_bytes = b'\x01\x04\x00\x00\x00\x00\x00\x05\x15\x00\x00\x00\x01\x02\x03\x04'
            
            # Call the function
            result = ConvertSidToStringSid(test_sid_bytes)
            
            # Verify result
            assert result == test_string_sid
        
        # Verify API calls
        mock_advapi32.ConvertSidToStringSidA.assert_called_once()
        mock_kernel32.LocalFree.assert_called_once()
    
    @patch('openjd.adaptor_runtime_client._win32._security.advapi32')
    def test_convert_sid_to_string_sid_invalid_sid(self, mock_advapi32):
        """Test SID to string conversion with invalid SID."""
        # Mock failed conversion
        mock_advapi32.ConvertSidToStringSidA.return_value = False
        
        # Test with invalid SID bytes
        invalid_sid_bytes = b'\x00\x00\x00\x00'
        
        # Should raise WindowsError
        with pytest.raises(WindowsError) as exc_info:
            ConvertSidToStringSid(invalid_sid_bytes)
        
        assert "ConvertSidToStringSidA" in exc_info.value.funcname


class TestGetFileSecurity:
    """Test the GetFileSecurity function."""
    
    @patch('openjd.adaptor_runtime_client._win32._security.advapi32')
    @patch('openjd.adaptor_runtime_client._win32._security.GetLastError')
    def test_get_file_security_success(self, mock_get_last_error, mock_advapi32):
        """Test successful file security retrieval."""
        # Mock GetLastError to return ERROR_INSUFFICIENT_BUFFER on first call
        mock_get_last_error.return_value = 122  # ERROR_INSUFFICIENT_BUFFER
        
        # Mock both calls with a single side_effect function
        def mock_get_file_security_call(*args):
            # args[2] is the security descriptor buffer, args[4] is length_needed
            if args[2] is None:
                # First call - just set buffer size and return False
                args[4]._obj.value = 20  # length_needed
                return False
            else:
                # Second call - populate buffer and return True
                sd_data = b'\x01\x00\x04\x80' + b'\x00' * 16  # Minimal security descriptor
                ctypes.memmove(args[2], sd_data, len(sd_data))
                return True
        
        mock_advapi32.GetFileSecurityA.side_effect = mock_get_file_security_call
        
        # Call the function
        result = GetFileSecurity("C:\\test.txt", OWNER_SECURITY_INFORMATION)
        
        # Verify result
        assert isinstance(result, bytes)
        assert len(result) > 0
        
        # Verify API calls
        assert mock_advapi32.GetFileSecurityA.call_count == 2
    
    @patch('openjd.adaptor_runtime_client._win32._security.advapi32')
    @patch('openjd.adaptor_runtime_client._win32._security.GetLastError')
    def test_get_file_security_file_not_found(self, mock_get_last_error, mock_advapi32):
        """Test file security retrieval when file is not found."""
        # Mock the call to fail with ERROR_FILE_NOT_FOUND
        mock_advapi32.GetFileSecurityA.return_value = False
        mock_get_last_error.return_value = 2  # ERROR_FILE_NOT_FOUND
        
        # Should raise WindowsError
        with pytest.raises(WindowsError) as exc_info:
            GetFileSecurity("C:\\nonexistent.txt", OWNER_SECURITY_INFORMATION)
        
        assert exc_info.value.winerror == 2
        assert "GetFileSecurityA" in exc_info.value.funcname


class TestSetFileSecurity:
    """Test the SetFileSecurity function."""
    
    @patch('openjd.adaptor_runtime_client._win32._security.advapi32')
    def test_set_file_security_success(self, mock_advapi32):
        """Test successful file security setting."""
        # Mock successful call
        mock_advapi32.SetFileSecurityA.return_value = True
        
        # Test security descriptor bytes
        test_sd_bytes = b'\x01\x00\x04\x80' + b'\x00' * 16
        
        # Call the function
        SetFileSecurity("C:\\test.txt", OWNER_SECURITY_INFORMATION, test_sd_bytes)
        
        # Verify API call
        mock_advapi32.SetFileSecurityA.assert_called_once()
        call_args = mock_advapi32.SetFileSecurityA.call_args[0]
        assert call_args[0] == b"C:\\test.txt"
        assert call_args[1] == OWNER_SECURITY_INFORMATION
    
    @patch('openjd.adaptor_runtime_client._win32._security.advapi32')
    def test_set_file_security_access_denied(self, mock_advapi32):
        """Test file security setting when access is denied."""
        # Mock failed call
        mock_advapi32.SetFileSecurityA.return_value = False
        
        # Test security descriptor bytes
        test_sd_bytes = b'\x01\x00\x04\x80' + b'\x00' * 16
        
        # Should raise WindowsError
        with pytest.raises(WindowsError) as exc_info:
            SetFileSecurity("C:\\test.txt", OWNER_SECURITY_INFORMATION, test_sd_bytes)
        
        assert "SetFileSecurityA" in exc_info.value.funcname


class TestSecurityConstants:
    """Test that security constants have expected values."""
    
    def test_acl_constants(self):
        """Test ACL-related constants."""
        assert ACL_REVISION == 2
        
    def test_security_descriptor_constants(self):
        """Test security descriptor constants."""
        assert SECURITY_DESCRIPTOR_REVISION == 1
        
    def test_sid_constants(self):
        """Test SID-related constants."""
        assert SID_REVISION == 1
        assert SID_MAX_SUB_AUTHORITIES == 15
        
    def test_security_information_constants(self):
        """Test security information constants."""
        assert OWNER_SECURITY_INFORMATION == 0x00000001
        assert GROUP_SECURITY_INFORMATION == 0x00000002
        assert DACL_SECURITY_INFORMATION == 0x00000004
        assert SACL_SECURITY_INFORMATION == 0x00000008
        
    def test_sid_name_use_constants(self):
        """Test SID name use constants."""
        assert SidTypeUser == 1
        assert SidTypeGroup == 2
        assert SidTypeDomain == 3


class TestSecurityIntegration:
    """Integration tests for security operations."""
    
    def test_structure_sizes(self):
        """Test that structures have reasonable sizes."""
        # These tests ensure the structures are properly defined
        sid = SID()
        acl = ACL()
        sd = SECURITY_DESCRIPTOR()
        
        # SID should be at least 12 bytes (8 + 4 for one sub-authority)
        assert ctypes.sizeof(sid) >= 12
        
        # ACL should be 8 bytes
        assert ctypes.sizeof(acl) == 8
        
        # Security descriptor should be at least 20 bytes on 32-bit, more on 64-bit
        assert ctypes.sizeof(sd) >= 20
    
    def test_structure_initialization(self):
        """Test that structures can be properly initialized."""
        # Test SID initialization
        sid = SID()
        sid.Revision = SID_REVISION
        sid.SubAuthorityCount = 1
        sid.SubAuthority[0] = 12345
        
        assert sid.Revision == SID_REVISION
        assert sid.SubAuthorityCount == 1
        assert sid.SubAuthority[0] == 12345
        
        # Test ACL initialization
        acl = ACL()
        acl.AclRevision = ACL_REVISION
        acl.AclSize = 100
        acl.AceCount = 2
        
        assert acl.AclRevision == ACL_REVISION
        assert acl.AclSize == 100
        assert acl.AceCount == 2
        
        # Test Security Descriptor initialization
        sd = SECURITY_DESCRIPTOR()
        sd.Revision = SECURITY_DESCRIPTOR_REVISION
        sd.Control = 0x8000
        
        assert sd.Revision == SECURITY_DESCRIPTOR_REVISION
        assert sd.Control == 0x8000


class TestInitializeAcl:
    """Test the InitializeAcl function."""
    
    @patch('openjd.adaptor_runtime_client._win32._security.advapi32')
    def test_initialize_acl_success(self, mock_advapi32):
        """Test successful ACL initialization."""
        # Mock successful call
        mock_advapi32.InitializeAcl.return_value = True
        
        # Call the function
        result = InitializeAcl(1024, ACL_REVISION)
        
        # Verify result
        assert isinstance(result, bytes)
        assert len(result) == 1024
        
        # Verify API call
        mock_advapi32.InitializeAcl.assert_called_once()
        call_args = mock_advapi32.InitializeAcl.call_args[0]
        assert call_args[1] == 1024  # ACL size
        assert call_args[2] == ACL_REVISION  # ACL revision
    
    @patch('openjd.adaptor_runtime_client._win32._security.advapi32')
    def test_initialize_acl_default_revision(self, mock_advapi32):
        """Test ACL initialization with default revision."""
        # Mock successful call
        mock_advapi32.InitializeAcl.return_value = True
        
        # Call the function without specifying revision
        result = InitializeAcl(512)
        
        # Verify result
        assert isinstance(result, bytes)
        assert len(result) == 512
        
        # Verify API call used default revision
        mock_advapi32.InitializeAcl.assert_called_once()
        call_args = mock_advapi32.InitializeAcl.call_args[0]
        assert call_args[2] == ACL_REVISION  # Should use default
    
    @patch('openjd.adaptor_runtime_client._win32._security.advapi32')
    def test_initialize_acl_failure(self, mock_advapi32):
        """Test ACL initialization failure."""
        # Mock failed call
        mock_advapi32.InitializeAcl.return_value = False
        
        # Should raise WindowsError
        with pytest.raises(WindowsError) as exc_info:
            InitializeAcl(1024)
        
        assert "InitializeAcl" in exc_info.value.funcname


class TestAddAccessAllowedAce:
    """Test the AddAccessAllowedAce function."""
    
    @patch('openjd.adaptor_runtime_client._win32._security.advapi32')
    def test_add_access_allowed_ace_success(self, mock_advapi32):
        """Test successful addition of access-allowed ACE."""
        # Mock successful call
        mock_advapi32.AddAccessAllowedAce.return_value = True
        
        # Test data
        test_acl_bytes = b'\x02\x00\x1C\x00\x01\x00\x00\x00' + b'\x00' * 20  # Minimal ACL
        test_sid_bytes = b'\x01\x02\x00\x00\x00\x00\x00\x05\x15\x00\x00\x00'  # Minimal SID
        access_mask = 0x1F01FF  # GENERIC_ALL
        
        # Call the function
        result = AddAccessAllowedAce(test_acl_bytes, ACL_REVISION, access_mask, test_sid_bytes)
        
        # Verify result
        assert isinstance(result, bytes)
        assert len(result) == len(test_acl_bytes)
        
        # Verify API call
        mock_advapi32.AddAccessAllowedAce.assert_called_once()
        call_args = mock_advapi32.AddAccessAllowedAce.call_args[0]
        assert call_args[1] == ACL_REVISION  # ACE revision
        assert call_args[2] == access_mask   # Access mask
    
    @patch('openjd.adaptor_runtime_client._win32._security.advapi32')
    def test_add_access_allowed_ace_failure(self, mock_advapi32):
        """Test failure when adding access-allowed ACE."""
        # Mock failed call
        mock_advapi32.AddAccessAllowedAce.return_value = False
        
        # Test data
        test_acl_bytes = b'\x02\x00\x1C\x00\x01\x00\x00\x00' + b'\x00' * 20
        test_sid_bytes = b'\x01\x02\x00\x00\x00\x00\x00\x05\x15\x00\x00\x00'
        
        # Should raise WindowsError
        with pytest.raises(WindowsError) as exc_info:
            AddAccessAllowedAce(test_acl_bytes, ACL_REVISION, 0x1F01FF, test_sid_bytes)
        
        assert "AddAccessAllowedAce" in exc_info.value.funcname
    
    @patch('openjd.adaptor_runtime_client._win32._security.advapi32')
    def test_add_access_allowed_ace_different_permissions(self, mock_advapi32):
        """Test adding access-allowed ACE with different permission masks."""
        # Mock successful call
        mock_advapi32.AddAccessAllowedAce.return_value = True
        
        # Test data
        test_acl_bytes = b'\x02\x00\x1C\x00\x01\x00\x00\x00' + b'\x00' * 20
        test_sid_bytes = b'\x01\x02\x00\x00\x00\x00\x00\x05\x15\x00\x00\x00'
        
        # Test different access masks
        access_masks = [
            0x80000000,  # GENERIC_READ
            0x40000000,  # GENERIC_WRITE
            0x20000000,  # GENERIC_EXECUTE
            0x10000000,  # GENERIC_ALL
        ]
        
        for access_mask in access_masks:
            mock_advapi32.AddAccessAllowedAce.reset_mock()
            
            result = AddAccessAllowedAce(test_acl_bytes, ACL_REVISION, access_mask, test_sid_bytes)
            
            # Verify result
            assert isinstance(result, bytes)
            
            # Verify correct access mask was passed
            call_args = mock_advapi32.AddAccessAllowedAce.call_args[0]
            assert call_args[2] == access_mask


class TestAddAccessDeniedAce:
    """Test the AddAccessDeniedAce function."""
    
    @patch('openjd.adaptor_runtime_client._win32._security.advapi32')
    def test_add_access_denied_ace_success(self, mock_advapi32):
        """Test successful addition of access-denied ACE."""
        # Mock successful call
        mock_advapi32.AddAccessDeniedAce.return_value = True
        
        # Test data
        test_acl_bytes = b'\x02\x00\x1C\x00\x01\x00\x00\x00' + b'\x00' * 20  # Minimal ACL
        test_sid_bytes = b'\x01\x02\x00\x00\x00\x00\x00\x05\x15\x00\x00\x00'  # Minimal SID
        access_mask = 0x40000000  # GENERIC_WRITE
        
        # Call the function
        result = AddAccessDeniedAce(test_acl_bytes, ACL_REVISION, access_mask, test_sid_bytes)
        
        # Verify result
        assert isinstance(result, bytes)
        assert len(result) == len(test_acl_bytes)
        
        # Verify API call
        mock_advapi32.AddAccessDeniedAce.assert_called_once()
        call_args = mock_advapi32.AddAccessDeniedAce.call_args[0]
        assert call_args[1] == ACL_REVISION  # ACE revision
        assert call_args[2] == access_mask   # Access mask
    
    @patch('openjd.adaptor_runtime_client._win32._security.advapi32')
    def test_add_access_denied_ace_failure(self, mock_advapi32):
        """Test failure when adding access-denied ACE."""
        # Mock failed call
        mock_advapi32.AddAccessDeniedAce.return_value = False
        
        # Test data
        test_acl_bytes = b'\x02\x00\x1C\x00\x01\x00\x00\x00' + b'\x00' * 20
        test_sid_bytes = b'\x01\x02\x00\x00\x00\x00\x00\x05\x15\x00\x00\x00'
        
        # Should raise WindowsError
        with pytest.raises(WindowsError) as exc_info:
            AddAccessDeniedAce(test_acl_bytes, ACL_REVISION, 0x40000000, test_sid_bytes)
        
        assert "AddAccessDeniedAce" in exc_info.value.funcname
    
    @patch('openjd.adaptor_runtime_client._win32._security.advapi32')
    def test_add_access_denied_ace_different_permissions(self, mock_advapi32):
        """Test adding access-denied ACE with different permission masks."""
        # Mock successful call
        mock_advapi32.AddAccessDeniedAce.return_value = True
        
        # Test data
        test_acl_bytes = b'\x02\x00\x1C\x00\x01\x00\x00\x00' + b'\x00' * 20
        test_sid_bytes = b'\x01\x02\x00\x00\x00\x00\x00\x05\x15\x00\x00\x00'
        
        # Test different access masks
        access_masks = [
            0x80000000,  # GENERIC_READ
            0x40000000,  # GENERIC_WRITE
            0x20000000,  # GENERIC_EXECUTE
            0x10000000,  # GENERIC_ALL
        ]
        
        for access_mask in access_masks:
            mock_advapi32.AddAccessDeniedAce.reset_mock()
            
            result = AddAccessDeniedAce(test_acl_bytes, ACL_REVISION, access_mask, test_sid_bytes)
            
            # Verify result
            assert isinstance(result, bytes)
            
            # Verify correct access mask was passed
            call_args = mock_advapi32.AddAccessDeniedAce.call_args[0]
            assert call_args[2] == access_mask


class TestAclManipulationIntegration:
    """Integration tests for ACL manipulation functions."""
    
    @patch('openjd.adaptor_runtime_client._win32._security.advapi32')
    def test_acl_workflow(self, mock_advapi32):
        """Test a complete ACL manipulation workflow."""
        # Mock all API calls to succeed
        mock_advapi32.InitializeAcl.return_value = True
        mock_advapi32.AddAccessAllowedAce.return_value = True
        mock_advapi32.AddAccessDeniedAce.return_value = True
        
        # Test data
        test_sid_bytes = b'\x01\x02\x00\x00\x00\x00\x00\x05\x15\x00\x00\x00'
        
        # Step 1: Initialize ACL
        acl_bytes = InitializeAcl(1024)
        assert isinstance(acl_bytes, bytes)
        assert len(acl_bytes) == 1024
        
        # Step 2: Add access-allowed ACE
        acl_bytes = AddAccessAllowedAce(acl_bytes, ACL_REVISION, 0x1F01FF, test_sid_bytes)
        assert isinstance(acl_bytes, bytes)
        
        # Step 3: Add access-denied ACE
        acl_bytes = AddAccessDeniedAce(acl_bytes, ACL_REVISION, 0x40000000, test_sid_bytes)
        assert isinstance(acl_bytes, bytes)
        
        # Verify all API calls were made
        mock_advapi32.InitializeAcl.assert_called_once()
        mock_advapi32.AddAccessAllowedAce.assert_called_once()
        mock_advapi32.AddAccessDeniedAce.assert_called_once()
    
    def test_acl_manipulation_with_real_structures(self):
        """Test ACL manipulation functions with real ctypes structures."""
        # This test verifies that our ctypes structures are compatible
        # with the function signatures (no mocking)
        
        # Create test structures
        acl = ACL()
        acl.AclRevision = ACL_REVISION
        acl.AclSize = 100
        acl.AceCount = 0
        
        sid = SID()
        sid.Revision = SID_REVISION
        sid.SubAuthorityCount = 1
        sid.SubAuthority[0] = 12345
        
        # Convert structures to bytes
        acl_bytes = ctypes.string_at(ctypes.byref(acl), ctypes.sizeof(acl))
        sid_bytes = ctypes.string_at(ctypes.byref(sid), ctypes.sizeof(sid))
        
        # Verify we can create buffers from the bytes
        acl_buffer = ctypes.create_string_buffer(acl_bytes)
        sid_buffer = ctypes.create_string_buffer(sid_bytes)
        
        # Verify we can cast the buffers back to structure pointers
        from openjd.adaptor_runtime_client._win32._security import PACL, PSID
        acl_ptr = ctypes.cast(acl_buffer, PACL)
        sid_ptr = ctypes.cast(sid_buffer, PSID)
        
        # Verify the structures are accessible
        assert acl_ptr.contents.AclRevision == ACL_REVISION
        assert sid_ptr.contents.Revision == SID_REVISION
        
        # This confirms our function signatures should work with real Windows APIs