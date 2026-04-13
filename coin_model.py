import sys
import os
import cv2
import yaml
import re
from collections import defaultdict
from ultralytics import YOLO


def get_external_path(relative_path):
    """
    Returns the path to a file located in the same directory as the executable.
    """
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class CoinModel:
    """
    Handles AI inference, configuration loading, data calculations, and validation.
    """

    def __init__(self):
        """
        Initializes defaults and paths for the AI model and configuration.
        """
        self.currency = "CZK"
        self.coin_values = {}
        self.model = None

    def load_model_and_config(self):
        """
        Loads the YOLO model, parses the YAML configuration, and validates class mapping.
        Checks for the existence of the required directory and files.
        Returns a tuple of boolean success state and error message.
        """
        model_dir = get_external_path("AI_model")
        if not os.path.exists(model_dir):
            return False, f"Missing directory. Please ensure the 'AI_model' folder exists at: {model_dir}"

        model_path = os.path.join(model_dir, "best.pt")
        if not os.path.exists(model_path):
            return False, f"Missing model file. Could not find 'best.pt' at: {model_path}"

        yaml_path = os.path.join(model_dir, "data.yaml")
        if not os.path.exists(yaml_path):
            return False, f"Missing configuration file. Could not find 'data.yaml' at: {yaml_path}"

        self.model = YOLO(model_path)

        try:
            with open(yaml_path, "r") as file:
                data = yaml.safe_load(file)

            if not isinstance(data, dict) or "names" not in data:
                return False, "The data.yaml file is missing the 'names' list."

            names_list = data["names"]
            if not isinstance(names_list, list):
                return False, "The 'names' key in data.yaml is not a valid list."

            currency_found = False
            for name in names_list:
                val_match = re.search(r'\d+', str(name))
                if val_match:
                    self.coin_values[str(name)] = int(val_match.group())
                    if not currency_found:
                        curr_match = re.search(r'[a-zA-Z]+', str(name))
                        if curr_match:
                            self.currency = curr_match.group().upper()
                            currency_found = True
        except Exception as exc:
            return False, str(exc)

        model_classes = list(self.model.names.values())
        yaml_classes = list(self.coin_values.keys())

        unmapped_classes = [cls for cls in model_classes if cls not in yaml_classes]

        if len(unmapped_classes) > 0 and len(yaml_classes) > 0:
            overlap = set(model_classes).intersection(set(yaml_classes))
            if not overlap:
                return False, "Model mismatch. The AI model predicts items not listed in data.yaml."

        return True, ""

    def process_image(self, file_path):
        """
        Runs the YOLO model on a single image and calculates its coin values.
        Returns the annotated image array, local total value, local total count, and coin counts dictionary.
        """
        image = cv2.imread(file_path)
        if image is None:
            return None, 0, 0, {}

        results = self.model(image)
        annotated_image = image.copy()

        local_total_value = 0
        local_total_count = 0
        local_coin_counts = defaultdict(int)

        for result in results:
            annotated_image = result.plot()
            for box in result.boxes:
                class_id = int(box.cls[0])
                class_name = self.model.names[class_id]

                if class_name in self.coin_values:
                    local_total_value += self.coin_values[class_name]
                    local_total_count += 1
                    local_coin_counts[class_name] += 1

        return annotated_image, local_total_value, local_total_count, local_coin_counts