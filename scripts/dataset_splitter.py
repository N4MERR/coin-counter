"""
Module for splitting a dataset into training and validation sets.
Splits the dataset based on the total object (coin) count rather than image count.
"""
import os
import shutil
import random
import argparse

class DatasetSplitter:
    """
    Handles the random distribution of image and label files into train and val directories
    based on the object count found in the label files.
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
        Calculates the object count per image, shuffles the dataset, and distributes
        files to reach the target split ratio based on total objects.
        """
        self.setup_directories()

        images_dir = os.path.join(self.source_dir, 'images')
        labels_dir = os.path.join(self.source_dir, 'labels')

        all_images = [f for f in os.listdir(images_dir) if f.endswith('.jpg')]
        random.shuffle(all_images)

        image_object_counts = {}
        total_objects = 0

        for image_name in all_images:
            label_name = image_name.replace('.jpg', '.txt')
            label_path = os.path.join(labels_dir, label_name)
            obj_count = self.count_objects_in_file(label_path)
            image_object_counts[image_name] = obj_count
            total_objects += obj_count

        target_train_objects = int(total_objects * self.split_ratio)
        current_train_objects = 0

        train_images = []
        val_images = []

        for image_name in all_images:
            if current_train_objects < target_train_objects:
                train_images.append(image_name)
                current_train_objects += image_object_counts[image_name]
            else:
                val_images.append(image_name)

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

        val_objects = total_objects - current_train_objects
        print("Dataset split complete based on object count.")
        print(f"Total Objects: {total_objects}")
        print(f"Train Objects: {current_train_objects} ({len(train_images)} images)")
        print(f"Val Objects: {val_objects} ({len(val_images)} images)")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Split dataset via command line arguments.")
    parser.add_argument('--source', type=str, required=True, help="Path to the input directory")
    parser.add_argument('--target', type=str, required=True, help="Path to the output directory")
    parser.add_argument('--ratio', type=float, default=0.9, help="Split ratio for training data")

    args = parser.parse_args()

    splitter = DatasetSplitter(args.source, args.target, args.ratio)
    splitter.split_data()
