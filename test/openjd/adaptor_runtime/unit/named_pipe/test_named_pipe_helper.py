# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

from openjd.adaptor_runtime._osname import OSName
from unittest.mock import patch, MagicMock
import pytest
import os
import re
import time

named_pipe_helper = pytest.importorskip(
    "openjd.adaptor_runtime_client.named_pipe.named_pipe_helper"
)
# Import our ctypes implementations (Windows only)
if OSName.is_windows():
    from ctypes.wintypes import HANDLE
    from openjd.adaptor_runtime_client._win32._error_handling import WindowsError
    from openjd.adaptor_runtime_client._win32._constants import NO_ERROR, ERROR_MORE_DATA, ERROR_FILE_NOT_FOUND
    from openjd.adaptor_runtime_client._win32._named_pipes import CreateFileA


class MockReadFile:
    @staticmethod
    def ReadFile(handle: HANDLE, buffer):
        time.sleep(0.5)
        return NO_ERROR, bytes("fake_data", "utf-8")


@pytest.mark.skipif(not OSName.is_windows(), reason="Windows-specific tests")
class TestNamedPipeHelper:
    @patch.object(
        named_pipe_helper, "CreateFile", side_effect=WindowsError(ERROR_FILE_NOT_FOUND, "CreateFile", "The system cannot find the file specified.")
    )
    def test_establish_named_pipe_connection_timeout_raises_exception(self, mock_create_file):
        with pytest.raises(named_pipe_helper.NamedPipeConnectTimeoutError):
            named_pipe_helper.NamedPipeHelper.establish_named_pipe_connection("fakepipe", 1.0)

    @patch.object(named_pipe_helper, "ReadFile", wraps=MockReadFile.ReadFile)
    @patch.object(named_pipe_helper, "CloseHandle", return_value=True)
    def test_read_from_pipe_timeout_raises_exception(self, mock_read_file, mock_close_handle):
        mock_handle = MagicMock(spec=HANDLE)
        with pytest.raises(
            named_pipe_helper.NamedPipeReadTimeoutError,
            match="NamedPipe Server read timeout after \\d\\.\\d+ seconds.$",
        ):
            named_pipe_helper.NamedPipeHelper.read_from_pipe(mock_handle, 0.1)

        mock_close_handle.assert_called_once()

    @patch("os.getpid", return_value=1)
    @patch(
        "openjd.adaptor_runtime_client.named_pipe.named_pipe_helper.NamedPipeHelper.check_named_pipe_exists",
        return_value=False,
    )
    def test_generate_pipe_name(self, mock_check_named_pipe_exists, mock_getpid):
        name = named_pipe_helper.NamedPipeHelper.generate_pipe_name("AdaptorTest")
        assert name == r"\\.\pipe\AdaptorTest_1"

    @patch("os.getpid", return_value=1)
    @patch(
        "openjd.adaptor_runtime_client.named_pipe.named_pipe_helper.NamedPipeHelper.check_named_pipe_exists",
        side_effect=[True, False],
    )
    def test_generate_pipe_name2(self, mock_check_named_pipe_exists, mock_getpid):
        # This test is to ensure that the pipe name will change when it already exists.
        name = named_pipe_helper.NamedPipeHelper.generate_pipe_name("AdaptorTest")
        assert r"\\.\pipe\AdaptorTest_1_0_" in name

    @patch("os.getpid", return_value=1)
    @patch(
        "openjd.adaptor_runtime_client.named_pipe.named_pipe_helper.NamedPipeHelper.check_named_pipe_exists",
        return_value=True,
    )
    def test_failed_to_generate_pipe_name(self, mock_check_named_pipe_exists, mock_getpid):
        with pytest.raises(
            named_pipe_helper.NamedPipeNamingError,
            match="Cannot find an available pipe name.",
        ):
            named_pipe_helper.NamedPipeHelper.generate_pipe_name("AdaptorTest")
