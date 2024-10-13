# Stellive Live Status Manager with PyQt5

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from os import environ
import requests
import webbrowser

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

class StelliveLiveStatus(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        # Window Main Setting
        self.setWindowTitle('STELLIVE Live Status') # Title의 제목을 설정
        self.setWindowIcon(QIcon('stellive_image/icon.png')) # 아이콘의 경로를 지정.

        # Status Bar
        self.statusBar = QStatusBar(self)
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")

        # Window size
        self.move(300, 300) # 스크린의 어디로 이동
        self.resize(960, 540) # 창 크기를 지정
        self.show() # 창을 보여줌

        # Image batch
        self.imageWidget = QWidget(self)
        self.setCentralWidget(self.imageWidget)

        # VTuber Font Set
        self.VTuberNameFont = QFont('경기천년제목 Medium', 25)

        # CHZZK Site
        self.headers = { # 치지직이 뱉기 때문에 헤더에 UA 넣어서 보내야함
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        }
        self.chzzk_url = 'https://api.chzzk.naver.com/service/v1/channels/{channelID}'
        self.chzzk_live_url = 'https://chzzk.naver.com/live/{channelID}'
        self.chzzk_station_url = "https://chzzk.naver.com/{channelID}"

        self.chzzk_ch_ids = { # 치지직 채널 ID
            'kanna'   : 'f722959d1b8e651bd56209b343932c01',  # 칸나
            'uni'     : '45e71a76e949e16a34764deb962f9d9f',  # 유니
            'hina'    : 'b044e3a3b9259246bc92e863e7d3f3b8',  # 히나
            'mashiro' : '4515b179f86b67b4981e16190817c580',  # 마시로
            'rize'    : '4325b1d5bbc321fad3042306646e2e50',  # 리제
            'tabi'    : 'a6c4ddb09cdb160478996007bff35296',  # 타비
            'shibuki' : '64d76089fba26b180d9c9e48a32600d9',  # 시부키
            'rin'     : '516937b5f85cbf2249ce31b0ad046b0f',  # 린
            'nana'    : '4d812b586ff63f8a2946e64fa860bbf5',  # 나나
            'riko'    : '8fd39bb8de623317de90654718638b10'   # 리코
        }

        # STELLIVE Logo
        self.stelliveHeadLogo = QLabel(self.imageWidget)
        self.stelliveHeadLogo.setPixmap(QPixmap('stellive_image/logo.png'))
        self.stelliveHeadLogo.move(10, 10)
        click(self.stelliveHeadLogo).connect(lambda: self.refreshNow('headclicked'))
            # Click시 호출할 함수 넘길때 이렇게 해야함

        # STELLIVE VTuber
        #self.stelliveListOne = QLabel(self.imageWidget)
        #self.stelliveListOne.setPixmap(QPixmap('stellive_image/1_Kanna.png'))

        self.original_stelliveListOne = QPixmap('stellive_image/1_Kanna.png')
        self.resized_stalliveListOne = self.original_stelliveListOne.scaled(100, 100)
        self.stelliveListOne = QLabel(self.imageWidget)
        self.stelliveListOne.setPixmap(self.resized_stalliveListOne)
        self.stelliveListOne.move(10, self.stelliveHeadLogo.pixmap().height()+10) # 상대 위치로 하는게 안전할듯?

        self.stelliveNameOne = QLabel('아이리 칸나', self.imageWidget) # 칸으로 쓸 때 imageWidget (QWidget) 잊지말기
        self.stelliveNameOne.move(10+self.stelliveListOne.pixmap().width()+10, self.stelliveHeadLogo.pixmap().height()+10)
        self.stelliveNameOne.setFont(self.VTuberNameFont)
        self.stelliveNameOne.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.stelliveNameOne.adjustSize()

        self.stelliveStatusOne = QLabel('방송 중 아님!', self.imageWidget) # 칸으로 쓸 때 imageWidget (QWidget) 잊지말기
        self.stelliveStatusOne.move(10+self.stelliveListOne.pixmap().width()+10, 180)
        self.stelliveStatusOne.setFont(self.VTuberNameFont)
        self.stelliveStatusOne.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.stelliveStatusOne.adjustSize()

        if self.update_status('kanna') == True: 
            self.stelliveNameOne.setStyleSheet("color: black;")  # 글자 색상을 그레이로 바꿈
            self.stelliveStatusOne.setText('지금 방송 중!')
            self.stelliveStatusOne.setStyleSheet("color: black;")  # 글자 색상을 그레이로 바꿈
            click(self.stelliveStatusOne).connect(lambda: self.openBroadcastNow('kanna'))

        else:
            self.stelliveNameOne.setStyleSheet("color: grey;")  # 글자 색상을 그레이로 바꿈
            self.stelliveStatusOne.setText('방송 중 아님!')
            self.stelliveStatusOne.setStyleSheet("color: grey;")  # 글자 색상을 그레이로 바꿈
            click(self.stelliveStatusOne).connect(lambda: self.openStationNow('kanna'))
            

        click(self.stelliveListOne).connect(lambda: self.refreshNow('kannaClicked'))
    
    def update_status(self, name):
        if name in self.chzzk_ch_ids: # 들어온 이름이 리스트 이름과 같으면 실행
            print(self.chzzk_ch_ids[name])
            url = self.chzzk_url.format(channelID=self.chzzk_ch_ids[name])
            print(url)
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:  # 성공적으로 수신했을 때
                data = response.json() # HTML 말고 JSON으로 해야함
                open_live_status = data['content']['openLive']
                if open_live_status:
                    return True # 채널 ID 반환하려면
                else:
                    return False # 빈 값도 같이 반환해야함
        
        #return False, None # 아무것도 없을 때
        
    def refreshNow(self, switch):
        if switch == 'headclicked':
            print("클릭하면 일단 켜지게 해둠.")
            self.statusBar.showMessage("Refreshing...")
        elif switch == 'kannaClicked':
            print("칸나 머리 누름")
        self.statusBar.showMessage("Ready")
        return
    
    def openBroadcastNow(self, switch): # 방송이 켜져있을 때 방송으로 바로 이동
        if switch in self.chzzk_ch_ids:
            webbrowser.open(self.chzzk_live_url.format(channelID=self.chzzk_ch_ids[switch]))
        return

    def openStationNow(self, switch): # 방송이 꺼져있을 때 방송국으로 이동
        print(switch)
        if switch in self.chzzk_ch_ids:
            webbrowser.open(self.chzzk_station_url.format(channelID=self.chzzk_ch_ids[switch]))
            print(self.chzzk_station_url.format(channelID=self.chzzk_ch_ids[switch]))
        return

if __name__ == '__main__':
    suppress_qt_warnings()
    app = QApplication(sys.argv) # PyQt5는 어플리케이션 객체를 생성해야 함.
    StatusWindow = StelliveLiveStatus()
    StatusWindow.show()
    sys.exit(app.exec_())