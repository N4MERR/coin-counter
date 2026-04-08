import sys
import os
import cv2
import yaml
import re
from collections import defaultdict
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QWidget, \
    QFileDialog, QMessageBox, QStackedWidget, QScrollArea, QCheckBox, QFrame
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt
from ultralytics import YOLO


class CoinCounterApp(QMainWindow):
    """
    Main application window for the Coin Counter Monolith.
    Manages state transitions, dynamic YAML configuration, batch processing,
    context-aware UI layout, and interactive filtering.
    """

    def __init__(self):
        """
        Initializes the stacked UI layout, the scrollable image area, loads the YAML configuration,
        initializes the YOLO model, and prepares the data storage list.
        """
        super().__init__()
        self.setWindowTitle("Coin Value Predictor")
        self.setGeometry(100, 100, 1200, 800)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.init_startup_screen()
        self.init_main_screen()

        self.currency = "CZK"
        self.model = YOLO("best.pt")
        self.coin_values = self.load_yaml_config()
        self.image_data_list = []

        self.stacked_widget.setCurrentIndex(0)

    def init_startup_screen(self):
        """
        Creates the initial screen featuring only a large, centered upload button.
        """
        self.startup_widget = QWidget()
        layout = QVBoxLayout(self.startup_widget)

        btn_layout = QHBoxLayout()
        self.startup_upload_btn = QPushButton("Upload Photo(s)")
        self.startup_upload_btn.setFixedSize(300, 80)
        self.startup_upload_btn.setStyleSheet("font-size: 22px; font-weight: bold;")
        self.startup_upload_btn.clicked.connect(self.upload_files)

        btn_layout.addStretch()
        btn_layout.addWidget(self.startup_upload_btn)
        btn_layout.addStretch()

        layout.addStretch()
        layout.addLayout(btn_layout)
        layout.addStretch()

        self.stacked_widget.addWidget(self.startup_widget)

    def init_main_screen(self):
        """
        Creates the main results screen featuring a top toolbar button, and a horizontally
        centered container holding the scrollable image area and the vertically centered statistics panel.
        """
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)

        self.top_bar_layout = QHBoxLayout()
        self.main_upload_btn = QPushButton("Upload Photo(s)")
        self.main_upload_btn.setFixedSize(200, 40)
        self.main_upload_btn.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.main_upload_btn.clicked.connect(self.upload_files)

        self.top_bar_layout.addWidget(self.main_upload_btn)
        self.top_bar_layout.addStretch()
        self.main_layout.addLayout(self.top_bar_layout)

        self.center_layout = QHBoxLayout()
        self.center_layout.addStretch()

        self.wrapper_container = QWidget()
        self.wrapper_layout = QHBoxLayout(self.wrapper_container)
        self.wrapper_layout.setContentsMargins(0, 0, 0, 0)
        self.wrapper_layout.setSpacing(20)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFixedWidth(650)
        self.scroll_content = QWidget()

        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(0)
        self.scroll_area.setWidget(self.scroll_content)

        self.wrapper_layout.addWidget(self.scroll_area)

        self.stats_container = QWidget()
        self.stats_layout = QVBoxLayout(self.stats_container)
        self.stats_layout.addStretch()

        self.stats_label = QLabel()
        self.stats_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.stats_label.setStyleSheet(
            "border: 2px solid #888; border-radius: 8px; font-size: 22px; font-weight: bold; padding: 30px;")

        self.stats_layout.addWidget(self.stats_label)
        self.stats_layout.addStretch()

        self.wrapper_layout.addWidget(self.stats_container)

        self.center_layout.addWidget(self.wrapper_container)
        self.center_layout.addStretch()

        self.main_layout.addLayout(self.center_layout)
        self.stacked_widget.addWidget(self.main_widget)

    def load_yaml_config(self):
        """
        Loads the class names from data.yaml, extracts the numeric value, and parses the currency text.
        Returns a dictionary mapping the original string name to its integer value.
        """
        parsed_values = {}

        try:
            with open("data.yaml", "r") as file:
                data = yaml.safe_load(file)

            if not isinstance(data, dict) or "names" not in data:
                QMessageBox.warning(self, "YAML Error", "The data.yaml file is missing the 'names' list.")
                return parsed_values

            names_list = data["names"]

            if not isinstance(names_list, list):
                QMessageBox.warning(self, "YAML Error", "The 'names' key in data.yaml is not a valid list.")
                return parsed_values

            currency_found = False
            for name in names_list:
                val_match = re.search(r'\d+', str(name))
                if val_match:
                    parsed_values[str(name)] = int(val_match.group())
                    if not currency_found:
                        curr_match = re.search(r'[a-zA-Z]+', str(name))
                        if curr_match:
                            self.currency = curr_match.group().upper()
                            currency_found = True
                else:
                    QMessageBox.information(self, "Parsing Warning",
                                            f"Could not extract a numeric value from the class name: {name}")

        except FileNotFoundError:
            QMessageBox.critical(self, "File Not Found", "Could not find data.yaml in the current directory.")
        except yaml.YAMLError as exc:
            QMessageBox.critical(self, "YAML Parsing Error",
                                 f"Failed to parse data.yaml. Ensure it is formatted correctly.\nDetails: {exc}")
        except Exception as exc:
            QMessageBox.critical(self, "Unexpected Error",
                                 f"An unexpected error occurred while loading data.yaml:\n{exc}")

        return parsed_values

    def upload_files(self):
        """
        Opens a file dialog allowing selection of multiple images, switches the UI state,
        clears previous data, and triggers batch processing.
        """
        if not self.coin_values:
            QMessageBox.warning(self, "Missing Configuration",
                                "Cannot process images without a valid data.yaml configuration.")
            return

        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", "Image Files (*.png *.jpg *.jpeg)")
        if not file_paths:
            return

        self.stacked_widget.setCurrentIndex(1)
        self.clear_scroll_area()
        self.process_images(file_paths)

    def clear_scroll_area(self):
        """
        Removes all existing image widgets and dynamic layout spacers from the scroll area layout.
        """
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.spacerItem():
                del item
        self.image_data_list.clear()

    def process_images(self, file_paths):
        """
        Iterates over uploaded files, runs YOLO prediction, calculates per-image statistics,
        and manages dynamic stretches to keep lists centered if they are small enough.
        """
        is_multiple = len(file_paths) > 1

        self.scroll_layout.addStretch()

        for file_path in file_paths:
            image = cv2.imread(file_path)
            if image is None:
                continue

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

            filename = os.path.basename(file_path)
            self.create_image_widget(annotated_image, filename, local_total_value, local_total_count, local_coin_counts,
                                     is_multiple)

        self.scroll_layout.addStretch()
        self.recalculate_totals()

    def create_image_widget(self, image, filename, local_value, local_count, local_counts, is_multiple):
        """
        Creates a container holding the aspect-ratio scaled image centered with its name below it.
        Overlays an unmodified checkbox in the top-right corner of the image boundaries.
        """
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, ch = image_rgb.shape
        bytes_per_line = ch * w
        q_img = QImage(image_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(10)

        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)

        left_side = QWidget()
        left_layout = QVBoxLayout(left_side)
        left_layout.setContentsMargins(0, 10, 0, 10)
        left_layout.setSpacing(5)

        image_label = QLabel()
        image_label.setAlignment(Qt.AlignCenter)

        max_width = 350
        max_height = 250
        scaled_pixmap = pixmap.scaled(max_width, max_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        image_label.setPixmap(scaled_pixmap)
        image_label.setFixedSize(scaled_pixmap.size())

        overlay_layout = QVBoxLayout(image_label)
        overlay_layout.setContentsMargins(5, 5, 5, 5)

        top_row_layout = QHBoxLayout()
        top_row_layout.addStretch()

        checkbox = QCheckBox()
        checkbox.setChecked(True)
        checkbox.stateChanged.connect(self.recalculate_totals)

        if not is_multiple:
            checkbox.hide()

        top_row_layout.addWidget(checkbox)

        overlay_layout.addLayout(top_row_layout)
        overlay_layout.addStretch()

        left_layout.addWidget(image_label, alignment=Qt.AlignCenter)

        name_label = QLabel(filename)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("font-size: 14px; font-weight: bold;")

        left_layout.addWidget(name_label)

        row_layout.addWidget(left_side, stretch=2 if is_multiple else 1)

        if is_multiple:
            right_side = QWidget()
            right_layout = QVBoxLayout(right_side)
            right_layout.setContentsMargins(0, 10, 10, 10)

            right_layout.addStretch()

            sorted_coins = sorted(local_counts.items(), key=lambda item: self.coin_values.get(item[0], 0), reverse=True)
            breakdown_lines = []
            for coin_name, count in sorted_coins:
                breakdown_lines.append(f"{coin_name} x{count}")
            breakdown_text = "\n".join(breakdown_lines) if breakdown_lines else "None"

            local_stats_text = f"Value: {local_value} {self.currency}\nCoins: {local_count}\n\nBreakdown:\n{breakdown_text}"
            local_stats_label = QLabel(local_stats_text)
            local_stats_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            local_stats_label.setStyleSheet("font-size: 16px; padding-left: 20px;")

            right_layout.addWidget(local_stats_label)
            right_layout.addStretch()

            row_layout.addWidget(right_side, stretch=1)

        container_layout.addLayout(row_layout)

        if is_multiple:
            separator = QFrame()
            separator.setFrameShape(QFrame.HLine)
            separator.setStyleSheet("color: #ccc;")
            container_layout.addWidget(separator)

        self.scroll_layout.addWidget(container)

        self.image_data_list.append({
            "checkbox": checkbox,
            "value": local_value,
            "count": local_count,
            "coin_counts": local_counts
        })

    def recalculate_totals(self):
        """
        Iterates through all tracked image data. Aggregates values and counts only for images
        whose checkboxes are currently checked (or hidden but logically checked), then triggers a display update.
        """
        global_total_value = 0
        global_total_count = 0
        global_coin_counts = defaultdict(int)

        for data in self.image_data_list:
            if data["checkbox"].isChecked():
                global_total_value += data["value"]
                global_total_count += data["count"]
                for coin_name, count in data["coin_counts"].items():
                    global_coin_counts[coin_name] += count

        self.update_stats_display(global_total_value, global_total_count, global_coin_counts)

    def update_stats_display(self, total_value, total_count, coin_counts):
        """
        Formats the accumulated statistics, sorts the dictionary by coin value in descending order,
        and updates the multi-line string on the bordered UI label.
        """
        sorted_coins = sorted(coin_counts.items(), key=lambda item: self.coin_values.get(item[0], 0), reverse=True)

        breakdown_lines = []
        for coin_name, count in sorted_coins:
            breakdown_lines.append(f"{coin_name} x{count}")

        breakdown_text = "\n".join(breakdown_lines) if breakdown_lines else "None"

        display_text = f"Total Value: {total_value} {self.currency}\nTotal Coins: {total_count}\n\nBreakdown:\n{breakdown_text}"
        self.stats_label.setText(display_text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CoinCounterApp()
    window.show()
    sys.exit(app.exec())