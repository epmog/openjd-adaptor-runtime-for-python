# Design Document

## Overview

This design outlines the approach for removing pywin32 dependencies from the openjd-adaptor-runtime-for-python project by implementing equivalent functionality using Python's ctypes library. The project currently uses pywin32 for Windows-specific operations including named pipes, file security, and Windows API interactions. We will replace all pywin32 usage with ctypes-based implementations while maintaining identical functionality and API compatibility.

The existing `_win32/_named_pipes.py` module already demonstrates the pattern we'll follow - using ctypes to define Windows API functions, constants, and structures with proper type annotations and Microsoft documentation references.

## Architecture

### Module Structure

The implementation will extend the existing `src/openjd/adaptor_runtime_client/_win32/` directory with additional modules:

```
src/openjd/adaptor_runtime_client/_win32/
├── _named_pipes.py          # Existing - already has some ctypes implementations
├── _file_operations.py      # New - ReadFile, WriteFile, file operations
├── _security.py            # New - Security APIs, ACLs, SIDs
├── _error_handling.py      # New - Windows error handling and constants
└── _constants.py           # New - Windows constants and error codes
```

### Design Principles

1. **Maintain API Compatibility**: All existing public interfaces remain unchanged
2. **Follow Existing Pattern**: Use the same ctypes pattern established in `_named_pipes.py`
3. **Microsoft Documentation**: Reference official Microsoft documentation for all APIs
4. **Type Safety**: Use proper ctypes type annotations
5. **Error Handling**: Implement equivalent error handling to pywin32

## Components and Interfaces

### 1. Error Handling Component (`_error_handling.py`)

**Purpose**: Replace `pywintypes.error` with a ctypes-based equivalent

**Key Classes**:
- `WindowsError`: Custom exception class to replace `pywintypes.error`
- Error code constants (ERROR_BROKEN_PIPE, ERROR_PIPE_NOT_CONNECTED, etc.)

**Interface**:
```python
class WindowsError(Exception):
    def __init__(self, winerror: int, funcname: str, strerror: str):
        self.winerror = winerror
        self.funcname = funcname  
        self.strerror = strerror

def get_last_error() -> WindowsError:
    """Get the last Windows error using GetLastError()"""
    
def format_message(error_code: int) -> str:
    """Format a Windows error code into a human-readable message"""
```

### 2. File Operations Component (`_file_operations.py`)

**Purpose**: Replace win32file functions with ctypes equivalents

**Key Functions**:
- `ReadFile`: Replace `win32file.ReadFile`
- `WriteFile`: Replace `win32file.WriteFile`
- `CreateFile`: Replace `win32file.CreateFile` (already exists, may need enhancement)

**Interface**:
```python
def ReadFile(handle: HANDLE, buffer_size: int) -> tuple[int, bytes]:
    """Read data from a file handle, returns (error_code, data)"""

def WriteFile(handle: HANDLE, data: bytes) -> int:
    """Write data to a file handle, returns error code"""
```

### 3. Security Component (`_security.py`)

**Purpose**: Replace win32security functions with ctypes equivalents

**Key Structures**:
- `SECURITY_DESCRIPTOR`: Windows security descriptor
- `ACL`: Access Control List
- `SID`: Security Identifier

**Key Functions**:
- `LookupAccountName`: Get SID from username
- `LookupAccountSid`: Get username from SID
- `GetFileSecurity`: Get file security information
- `SetFileSecurity`: Set file security information
- `ConvertStringSidToSid`: Convert string SID to SID structure

### 4. Constants Component (`_constants.py`)

**Purpose**: Define all Windows constants used throughout the codebase

**Key Constants**:
- File access rights (GENERIC_READ, GENERIC_WRITE, GENERIC_ALL)
- Error codes (ERROR_BROKEN_PIPE, ERROR_PIPE_NOT_CONNECTED, etc.)
- Security constants (ACL_REVISION, FILE_GENERIC_READ, etc.)
- Named pipe constants (already partially defined)

## Data Models

### Handle Management

**Current State**: Uses `pywintypes.HANDLE`
**New State**: Uses `ctypes.wintypes.HANDLE`

The transition requires careful handle management to ensure:
- Handles are properly closed
- Handle validation works correctly
- Handle comparison operations work

### Error Information

**Current State**: `pywintypes.error` with attributes:
- `winerror`: Error code
- `funcname`: Function name
- `strerror`: Error message

**New State**: Custom `WindowsError` class with identical attributes and behavior

### Security Structures

**Current State**: Uses win32security objects
**New State**: ctypes.Structure-based implementations

```python
class SECURITY_DESCRIPTOR(ctypes.Structure):
    # Implementation based on Microsoft documentation
    
class ACL(ctypes.Structure):
    # Implementation based on Microsoft documentation
    
class SID(ctypes.Structure):
    # Implementation based on Microsoft documentation
```

## Error Handling

### Exception Compatibility

The new error handling must maintain compatibility with existing exception handling code:

1. **PipeDisconnectedException**: Currently catches `pywintypes.error`, must work with new `WindowsError`
2. **Error Code Checking**: Code that checks `e.winerror` must continue to work
3. **Error Messages**: Error messages should be identical or equivalent

### Error Translation

Create a mapping system to translate Windows error codes to appropriate Python exceptions:

```python
def handle_windows_error(error_code: int, function_name: str) -> None:
    """Convert Windows error codes to appropriate exceptions"""
    if error_code in [ERROR_BROKEN_PIPE, ERROR_PIPE_NOT_CONNECTED]:
        # Raise appropriate exception
    elif error_code == ERROR_FILE_NOT_FOUND:
        # Raise appropriate exception
```

## Testing Strategy

### Unit Tests

1. **Error Handling Tests**: Verify new error classes behave identically to pywin32 errors
2. **API Compatibility Tests**: Ensure all function signatures remain the same
3. **Constant Value Tests**: Verify all Windows constants have correct values
4. **Structure Tests**: Verify ctypes structures have correct field layouts

### Integration Tests

1. **Named Pipe Tests**: Verify named pipe operations work end-to-end
2. **File Security Tests**: Verify file permission operations work correctly
3. **Cross-Platform Tests**: Ensure non-Windows platforms are unaffected

### Compatibility Tests

1. **Existing Test Suite**: All existing tests must pass without modification
2. **Error Scenario Tests**: Verify error conditions produce identical results
3. **Performance Tests**: Ensure ctypes implementation has similar performance

### Test Migration Strategy

1. **Phase 1**: Run existing tests with new implementation
2. **Phase 2**: Add specific tests for new ctypes functions
3. **Phase 3**: Add regression tests for edge cases

## Implementation Phases

### Phase 1: Error Handling Foundation
- Implement `WindowsError` class
- Implement error code constants
- Implement `GetLastError` and `FormatMessage` functions

### Phase 2: File Operations
- Implement `ReadFile` and `WriteFile` functions
- Update named pipe helper to use new file operations
- Test file I/O operations

### Phase 3: Security Operations
- Implement security structures (SID, ACL, SECURITY_DESCRIPTOR)
- Implement security functions (LookupAccountName, GetFileSecurity, etc.)
- Update secure file operations

### Phase 4: Integration and Cleanup
- Remove all pywin32 imports
- Update pyproject.toml to remove pywin32 dependency
- Run full test suite
- Update documentation

## Migration Strategy

### Backward Compatibility

During the transition, we'll maintain backward compatibility by:

1. **Gradual Replacement**: Replace pywin32 usage module by module
2. **Interface Preservation**: Keep all public APIs unchanged
3. **Error Compatibility**: Ensure new errors are compatible with existing exception handling

### Risk Mitigation

1. **Comprehensive Testing**: Extensive testing at each phase
2. **Rollback Plan**: Ability to revert changes if issues are discovered
3. **Documentation**: Clear documentation of all changes and new implementations

## Dependencies

### Removed Dependencies
- `pywin32`: Will be completely removed from requirements

### New Dependencies
- None - ctypes is part of Python standard library

### Existing Dependencies
- All existing dependencies remain unchanged

## Performance Considerations

### ctypes vs pywin32

- **ctypes**: Direct Windows API calls, minimal overhead
- **pywin32**: Wrapper around Windows APIs, slightly more overhead
- **Expected Impact**: Similar or slightly better performance with ctypes

### Memory Management

- **Handle Management**: Ensure proper handle cleanup
- **Structure Allocation**: Proper ctypes structure memory management
- **Buffer Management**: Efficient buffer allocation for file operations

## Security Considerations

### API Security

- **Input Validation**: Validate all inputs to Windows API calls
- **Buffer Overflow Protection**: Use proper buffer size management
- **Handle Security**: Ensure handles cannot be misused

### Compatibility Security

- **Permission Preservation**: Ensure file permissions work identically
- **Security Descriptor Handling**: Proper security descriptor management
- **Access Control**: Maintain existing access control behavior