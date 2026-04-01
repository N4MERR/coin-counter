"""
Module for generating data.yaml configuration file.
"""
import yaml
import argparse
import os

def generate_yaml(dataset_path, split_data_path, output_file, classes_filename):
    """
    Reads class names from a text file in the original dataset and generates a YAML configuration pointing to the split dataset.
    """
    classes_path = os.path.join(dataset_path, classes_filename)
    
    if not os.path.exists(classes_path):
        raise FileNotFoundError(f"Could not find the classes file at: {classes_path}")

    with open(classes_path, 'r', encoding='utf-8') as file_handler:
        class_names = [line.strip() for line in file_handler.readlines() if line.strip()]

    config_data = {
        'path': split_data_path,
        'train': 'images/train',
        'val': 'images/val',
        'nc': len(class_names),
        'names': class_names
    }
    
    with open(output_file, 'w', encoding='utf-8') as file_handler:
        yaml.dump(config_data, file_handler, default_flow_style=False, sort_keys=False)
        
    print(f"Successfully generated '{output_file}' pointing to '{split_data_path}'")

if __name__ == '__main__':
    """
    Parses command-line arguments and triggers the YAML generation process.
    """
    parser = argparse.ArgumentParser(description="Generate YOLO data.yaml file dynamically from classes.txt.")
    parser.add_argument('--path', type=str, required=True, help="Path to the original dataset containing classes.txt")
    parser.add_argument('--split_data_path', type=str, required=True, help="Path to your split dataset directory")
    parser.add_argument('--output', type=str, default='/content/data.yaml', help="Where to save the yaml file")
    parser.add_argument('--classes', type=str, default='classes.txt', help="Name of the classes file inside the original dataset folder")
    
    args = parser.parse_args()
    generate_yaml(args.path, args.split_data_path, args.output, args.classes)
