"""
Module for splitting a dataset into training and validation sets.
Splits the dataset using a greedy approach based on the total object (coin) count to ensure even distribution of dense and sparse images.
"""
import os
import shutil
import argparse

class DatasetSplitter:
    """
    Handles the distribution of image and label files into train and val directories
    by sorting images by object count and greedily assigning them to maintain the split ratio.
    """
    def __init__(self, source_dir, target_dir, split_ratio=0.8):
        """
        Initializes the dataset splitter.
        """
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.split_ratio = split_ratio

    def setup_directories(self):
        """
        Creates the necessary directory structure for YOLOv8.
        """
        directories = [
            os.path.join(self.target_dir, 'images', 'train'),
            os.path.join(self.target_dir, 'images', 'val'),
            os.path.join(self.target_dir, 'labels', 'train'),
            os.path.join(self.target_dir, 'labels', 'val')
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def count_objects_in_file(self, label_path):
        """
        Reads the label file and returns the number of objects (lines).
        Returns 0 if the file does not exist.
        """
        if not os.path.exists(label_path):
            return 0
        with open(label_path, 'r') as f:
            return len([line for line in f if line.strip()])

    def split_data(self):
        """
        Calculates the object count per image, sorts them descending, and distributes
        files to maintain the target split ratio of total objects.
        """
        self.setup_directories()

        images_dir = os.path.join(self.source_dir, 'images')
        labels_dir = os.path.join(self.source_dir, 'labels')

        all_images = [f for f in os.listdir(images_dir) if f.endswith('.jpg')]

        image_data = []
        total_objects = 0

        for image_name in all_images:
            label_name = image_name.replace('.jpg', '.txt')
            label_path = os.path.join(labels_dir, label_name)
            obj_count = self.count_objects_in_file(label_path)
            image_data.append((image_name, obj_count))
            total_objects += obj_count

        image_data.sort(key=lambda x: x[1], reverse=True)

        train_images = []
        val_images = []
        current_train_objects = 0
        current_val_objects = 0

        for image_name, obj_count in image_data:
            current_total = current_train_objects + current_val_objects
            if current_total == 0:
                current_ratio = 0.0
            else:
                current_ratio = current_train_objects / current_total

            if current_ratio < self.split_ratio:
                train_images.append(image_name)
                current_train_objects += obj_count
            else:
                val_images.append(image_name)
                current_val_objects += obj_count

        for image_name in train_images:
            label_name = image_name.replace('.jpg', '.txt')
            shutil.copy(os.path.join(images_dir, image_name), os.path.join(self.target_dir, 'images', 'train', image_name))
            if os.path.exists(os.path.join(labels_dir, label_name)):
                shutil.copy(os.path.join(labels_dir, label_name), os.path.join(self.target_dir, 'labels', 'train', label_name))

        for image_name in val_images:
            label_name = image_name.replace('.jpg', '.txt')
            shutil.copy(os.path.join(images_dir, image_name), os.path.join(self.target_dir, 'images', 'val', image_name))
            if os.path.exists(os.path.join(labels_dir, label_name)):
                shutil.copy(os.path.join(labels_dir, label_name), os.path.join(self.target_dir, 'labels', 'val', label_name))

        print("Dataset split complete based on object count.")
        print(f"Total Objects: {total_objects}")
        print(f"Train Objects: {current_train_objects} ({len(train_images)} images)")
        print(f"Val Objects: {current_val_objects} ({len(val_images)} images)")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Split dataset via command line arguments.")
    parser.add_argument('--source', type=str, required=True, help="Path to the input directory")
    parser.add_argument('--target', type=str, required=True, help="Path to the output directory")
    parser.add_argument('--ratio', type=float, default=0.9, help="Split ratio for training data")

    args = parser.parse_args()

    splitter = DatasetSplitter(args.source, args.target, args.ratio)
    splitter.split_data()