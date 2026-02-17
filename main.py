import sys
import os
import logging
from PyQt6.QtWidgets import QApplication

# 고해상도 지원 (High DPI)
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
os.environ["QT_API"] = "pyqt6"

# 로깅 설정
def setup_logging():
    log_file = os.path.join(os.getcwd(), 'error.log')
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    sys.excepthook = handle_exception

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

def main():
    setup_logging()
    logging.info("Application started")
    app = QApplication(sys.argv)
    
    from ui.main_window import MainWindow
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
