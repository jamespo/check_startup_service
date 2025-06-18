import unittest
from unittest.mock import patch, MagicMock
from collections import namedtuple

# Import the module and class from check_startup_service.py
from check_startup_service import CheckInitService

Options = namedtuple('Options', ['services', 'matchregex', 'svccmd'])

class TestCheckInitService(unittest.TestCase):

    @patch('check_startup_service.os.popen')
    def test_running_service(self, mock_popen):
        # Simulate a service that is running; output contains "active"
        options = Options(services="service1", 
                          matchregex="(?:^active|is running|start/running)",
                          svccmd="/bin/systemctl")
        # Create a fake output that includes "active"
        fake_output = ["active\n"]
        mock_process = MagicMock()
        mock_process.readlines.return_value = fake_output
        mock_popen.return_value = mock_process

        cis = CheckInitService(options)
        rc = cis.checkinits()
        self.assertEqual(rc, 0)
        self.assertIn("service1", cis.expected_services)

    @patch('check_startup_service.os.popen')
    def test_non_running_service(self, mock_popen):
        # Simulate a service that is not running; output does not match regex
        options = Options(services="service1", 
                          matchregex="(?:^active|is running|start/running)",
                          svccmd="/bin/systemctl")
        # Create a fake output that does NOT match
        fake_output = ["inactive\n"]
        mock_process = MagicMock()
        mock_process.readlines.return_value = fake_output
        mock_popen.return_value = mock_process

        cis = CheckInitService(options)
        rc = cis.checkinits()
        self.assertEqual(rc, 1)
        self.assertIn("service1", cis.rogue_services)

    @patch('check_startup_service.os.popen')
    def test_negated_service(self, mock_popen):
        # Test for a negated service (prefixed with ^) where the service is not running.
        options = Options(services="^service1", 
                          matchregex="(?:^active|is running|start/running)",
                          svccmd="/bin/systemctl")
        # For negated service, if it is not running the output should not match regex.
        fake_output = ["inactive\n"]
        mock_process = MagicMock()
        mock_process.readlines.return_value = fake_output
        mock_popen.return_value = mock_process

        cis = CheckInitService(options)
        rc = cis.checkinits()
        self.assertEqual(rc, 0)
        self.assertIn("^service1", cis.expected_services)
        self.assertNotIn("^service1", cis.rogue_services)

if __name__ == '__main__':
    unittest.main()
