from unittest import TestCase

from mock import MagicMock, patch

from pyinfra.api import Config, State
from pyinfra.api.connect import connect_all

from ..util import make_inventory


class TestWinrmConnector(TestCase):
    def setUp(self):
        self.fake_connect_patch = patch('pyinfra.api.connectors.winrm.connect')
        self.fake_connect_mock = self.fake_connect_patch.start()

    def tearDown(self):
        self.fake_connect_patch.stop()

    def test_connect_host(self):
        inventory = make_inventory()
        state = State(inventory, Config())
        host = inventory.get_host('somehost')
        host.connect(state, for_fact=True)
        self.assertEqual(len(state.active_hosts), 0)

    def test_connect_all_password(self):
        inventory = make_inventory(hosts=(
            ('@winrm/somehost', {'winrm_username': 'testuser', 'winrm_password': 'testpass'}),
            ('@winrm/anotherhost', {'winrm_username': 'testuser2', 'winrm_password': 'testpass2'}),
        ))
        state = State(inventory, Config())
        connect_all(state)

        # Get a host
        somehost = inventory.get_host('@winrm/somehost')
        self.assertEqual(somehost.data.winrm_username, 'testuser')
        self.assertEqual(somehost.data.winrm_password, 'testpass')

        self.assertEqual(len(state.active_hosts), 2)

    def test_run_shell_command(self):
        fake_winrm_session = MagicMock()

        fake_winrm = MagicMock()
        fake_stdin = MagicMock()
        fake_stdout = MagicMock()
        fake_winrm.run_cmd.return_value = fake_stdin, fake_stdout, MagicMock()

        fake_winrm_session.return_value = fake_winrm

        inventory = make_inventory(hosts=('@winrm/somehost',))
        state = State(inventory, Config())
        host = inventory.get_host('@winrm/somehost')
        host.connect(state)

        command = 'echo hi'

        out = host.run_shell_command(state, command, stdin='hello', print_output=True)
        assert len(out) == 3

        status, stdout, stderr = out
        # TODO: assert status is True

        combined_out = host.run_shell_command(
            state, command, print_output=True,
            return_combined_output=True,
        )
        assert len(combined_out) == 2

        # TODO: fake_winrm.run_shell_command.assert_called_with("'echo hi'", get_pty=False)
