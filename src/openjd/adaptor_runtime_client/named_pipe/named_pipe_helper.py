# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

import ctypes
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from random import randint

import getpass
import time
import json
from typing import Dict, List, Optional
from ctypes.wintypes import HANDLE
from enum import Enum
import os

from .._win32._named_pipes import (
    CloseHandle,
    CreateFileA,
    CreateNamedPipeA,
    SetNamedPipeHandleState,
    GENERIC_READ,
    GENERIC_WRITE,
    INVALID_HANDLE_VALUE,
    OPEN_EXISTING,
    PIPE_ACCESS_DUPLEX,
    PIPE_TYPE_MESSAGE,
    PIPE_READMODE_MESSAGE,
    PIPE_WAIT,
    ERROR_FILE_NOT_FOUND,
    ERROR_BROKEN_PIPE,
    ERROR_PIPE_NOT_CONNECTED,
    ERROR_PIPE_BUSY,
    ERROR_INVALID_HANDLE,
)
from .._win32._file_operations import (
    ReadFile,
    WriteFile,
    ERROR_MORE_DATA,
    NO_ERROR,
)
from .._win32._error_handling import (
    WindowsError,
)

from .named_pipe_config import (
    NAMED_PIPE_BUFFER_SIZE,
    DEFAULT_MAX_NAMED_PIPE_INSTANCES,
    DEFAULT_NAMED_PIPE_SERVER_TIMEOUT_IN_SECONDS,
)

_logger = logging.getLogger(__name__)


class NamedPipeOperation(str, Enum):
    CONNECT = "connect"
    READ = "read"


class PipeDisconnectedException(Exception):
    """
    Exception raised when a Named Pipe is either broken or not connected.

    Attributes:
        winerror (int): The numerical error code
        funcname (str): The name of the function that caused the error
        strerror (str): The human-readable error message
    """

    def __init__(self, winerror: int, funcname: str = "", strerror: str = ""):
        self.winerror = winerror  # The numerical error code
        self.funcname = funcname  # The name of the function that caused the error
        self.strerror = strerror  # The human-readable error message

        self.message = f"An error occurred: {strerror} (Error code: {winerror}) in function {funcname}"
        super().__init__(self.message)

    def __str__(self):
        return self.message


class NamedPipeTimeoutError(Exception):
    """A custom error raised on timeouts when waiting for another error."""

    def __init__(
        self, operation: NamedPipeOperation, duration: float, error: Optional[Exception] = None
    ):
        """NamedPipe timeout exception.

        Args:
            operation (NamedPipeOperation): The type of NamedPipe operation that timed out.
            duration (float): The duration waited in seconds.
            error (Exception): The original error that was raised, if an error was raised by the operation.
        """
        self.error = error

        message = f"NamedPipe Server {operation.value} timeout after {duration} seconds."
        if error:
            message = os.linesep.join([message, f"Original error: {error}"])

        super().__init__(message)


class NamedPipeConnectTimeoutError(NamedPipeTimeoutError):
    """A custom error raised on connect timeouts when waiting for another error."""

    def __init__(self, duration: float, error: Exception):
        """Initialize TimeoutError with original error.

        Args:
            duration (float): The duration waited in seconds.
            error (Exception): The original error that was raised.
        """
        self.error = error
        super().__init__(NamedPipeOperation.CONNECT, duration, error)


class NamedPipeReadTimeoutError(NamedPipeTimeoutError):
    """A custom error raised on read timeouts."""

    def __init__(self, duration: float):
        """Initialize TimeoutError with original error.

        Args:
            duration (float): The duration waited in seconds.
        """
        super().__init__(NamedPipeOperation.READ, duration)


class NamedPipeNamingError(Exception):
    """Exception raised for errors in naming a named pipe."""

    pass


class NamedPipeHelper:
    """
    Helper class for reading from and writing to Named Pipes in Windows.

    This class provides static methods to interact with Named Pipes,
    facilitating data transmission between the server and the client.
    """

    @staticmethod
    def create_security_attributes():
        """
        Creates and returns security attributes for a named pipe,
        allowing access only to the current user and denying network access.

        Returns:
            None: Security attributes creation not yet implemented with ctypes
        """
        # TODO: Implement this method using our ctypes security functions
        # For now, return None to use default security
        return None

    @staticmethod
    def create_named_pipe_server(pipe_name: str, time_out_in_seconds: float) -> Optional[HANDLE]:
        """
        Creates a new instance of a named pipe or an additional instance if the pipe already exists.

        Args:
            pipe_name (str): Name of the pipe for which the instance is to be created.
            time_out_in_seconds (float): time out in seconds in service side.

        Returns:
            HANDLE: The handler for the created named pipe instance.

        """
        pipe_handle = CreateNamedPipeA(
            pipe_name.encode("ascii"),
            # A bi-directional pipe; both server and client processes can read from and write to the pipe.
            PIPE_ACCESS_DUPLEX,
            PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT,
            DEFAULT_MAX_NAMED_PIPE_INSTANCES,
            NAMED_PIPE_BUFFER_SIZE,  # nOutBufferSize
            NAMED_PIPE_BUFFER_SIZE,  # nInBufferSize
            time_out_in_seconds,
            None #TODO: NamedPipeHelper.create_security_attributes(),
        )
        if pipe_handle == INVALID_HANDLE_VALUE:
            return None
        return pipe_handle

    @staticmethod
    def _handle_pipe_exception(winerror: int, funcname: str = "") -> None:
        """
        Handles exceptions related to pipe operations.

        Args:
            winerror (int): The Windows error code
            funcname (str): The name of the function that caused the error

        Raises:
            PipeDisconnectedException: When the pipe is disconnected, broken, or invalid.
        """
        if winerror in [
            ERROR_BROKEN_PIPE,
            ERROR_PIPE_NOT_CONNECTED,
            ERROR_INVALID_HANDLE,
        ]:
            raise PipeDisconnectedException(winerror, funcname)
        else:
            # Import here to get the error message formatting
            from .._win32._error_handling import FormatMessage
            error_message = FormatMessage(winerror)
            raise WindowsError(winerror, funcname, error_message)

    @staticmethod
    def read_from_pipe_target(handle: HANDLE):
        """
        Reads data from a Named Pipe. Times out after timeout_in_seconds.
        Note: This method should be run in a thread with a timeout.
              win32.ReadFile can hang up, causing this to run indefinitely.

        Args:
            handle (HANDLE): The handle to the Named Pipe.
        """
        data_parts: List[str] = []
        while True:
            try:
                return_code, data = ReadFile(handle, NAMED_PIPE_BUFFER_SIZE)
                data_parts.append(data.decode("utf-8"))
                if return_code == ERROR_MORE_DATA:
                    continue
                elif return_code == NO_ERROR:
                    return data_parts
                else:
                    raise IOError(
                        f"Got error when reading from the Named Pipe with error code: {return_code}"
                    )
            # Server maybe shutdown during reading.
            except (OSError, WindowsError) as e:
                # Handle Windows API errors from our ctypes functions
                if hasattr(e, 'winerror'):
                    NamedPipeHelper._handle_pipe_exception(e.winerror, "ReadFile")
                else:
                    raise

    @staticmethod
    def read_from_pipe(handle: HANDLE, timeout_in_seconds: Optional[float] = 5.0) -> str:  # type: ignore
        """
        Reads data from a Named Pipe. Times out after timeout_in_seconds.

        Args:
            handle (HANDLE): The handle to the Named Pipe.
            timeout_in_seconds (Optional[float]): The maximum time in seconds to wait for data before
                raising a TimeoutError. Defaults to 5 seconds. None means waiting indefinitely.

        Returns:
            str: The data read from the Named Pipe.
        """

        with ThreadPoolExecutor(max_workers=1) as executor:
            start_time = time.time()
            future = executor.submit(NamedPipeHelper.read_from_pipe_target, handle)

            try:
                # Retrieve the result of the function with a timeout
                data_parts = future.result(timeout=timeout_in_seconds)
            except TimeoutError:
                # Close the handle will interrupt the ReadFile and the thread will end
                CloseHandle(handle)
                duration = time.time() - start_time
                raise NamedPipeReadTimeoutError(duration)

        return "".join(data_parts)

    @staticmethod
    def write_to_pipe(handle: HANDLE, message: str) -> None:  # type: ignore
        """
        Writes data to a Named Pipe.

        Args:
            handle (HANDLE): The handle to the Named Pipe.
            message (str): The message to write to the Named Pipe.

        """
        try:
            WriteFile(handle, message.encode("utf-8"))
        # Server maybe shutdown during writing.
        except (OSError, WindowsError) as e:
            # Handle Windows API errors from our ctypes functions
            if hasattr(e, 'winerror'):
                NamedPipeHelper._handle_pipe_exception(e.winerror, "WriteFile")
            else:
                raise

    @staticmethod
    def establish_named_pipe_connection(pipe_name: str, timeout_in_seconds: float) -> HANDLE:
        """
        Creates a client handle for connecting to a named pipe server.

        This function attempts to establish a connection to a named pipe server.
        It keeps trying until the connection is successful or the specified timeout is exceeded.
        If the server pipe is not available (either not found or busy), it waits and retries.
        Once connected, the pipe is set to message-read mode.

        Args:
            pipe_name (str): The name of the pipe to connect to.
            timeout_in_seconds (float): The maximum time in seconds to wait for the server pipe
                to become available before raising an error. If None, the function will wait indefinitely.

        Returns:
            HANDLE: A handle to the connected pipe.

        Raises:
            OSError: If the connection cannot be established within the timeout period
                or due to other errors.

        """
        start_time = time.time()
        # Wait for the server pipe to become available.
        handle = None
        while handle is None:
            try:
                handle = CreateFileA(
                    pipe_name.encode("ascii"),  # pipe name
                    # Give the read / write permission
                    GENERIC_READ | GENERIC_WRITE,
                    0,  # Disable the sharing Mode
                    None, # TODO: NamedPipeHelper.create_security_attributes(),
                    OPEN_EXISTING,  # Open existing pipe
                    0,  # No Additional flags
                    None,  # A valid handle to a template file, This parameter is ignored when opening an existing pipe.
                )
            except (OSError, WindowsError) as e:
                # NamedPipe server may be not ready,
                # or no additional resource to create new instance and need to wait for previous connection release
                winerror = getattr(e, 'winerror', 0)
                if winerror in [ERROR_FILE_NOT_FOUND, ERROR_PIPE_BUSY]:
                    duration = time.time() - start_time
                    time.sleep(0.1)
                    # Check timeout limit
                    if duration > timeout_in_seconds:
                        _logger.error(
                            f"NamedPipe Server connect timeout. Duration: {duration} seconds, "
                            f"Timeout limit: {timeout_in_seconds} seconds."
                        )
                        raise NamedPipeConnectTimeoutError(duration, e)
                    continue
                _logger.error(f"Could not open pipe: {e}")
                raise e

        # Switch to message-read mode for the pipe. This ensures that each write operation is treated as a
        # distinct message. For example, a single write operation like "Hello from client." will be read
        # entirely in one request, avoiding partial reads like "Hello fr".
        mode = ctypes.wintypes.DWORD(PIPE_READMODE_MESSAGE)
        SetNamedPipeHandleState(
            handle,  # The handle to the named pipe.
            ctypes.byref(mode),  # Set the pipe to message mode
            # Maximum bytes collected before transmission to the server.
            # 'None' means the system's default value is used.
            None,
            # Maximum time to wait
            # 'None' means the system's default value is used.
            None,
        )

        return handle

    @staticmethod
    def send_named_pipe_request(
        pipe_name: str,
        timeout_in_seconds: Optional[float],
        method: str,
        path: str,
        *,
        params: Optional[Dict] = None,
        json_body: Optional[Dict] = None,
    ) -> Dict:
        """
        Sends a request to a named pipe server and receives the response.

        This method establishes a connection to a named pipe server, sends a JSON-formatted request,
        and waits for a response.

        Args:
            pipe_name (str): The name of the pipe to connect to.
            timeout_in_seconds (Optional[float]): The maximum time in seconds to wait for the server to response.
                None means no timeout.
            method (str): The HTTP method type (e.g., 'GET', 'POST').
            path (str): The request path.
            params (dict, optional): Dictionary of URL parameters to append to the path.
            json_body (dict, optional): Dictionary representing the JSON body of the request.

        Returns:
            Dict: The parsed JSON response from the server.

        Raises:
            OSError: If there are issues in establishing a connection or sending the request.
            json.JSONDecodeError: If there is an error in parsing the server's response.
        """

        handle = NamedPipeHelper.establish_named_pipe_connection(
            pipe_name, DEFAULT_NAMED_PIPE_SERVER_TIMEOUT_IN_SECONDS
        )
        try:
            message_dict = {
                "method": method,
                "path": path,
            }

            if json_body:
                message_dict["body"] = json.dumps(json_body)
            if params:
                message_dict["params"] = json.dumps(params)
            message = json.dumps(message_dict)
            NamedPipeHelper.write_to_pipe(handle, message)
            result = NamedPipeHelper.read_from_pipe(handle, timeout_in_seconds)
        finally:
            CloseHandle(handle)
        return json.loads(result)

    @staticmethod
    def check_named_pipe_exists(pipe_name: str) -> bool:
        """
        Checks if a named pipe exists.

        Args:
            pipe_name (str): The name of the pipe to check.

        Returns:
            bool: True if the pipe exists, False otherwise.
        """
        try:
            handle = CreateFileA(
                pipe_name.encode("ascii"),
                GENERIC_READ,
                0,  # Disable the sharing Mode
                None,  # Don't need any security attributes
                OPEN_EXISTING,  # Open existing pipe
                0,  # No Additional flags
                None,  # A valid handle to a template file, This parameter is ignored when opening an existing pipe.
            )
            CloseHandle(handle)
        except (OSError, WindowsError) as e:
            winerror = getattr(e, 'winerror', 0)
            if winerror == ERROR_FILE_NOT_FOUND:
                return False
        return True

    @staticmethod
    def generate_pipe_name(prefix: str) -> str:
        """
        Generates a unique named pipe name.

        Args:
            prefix (str): The prefix to use for the pipe name.

        Returns:
            str: The unique named pipe name.
        """

        pipe_name = rf"\\.\pipe\{prefix}_{str(os.getpid())}"

        for i in range(5):
            if not NamedPipeHelper.check_named_pipe_exists(pipe_name):
                return pipe_name
            else:
                pipe_name = rf"\\.\pipe\{prefix}_{str(os.getpid())}_{str(i)}_{str(randint(0, 999))}"
        raise NamedPipeNamingError("Cannot find an available pipe name.")
