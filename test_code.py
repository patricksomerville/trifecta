#!/usr/bin/env python3

import os
import sys
import time
import re
import json

class DataProcessor:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file
        self.data = []
        self.processed_data = []
        
    def load_data(self):
        with open(self.input_file, 'r') as f:
            self.data = json.load(f)
        return len(self.data)
    
    def process_data(self):
        for item in self.data:
            if 'name' in item and 'value' in item:
                processed_item = {}
                processed_item['id'] = item.get('id', 'unknown')
                processed_item['name'] = item['name'].upper()
                processed_item['value'] = float(item['value']) * 1.1
                processed_item['timestamp'] = time.time()
                self.processed_data.append(processed_item)
        return len(self.processed_data)
    
    def save_data(self):
        with open(self.output_file, 'w') as f:
            json.dump(self.processed_data, f, indent=2)
        return os.path.getsize(self.output_file)
    
    def run(self):
        self.load_data()
        self.process_data()
        self.save_data()
        print(f"Processed {len(self.processed_data)} items")

def parse_arguments():
    if len(sys.argv) < 3:
        print("Usage: python test_code.py <input_file> <output_file>")
        sys.exit(1)
    return sys.argv[1], sys.argv[2]

def validate_file(file_path, check_exists=True):
    if check_exists and not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist.")
        sys.exit(1)
    
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except OSError:
            print(f"Error: Could not create directory {directory}")
            sys.exit(1)
    return True

def main():
    input_file, output_file = parse_arguments()
    validate_file(input_file)
    validate_file(output_file, False)
    
    processor = DataProcessor(input_file, output_file)
    processor.run()
    
    # Check if output file was created and is not empty
    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        print(f"Successfully processed data from {input_file} to {output_file}")
    else:
        print("Error: Processing failed or output file is empty")

if __name__ == "__main__":
    main()