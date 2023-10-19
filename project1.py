from pathlib import Path
import heapq


class DeviceSimulation:
    def __init__(self):
        self.device_states = {}
        self.propagation_rules = {}
        self.alerts = []
        self.cancellations = []
        self.end_time = 0
        self.events = []

    def _parse_device_line(self, line: str):
        parts = line.split()
        device_id = int(parts[1])
        self.device_states[device_id] = {'alerts': set(), 'cancellations': set()}

    def _parse_propagate_line(self, line: str):
        parts = line.split()
        sender_id = int(parts[1])
        receiver_id = int(parts[2])
        delay = int(parts[3])
        if sender_id not in self.propagation_rules:
            self.propagation_rules[sender_id] = []
        self.propagation_rules[sender_id].append((receiver_id, delay))

    def _parse_alert_line(self, line: str):
        parts = line.split()
        device_id = int(parts[1])
        description = parts[2]
        time = int(parts[3])
        self.alerts.append((device_id, description, time))

    def _parse_cancel_line(self, line: str):
        parts = line.split()
        device_id = int(parts[1])
        description = parts[2]
        time = int(parts[3])
        self.cancellations.append((device_id, description, time))

    def parse_input(self, input_file: Path):
        with input_file.open() as file:
            for line in file:
                if line.startswith('LENGTH'):
                    self.end_time = int(line.split()[1])
                elif line.startswith('DEVICE'):
                    self._parse_device_line(line)
                elif line.startswith('PROPAGATE'):
                    self._parse_propagate_line(line)
                elif line.startswith('ALERT'):
                    self._parse_alert_line(line)
                elif line.startswith('CANCEL'):
                    self._parse_cancel_line(line)

    def simulate(self, input_file: Path):
        self.parse_input(input_file)
        simulation_time = 0

        # Initialize a priority queue for events
        self.events = [(time, 'ALERT', device_id, 0, description) for device_id, description, time
                       in self.alerts] + \
                      [(time, 'CANCEL', device_id, 0, description) for device_id, description, time
                       in self.cancellations]

        heapq.heapify(self.events)

        while simulation_time < self.end_time:

            while self.events and self.events[0][0] <= simulation_time:
                event_time, event_type, device_id, from_id, description = heapq.heappop(self.events)

                if event_type == 'ALERT':
                    # Handle alert event
                    if from_id != 0:
                        print(
                            f'@{simulation_time}: #{device_id} RECEIVED ALERT FROM #{from_id}: {description}')
                    if description not in self.device_states[device_id]['cancellations']:
                        self.device_states[device_id]['alerts'].add(description)

                        # Propagate the alert to connected devices
                        for receiver_id, delay in self.propagation_rules.get(device_id, []):
                            receiver_time = simulation_time + delay
                            heapq.heappush(self.events, (
                            receiver_time, 'ALERT', receiver_id, device_id, description))
                            print(
                                f'@{simulation_time}: #{device_id} SENT ALERT TO #{receiver_id}: {description}')

                elif event_type == 'CANCEL':
                    # Handle cancellation event
                    if from_id != 0:
                        print(
                            f'@{simulation_time}: #{device_id} RECEIVED CANCELLATION FROM #{from_id}: {description}')
                    if description in self.device_states[device_id]['alerts']:
                        # Cancel the alert for the device and propagate the cancellation
                        self.device_states[device_id]['alerts'].remove(description)
                        self.device_states[device_id]['cancellations'].add(description)
                        # Propagate the alert to connected devices
                        for receiver_id, delay in self.propagation_rules.get(device_id, []):
                            receiver_time = simulation_time + delay
                            heapq.heappush(self.events, (
                            receiver_time, 'CANCEL', receiver_id, device_id, description))
                            print(
                                f'@{simulation_time}: #{device_id} SENT CANCELLATION TO #{receiver_id}: {description}')

            simulation_time += 1  # Move the simulation time forward

        # End of simulation
        print(f'@{simulation_time}: END')

    def read_input_file_path(self) -> Path:
        input_file_path = Path(input())
        if not input_file_path.exists():
            print("FILE NOT FOUND")
            exit()  # Terminate the program if the file does not exist
        return input_file_path

    def run(self):
        input_file_path = self.read_input_file_path()
        self.simulate(input_file_path)


if __name__ == '__main__':
    simulation = DeviceSimulation()
    simulation.run()
