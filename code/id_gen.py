import time
import threading

class SnowflakeIDGenerator:
    def __init__(self, datacenter_id, machine_id):
        # Bit lengths
        self.sequence_bits = 12
        self.machine_bits = 5
        self.datacenter_bits = 5
        self.timestamp_bits = 41

        # Max values
        self.max_sequence = (1 << self.sequence_bits) - 1
        self.max_machine = (1 << self.machine_bits) - 1
        self.max_datacenter = (1 << self.datacenter_bits) - 1

        # Shifts
        self.machine_shift = self.sequence_bits
        self.datacenter_shift = self.sequence_bits + self.machine_bits
        self.timestamp_shift = self.sequence_bits + self.machine_bits + self.datacenter_bits

        # Validate inputs
        if datacenter_id > self.max_datacenter or datacenter_id < 0:
            raise ValueError("Invalid datacenter_id")
        if machine_id > self.max_machine or machine_id < 0:
            raise ValueError("Invalid machine_id")

        self.datacenter_id = datacenter_id
        self.machine_id = machine_id

        # State
        self.sequence = 0
        self.last_timestamp = -1

        # Custom epoch (e.g., 2020-01-01)
        self.epoch = 1577836800000

        self.lock = threading.Lock()

    def _current_millis(self):
        return int(time.time() * 1000)

    def _wait_next_millis(self, last_ts):
        ts = self._current_millis()
        while ts <= last_ts:
            ts = self._current_millis()
        return ts

    def generate(self):
        with self.lock:
            timestamp = self._current_millis()

            if timestamp < self.last_timestamp:
                raise Exception("Clock moved backwards. Refusing to generate id.")

            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & self.max_sequence
                if self.sequence == 0:
                    timestamp = self._wait_next_millis(self.last_timestamp)
            else:
                self.sequence = 0

            self.last_timestamp = timestamp

            snowflake_id = (
                ((timestamp - self.epoch) << self.timestamp_shift) |
                (self.datacenter_id << self.datacenter_shift) |
                (self.machine_id << self.machine_shift) |
                self.sequence
            )

            return snowflake_id


# Example usage
if __name__ == "__main__":
    gen = SnowflakeIDGenerator(datacenter_id=3, machine_id=12)

    for _ in range(5):
        print(gen.generate())
