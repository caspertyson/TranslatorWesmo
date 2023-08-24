import csv

class CanMessageInterpreter:
    def __init__(self):
        self.interpretations = {}

    def load_interpretations_from_csv(self, filename):
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                canid = row[0]
                self.interpretations[canid] = []
                i = 1
                while i < len(row):
                    byte_count = int(row[i])
                    name = row[i+1]
                    self.interpretations[canid].append((name, byte_count))
                    i += 2

    def interpret(self, message):
        parts = message.split()
        canid = parts[0]
        if canid not in self.interpretations:
            return None
        interpretations = self.interpretations[canid]
        byte_parts = parts[1:]
        results = {}
        i = 0
        for name, byte_count in interpretations:
            bytes_value = byte_parts[i:i+byte_count]
            int_value = 0
            for b in bytes_value:
                int_value = (int_value << 8) + int(b, 16)
            results[name] = int_value
            i += byte_count
        return canid, results
