"""
This script parses a YOLO formatted dataset directory to calculate total image count,
total object counts per class, and a grand total of all objects.
"""

import os
import sys
import argparse

def read_classes(classes_path):
    """
    Reads the classes.txt file and returns a dictionary mapping class IDs to names.
    Exits the script if the file is not found.
    """
    class_mapping = {}
    if not os.path.isfile(classes_path):
        print(f"Error: classes.txt not found at {classes_path}")
        sys.exit(1)
        
    with open(classes_path, 'r') as f:
        lines = f.readlines()
        for idx, line in enumerate(lines):
            class_mapping[idx] = line.strip()
            
    return class_mapping

def process_dataset(dataset_path):
    """
    Locates the labels directory and processes all .txt files to aggregate
    file counts and class-specific object counts.
    """
    classes_path = os.path.join(dataset_path, 'classes.txt')
    labels_path = os.path.join(dataset_path, 'labels')
    
    class_mapping = read_classes(classes_path)
    
    if not os.path.isdir(labels_path):
        print(f"Error: labels directory not found at {labels_path}")
        sys.exit(1)
        
    total_counts = {name: 0 for name in class_mapping.values()}
    total_files = 0
    grand_total = 0

    for file in os.listdir(labels_path):
        if file.endswith('.txt') and file != 'classes.txt':
            total_files += 1
            file_path = os.path.join(labels_path, file)
            
            with open(file_path, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    parts = line.split()
                    if parts:
                        class_id = int(parts[0])
                        class_name = class_mapping.get(class_id, f"Unknown_ID_{class_id}")
                        
                        if class_name not in total_counts:
                            total_counts[class_name] = 0
                        
                        total_counts[class_name] += 1
                        grand_total += 1

    print("--- Dataset Label Summary ---")
    print(f"Total image count (label files): {total_files}")
    print("Total coins per class:")
    for coin_type, count in total_counts.items():
        print(f"  {coin_type}: {count}")
    print(f"Grand Total Coins: {grand_total}")
    print("-----------------------------")

if __name__ == "__main__":
    """
    Entry point for the script. Parses command line arguments and triggers processing.
    """
    parser = argparse.ArgumentParser(description="Count YOLO labels from a dataset path.")
    parser.add_argument("dataset_path", type=str, help="Path to the dataset directory containing classes.txt and the labels folder")
    args = parser.parse_args()
    
    process_dataset(args.dataset_path)
