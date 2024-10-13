from PyQt5.QtCore import QObject, QEvent, pyqtSignal
from os import environ

# 윈도우 HiDPI 고정 설정
def suppress_qt_warnings():
    environ["QT_DEVICE_PIXEL_RATIO"] = "0"
    environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    environ["QT_SCREEN_SCALE_FACTORS"] = "1"
    environ["QT_SCALE_FACTOR"] = "1"

def click(widget): # 어떤 것이던 클릭하면 들어가는 것
    class Filter(QObject):
        clicked = pyqtSignal()

        def eventFilter(self, object, event):
            if object == widget and event.type() == QEvent.MouseButtonPress:
                self.clicked.emit()
                return True # 클릭이 이루어지면 True
            return False # 이루어지지 않으면 False
        
    filter = Filter(widget)
    widget.installEventFilter(filter)
    return filter.clicked