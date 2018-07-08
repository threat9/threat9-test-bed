import socket

from threat9_test_bed.service_mocks import TCPServiceMock


def test_tcp_service_mock_get_command_mock():
    with TCPServiceMock("127.0.0.1", 8023) as target:
        assert target.host == "127.0.0.1"
        assert target.port == 8023

        mocked_scoo = target.get_command_mock(b"scoo")
        mocked_scoo.return_value = b"bee"
        mocked_doo = target.get_command_mock(b"doo")
        mocked_doo.return_value = b"where are you?"
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((target.host, target.port))
            s.send(b"doo")
            assert s.recv(1024) == b"where are you?"
            s.send(b"scoo")
            assert s.recv(1024) == b"bee"
