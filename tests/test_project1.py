import sys
import os
from pathlib import Path
import tempfile
from io import StringIO
import unittest


project1_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project1_dir)

from project1 import DeviceSimulation


class TestProject1(unittest.TestCase):
    def setUp(self):
        # You can set up any initial conditions or variables needed for testing here.
        self.simulation = DeviceSimulation()

    def test_parse_device_line(self):
        # Test parsing DEVICE line
        line = "DEVICE 1\n"
        self.simulation._parse_device_line(line)
        self.assertEqual(self.simulation.device_states[1],
                         {'alerts': set(), 'cancellations': set()})
        line = "DEVICE 2\n"
        self.simulation._parse_device_line(line)
        self.assertEqual(self.simulation.device_states[2],
                         {'alerts': set(), 'cancellations': set()})

    def test_parse_propagate_line(self):
        # Test parsing PROPAGATE line
        line = "PROPAGATE 1 2 750\n"
        self.simulation._parse_propagate_line(line)
        self.assertEqual(self.simulation.propagation_rules[1], [(2, 750)])
        line = "PROPAGATE 2 3 1250\n"
        self.simulation._parse_propagate_line(line)
        self.assertEqual(self.simulation.propagation_rules[2], [(3, 1250)])

    def test_parse_alert_line(self):
        # Test parsing ALERT line
        line = "ALERT 1 Trouble 0\n"
        self.simulation._parse_alert_line(line)
        self.assertEqual(self.simulation.alerts, [(1, 'Trouble', 0)])

    def test_parse_cancel_line(self):
        # Test parsing CANCEL line
        line = "CANCEL 1 Trouble 2200\n"
        self.simulation._parse_cancel_line(line)
        self.assertEqual(self.simulation.cancellations, [(1, 'Trouble', 2200)])

    def test_parse_input(self):
        # Create a temporary input file with sample data
        with tempfile.NamedTemporaryFile(mode = 'w', delete = False) as temp_file:
            temp_file.write("LENGTH 10\n")
            temp_file.write("DEVICE 1\n")
            temp_file.write("PROPAGATE 1 2 3\n")
            temp_file.write("ALERT 1 Description 5\n")
            temp_file.write("CANCEL 1 Description 7\n")

        input_file_path = Path(temp_file.name)  # Get the path to the temporary file

        # Call the parse_input method to parse the temporary input file
        self.simulation.parse_input(input_file_path)

        # Check if the parsed data matches the expected values
        self.assertEqual(self.simulation.end_time, 10)
        self.assertEqual(self.simulation.device_states,
                         {1: {'alerts': set(), 'cancellations': set()}})
        self.assertEqual(self.simulation.propagation_rules, {1: [(2, 3)]})
        self.assertEqual(self.simulation.alerts, [(1, 'Description', 5)])
        self.assertEqual(self.simulation.cancellations, [(1, 'Description', 7)])

    def test_read_input_file_path_existing_file(self):
        # Create a StringIO object to simulate user input
        input_text = "samples/sample_input.txt\n"
        sys.stdin = StringIO(input_text)
        input_file_path = self.simulation.read_input_file_path()
        # Assert that the returned input file path is of type Path
        self.assertIsInstance(input_file_path, Path)
        # Assert that the file exists
        self.assertTrue(input_file_path.is_file())
    def test_read_input_file_path_nonexistent_file(self):
        input_text = "samples/nonexistent_file.txt\n"
        sys.stdin = StringIO(input_text)
        # Use assertRaises to catch the expected SystemExit
        with self.assertRaises(SystemExit):
            self.simulation.read_input_file_path()

    def test_simulate(self):
        # Prepare test data and expected output
        input_text = "samples/sample_input.txt\n"
        expected_output = """@0: #1 SENT ALERT TO #2: Trouble
@750: #2 RECEIVED ALERT FROM #1: Trouble
@750: #2 SENT ALERT TO #3: Trouble
@2000: #3 RECEIVED ALERT FROM #2: Trouble
@2000: #3 SENT ALERT TO #4: Trouble
@2200: #1 SENT CANCELLATION TO #2: Trouble
@2500: #4 RECEIVED ALERT FROM #3: Trouble
@2500: #4 SENT ALERT TO #1: Trouble
@2950: #2 RECEIVED CANCELLATION FROM #1: Trouble
@2950: #2 SENT CANCELLATION TO #3: Trouble
@3500: #1 RECEIVED ALERT FROM #4: Trouble
@4200: #3 RECEIVED CANCELLATION FROM #2: Trouble
@4200: #3 SENT CANCELLATION TO #4: Trouble
@4700: #4 RECEIVED CANCELLATION FROM #3: Trouble
@4700: #4 SENT CANCELLATION TO #1: Trouble
@5700: #1 RECEIVED CANCELLATION FROM #4: Trouble
@9999: END
"""
        sys.stdin = StringIO(input_text)
        # Redirect stdout to capture the output
        sys.stdout = StringIO()
        # Call the simulate method
        self.simulation.run()
        # Get the actual output
        actual_output = sys.stdout.getvalue()
        # Assert that the actual output matches the expected output
        self.assertEqual(actual_output, expected_output)

if __name__ == '__main__':
    unittest.main()

