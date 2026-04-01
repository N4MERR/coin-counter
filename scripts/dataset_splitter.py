"""
Module for splitting a YOLO dataset into training and validation sets.
Accepts command-line arguments for source, target, and split ratio.
"""
import os
import shutil
import random
import argparse

class DatasetSplitter:
    """
    Handles the random distribution of image and label files into train and val directories.
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

    def split_data(self):
        """
        Moves files from the source directory to the randomized train and val folders.
        """
        self.setup_directories()

        images_dir = os.path.join(self.source_dir, 'images')
        labels_dir = os.path.join(self.source_dir, 'labels')

        all_images = [f for f in os.listdir(images_dir) if f.endswith('.jpg')]
        random.shuffle(all_images)

        split_index = int(len(all_images) * self.split_ratio)
        train_images = all_images[:split_index]
        val_images = all_images[split_index:]

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

        print(f"Dataset split complete. Train: {len(train_images)}, Val: {len(val_images)}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Split dataset via command line arguments.")
    parser.add_argument('--source', type=str, required=True, help="Path to the input directory")
    parser.add_argument('--target', type=str, required=True, help="Path to the output directory")
    parser.add_argument('--ratio', type=float, default=0.9, help="Split ratio for training data")

    args = parser.parse_args()

    splitter = DatasetSplitter(args.source, args.target, args.ratio)
    splitter.split_data()
