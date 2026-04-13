import sys
from PySide6.QtWidgets import QApplication

from coin_controller import CoinController
from coin_model import CoinModel
from coin_view import CoinView

if __name__ == "__main__":
    app = QApplication(sys.argv)

    model = CoinModel()
    view = CoinView()
    controller = CoinController(model, view)

    view.show()
    sys.exit(app.exec())