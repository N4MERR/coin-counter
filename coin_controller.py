import os
from collections import defaultdict
from PySide6.QtCore import QThread, Signal
from coin_model import CoinModel
from coin_view import CoinView


class PredictionWorker(QThread):
    """
    Executes YOLO inference on a background thread and collects all results into a single batch.
    """
    batch_finished = Signal(list)

    def __init__(self, model_instance, file_paths):
        """
        Initializes the thread worker with the AI model instance and paths.
        """
        super().__init__()
        self.model_instance = model_instance
        self.file_paths = file_paths

    def run(self):
        """
        Iterates through files, runs inference, and emits all data simultaneously when finished.
        """
        is_multiple = len(self.file_paths) > 1
        batch_results = []

        for file_path in self.file_paths:
            annotated_image, local_value, local_count, local_counts = self.model_instance.process_image(file_path)

            if annotated_image is None:
                continue

            filename = os.path.basename(file_path)

            sorted_coins = sorted(local_counts.items(),
                                  key=lambda item: self.model_instance.coin_values.get(item[0], 0), reverse=True)
            breakdown_lines = [f"{coin_name} x{count}" for coin_name, count in sorted_coins]
            breakdown_text = "\n".join(breakdown_lines) if breakdown_lines else "None"
            local_stats_text = f"Value: {local_value} {self.model_instance.currency}\nCoins: {local_count}\n\nBreakdown:\n{breakdown_text}"

            batch_results.append({
                "image": annotated_image,
                "filename": filename,
                "stats_text": local_stats_text,
                "is_multiple": is_multiple,
                "counts": local_counts,
                "value": local_value,
                "count": local_count
            })

        self.batch_finished.emit(batch_results)


class CoinController:
    """
    Connects the CoinModel and CoinView, managing user interactions and batch threading.
    """

    def __init__(self, model: CoinModel, view: CoinView):
        """
        Initializes the controller with the model and view instances, and binds UI signals.
        """
        self.model = model
        self.view = view
        self.image_data_list = []
        self.worker = None

        self.view.startup_upload_btn.clicked.connect(self.handle_upload)
        self.view.main_upload_btn.clicked.connect(self.handle_upload)

        self.initialize_app()

    def initialize_app(self):
        """
        Triggers the loading of the AI model and configuration.
        """
        success, error_msg = self.model.load_model_and_config()
        if not success:
            self.view.show_error("Initialization Error", error_msg, fatal=True)

    def handle_upload(self):
        """
        Coordinates file selection, cleans the view, and initiates threading.
        """
        file_paths = self.view.open_file_dialog()
        if not file_paths:
            return

        self.view.clear_scroll_area()
        self.image_data_list.clear()
        self.view.show_loading(len(file_paths))

        self.start_processing(file_paths)

    def start_processing(self, file_paths):
        """
        Initializes and starts the background worker thread for batched inference.
        """
        self.worker = PredictionWorker(self.model, file_paths)
        self.worker.batch_finished.connect(self.handle_batch_finished)
        self.worker.start()

    def handle_batch_finished(self, batch_results):
        """
        Receives all processed data from the thread at once and builds the UI components.
        """
        self.view.switch_to_main_screen()
        self.view.add_stretch_to_scroll()

        for result in batch_results:
            checkbox = self.view.create_image_widget(
                result["image"],
                result["filename"],
                result["stats_text"],
                result["is_multiple"],
                self.recalculate_totals
            )

            self.image_data_list.append({
                "checkbox": checkbox,
                "value": result["value"],
                "count": result["count"],
                "coin_counts": result["counts"]
            })

        self.view.add_stretch_to_scroll()
        self.recalculate_totals()
        self.view.hide_loading()

    def recalculate_totals(self):
        """
        Aggregates data from active image widgets and updates the global statistics display.
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

        sorted_coins = sorted(global_coin_counts.items(), key=lambda item: self.model.coin_values.get(item[0], 0),
                              reverse=True)
        breakdown_lines = [f"{coin_name} x{count}" for coin_name, count in sorted_coins]
        breakdown_text = "\n".join(breakdown_lines) if breakdown_lines else "None"

        display_text = f"Total Value: {global_total_value} {self.model.currency}\nTotal Coins: {global_total_count}\n\nBreakdown:\n{breakdown_text}"
        self.view.update_stats_display(display_text)