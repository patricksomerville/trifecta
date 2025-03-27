
class DataProcessor:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file
        self.data = []
        self.processed_data = []
        
    def process_data(self):
        for item in self.data:
            if item and "key" in item and item["key"] > 10:
                self.processed_data.append(item["value"])
        return len(self.processed_data)
    
    def save_results(self):
        with open(self.output_file, "w") as f:
            for item in self.processed_data:
                f.write(f"{item}\n")
                
def validate_inputs(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} does not exist")
        return False
    return True

def main():
    processor = DataProcessor("input.json", "output.txt")
    processor.process_data()
    processor.save_results()
