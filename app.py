import sys
from PySide6.QtCore import Qt, QDir, QUrl
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem
from PySide6.QtMultimedia import QMediaFormat
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from pathlib import Path

_placeholder = "Placeholder Text"

def nameFilters():
    """Create a tuple of name filters/preferred index for populating the
       open file dialog."""
    result = []
    preferredFilter = ""
    formats = QMediaFormat().supportedFileFormats(QMediaFormat.Decode)
    for m, format in enumerate(formats):
        mediaFormat = QMediaFormat(format)
        mimeType = mediaFormat.mimeType()
        if mimeType.isValid():
            filter = QMediaFormat.fileFormatDescription(format) + " ("
            for i, suffix in enumerate(mimeType.suffixes()):
                if i:
                    filter += ' '
                filter += "*." + suffix
            filter += ')'
            result.append(filter)
            if mimeType.name() == "video/mp4":
                preferredFilter = filter
    result.sort()
    preferred = result.index(preferredFilter) if preferredFilter else 0
    return (result, preferred)

class CubeWidget(QWidget):
    def __init__(self, parent=None):
        super(CubeWidget, self).__init__(parent)
        self.setMinimumSize(20, 20)  # Set the minimum size of the cube widget
        self.setStyleSheet("background-color: white;")  # Set the background color to white

class Widget(QWidget):
    def __init__(self, parent=None):
        super(Widget, self).__init__(parent)

        menu_widget = QListWidget()
       
        item = QListWidgetItem(f"Le nombre des personnes: ")
        item.setTextAlignment(Qt.AlignCenter)
        menu_widget.addItem(item)

        item = QListWidgetItem(f"Distance avec le plus proche: ")
        item.setTextAlignment(Qt.AlignCenter)
        menu_widget.addItem(item)

        item = QListWidgetItem(f"Distance avec le plus loin: ")
        item.setTextAlignment(Qt.AlignCenter)
        menu_widget.addItem(item)

        item = QListWidgetItem(f"Personne en  cas d'urgence: ")
        item.setTextAlignment(Qt.AlignCenter)
        menu_widget.addItem(item)

        video_widget = QVideoWidget()

        button = QPushButton("Mode Nuit")
        button.clicked.connect(self.open_video)

        main_layout = QVBoxLayout()

        content_layout = QVBoxLayout()
        content_layout.addWidget(video_widget)

        button_layout = QHBoxLayout()
        button_layout.addWidget(button)
        content_layout.addLayout(button_layout)

        main_widget = QWidget()
        main_widget.setLayout(content_layout)

        layout = QHBoxLayout()
        layout.addWidget(menu_widget, 1)
        layout.addWidget(main_widget, 4)

        main_layout.addLayout(layout)

        self.setLayout(main_layout)

        self.engine = QQmlApplicationEngine()
        app_dir = Path(__file__).parent
        app_dir_url = QUrl.fromLocalFile(str(app_dir))
        self.engine.addImportPath(str(app_dir))
        nameFilterList, selectedNameFilter = nameFilters()
        self.engine.setInitialProperties({
            "source": QUrl(),
            "nameFilters": nameFilterList,
            "selectedNameFilter": selectedNameFilter})
        self.engine.loadFromModule("MediaPlayer", "Main")

    def open_video(self):
        self.engine.rootObjects()[0].setProperty("source", QUrl.fromLocalFile("people-walking.mp4")) # Replace with the path to your video file

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Widget()
    window.show()

    with open("style.qss", "r") as f:
        _style = f.read()
        app.setStyleSheet(_style)

    sys.exit(app.exec_())
