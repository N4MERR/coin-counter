from PySide6.QtWidgets import QMainWindow, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QWidget, \
    QStackedWidget, QScrollArea, QCheckBox, QFrame, QMessageBox, QFileDialog, QProgressDialog
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt
import cv2


class CoinView(QMainWindow):
    """
    Manages the visual layout, user interface components, and state transitions.
    """

    def __init__(self):
        """
        Initializes the main window and sets up the stacked widget.
        """
        super().__init__()
        self.setWindowTitle("Coin Value Predictor")
        self.setGeometry(100, 100, 1200, 800)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.init_startup_screen()
        self.init_main_screen()

        self.stacked_widget.setCurrentIndex(0)

    def init_startup_screen(self):
        """
        Creates the initial screen featuring the upload button.
        """
        self.startup_widget = QWidget()
        layout = QVBoxLayout(self.startup_widget)

        btn_layout = QHBoxLayout()
        self.startup_upload_btn = QPushButton("Upload Photo(s)")
        self.startup_upload_btn.setFixedSize(300, 80)
        self.startup_upload_btn.setStyleSheet("font-size: 22px; font-weight: bold;")

        btn_layout.addStretch()
        btn_layout.addWidget(self.startup_upload_btn)
        btn_layout.addStretch()

        layout.addStretch()
        layout.addLayout(btn_layout)
        layout.addStretch()

        self.stacked_widget.addWidget(self.startup_widget)

    def init_main_screen(self):
        """
        Creates the main results screen containing the scroll area and statistics panel.
        """
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)

        self.top_bar_layout = QHBoxLayout()
        self.main_upload_btn = QPushButton("Upload Photo(s)")
        self.main_upload_btn.setFixedSize(200, 40)
        self.main_upload_btn.setStyleSheet("font-size: 16px; font-weight: bold;")

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

    def show_error(self, title, message, fatal=False):
        """
        Displays a critical error message box.
        """
        QMessageBox.critical(self, title, message)
        if fatal:
            import sys
            sys.exit(1)

    def open_file_dialog(self):
        """
        Opens a file dialog for image selection.
        Returns a list of file paths.
        """
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", "Image Files (*.png *.jpg *.jpeg)")
        return file_paths

    def switch_to_main_screen(self):
        """
        Changes the active view to the main results screen.
        """
        self.stacked_widget.setCurrentIndex(1)

    def clear_scroll_area(self):
        """
        Removes all existing image widgets from the scroll area layout.
        """
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.spacerItem():
                del item

    def add_stretch_to_scroll(self):
        """
        Adds a spacer element to the scroll layout.
        """
        self.scroll_layout.addStretch()

    def show_loading(self, file_count):
        """
        Displays an unmissable modal progress dialog to indicate background processing.
        """
        self.progress_dialog = QProgressDialog(f"Processing {file_count} image(s)...", None, 0, 0, self)
        self.progress_dialog.setWindowTitle("Analyzing")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setCancelButton(None)
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.show()

    def hide_loading(self):
        """
        Closes the modal progress dialog if it exists.
        """
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()

    def create_image_widget(self, image, filename, local_stats_text, is_multiple, toggle_callback):
        """
        Creates a container holding the scaled image and its corresponding statistics.
        Returns the QCheckBox instance for external state tracking.
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
        checkbox.stateChanged.connect(toggle_callback)

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

        return checkbox

    def update_stats_display(self, text):
        """
        Updates the main statistics panel with the provided text.
        """
        self.stats_label.setText(text)