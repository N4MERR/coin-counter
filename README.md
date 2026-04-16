# Coin Counter

**Author:** Zhao Xiang Yang | **School:** SPŠE Ječná | **Project Type:** School Project

A desktop application designed to detect, classify, and count coins using machine learning.

## Installation and Execution

No installation or internet connection is required to run the compiled application.

1. **[Download the Latest Version](https://github.com/N4MERR/coin-counter/releases/latest)**
2. Download the `coin_value_predictor.zip` file.
3. Extract the folder to your computer.
4. Run the `.exe` file.

## How It Works

### Workflow
1. Launch the application.
2. Upload a single image or multiple images (JPG or PNG).
3. The app processes the image and runs the YOLOv8 model.
4. Detected coins and their values are displayed in the GUI.

## Configuration & Custom AI Models

The application allows you to swap or upgrade the AI model. 

### Changing the Model
1. Place your model in the `AI_model` folder.
2. Ensure the model is in `.pt` format.
3. Provide a corresponding `.yaml` configuration file in the same folder.

**Example YAML Configuration:**
```yaml
path: /content/split_dataset
train: images/train
val: images/val
test: /content/test_data

nc: 6
names:
  - 10kc
  - 1kc
  - 20kc
  - 2kc
  - 50kc
  - 5kc
```

### Training a New Model
To improve detection accuracy or add support for new coins, you can train a custom YOLOv8 model.
* **Guide:** [AI Model Training Guide](https://drive.google.com/drive/folders/1b6icp6LVGExb0CjP5T9gkbILRX_tSvUS?usp=drive_link)

## Performance & Known Issues

The current model was tested with Czech coins (1, 2, 5, 10, 20, 50 CZK) under various lighting conditions and multi-image batches.

* **High Accuracy:** 10, 20, and 50 CZK coins.
* **Lower Accuracy:** 1, 2, and 5 CZK coins.
* **Known Issues:** The model is sensitive to image quality, and struggles differentiating the smaller denomination coins.

## Technical Architecture

* **GUI:** PySide (Provides the user interface)
* **Inference Module:** YOLOv8 / Ultralytics (Performs coin detection and classification)
* **Image Processing:** OpenCV (Handles image preprocessing)
* **Language:** Python
