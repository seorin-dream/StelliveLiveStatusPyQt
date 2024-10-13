# Stellive Live Status Manager with PyQt5

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from utility import *
import requests
import json
import webbrowser

class StelliveLiveStatus(QMainWindow):

    def __init__(self):
        super().__init__()
        self.loadVTuber()
        self.initUI()
        self.autoRefreshSet()

    # 30초마다 자동 갱신
    def autoRefreshSet(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(lambda: self.updateAllVTuberStatus())
        self.timer.start(30000)  # 30000ms == 30s

    # 모든 VTuber 아이템을 받아다가 업데이트 돌려야 되니까 만듬.
    def updateAllVTuberStatus(self):
        for name, vtuber_info in self.vtubers.items():
            self.update_status(name)

    def loadVTuber(self): # VTuber JSON 파일 로딩
        with open('vtubers.json', 'r', encoding='utf-8') as file:
            self.vtubers = json.load(file)

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
        self.resize(760, 630) # 창 크기를 지정
        self.show() # 창을 보여줌

        # Image batch
        self.imageWidget = QWidget(self)
        self.setCentralWidget(self.imageWidget)

        # VTuber Font Set and Background Color
        font_id = QFontDatabase.addApplicationFont('font/KartGothicBold.ttf') # 경로 상대 경로로 해야
        font_family = QFontDatabase.applicationFontFamilies(font_id)
        self.VTuberNameFont = QFont(font_family[0], 25) # 왜 [0] 해야하는지 모르겠지만 이렇게 해야 작동함.
        self.setStyleSheet("background-color: white;")

        # CHZZK Site
        self.headers = { # 치지직이 뱉기 때문에 헤더에 UA 넣어서 보내야함
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        }
        self.chzzk_url = 'https://api.chzzk.naver.com/service/v1/channels/{channelID}'
        self.chzzk_live_url = 'https://chzzk.naver.com/live/{channelID}'
        self.chzzk_station_url = "https://chzzk.naver.com/{channelID}"

        # STELLIVE Logo
        self.stelliveHeadLogo = QLabel(self.imageWidget)
        self.stelliveHeadLogo.setPixmap(QPixmap('stellive_image/logo.png'))
        self.stelliveHeadLogo.move(10, 10)
        # click(self.stelliveHeadLogo).connect(lambda: self.refreshNow('headclicked'))
        # 클릭할 때 사용할 함수 볼려고 그냥 둠

        # VTuber 배치 좌표 변수
        x_offset = 10  # x 좌표의 시작 위치
        y_offset = self.stelliveHeadLogo.pixmap().height() + 10  # y 좌표의 시작 위치
        row_spacing = 105  # 세로 간격
        column_spacing = 380  # 가로 간격

        index = 0  # VTuber 인덱스를 위한 변수
        for name, vtuber_info in self.vtubers.items():
            col = index % 2  # 열 위치(좌우 배치)
            row = index // 2  # 행 위치(위아래 배치)

            # 좌표 설정
            x = x_offset + col * column_spacing
            y = y_offset + row * row_spacing

            # VTuber 이미지
            original_vtuber_image = QPixmap(vtuber_info['image'])
            resized_vtuber_image = original_vtuber_image.scaled(100, 100)
            vtuber_image_label = QLabel(self.imageWidget)
            vtuber_image_label.setPixmap(resized_vtuber_image)
            vtuber_image_label.move(x, y)

            # VTuber 이름
            vtuber_name_label = QLabel(vtuber_info['name'], self.imageWidget)
            vtuber_name_label.move(x + resized_vtuber_image.width() + 10, y)
            vtuber_name_label.setFont(self.VTuberNameFont)
            vtuber_name_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            vtuber_name_label.adjustSize()

            # VTuber 상태
            vtuber_status_label = QLabel(self.imageWidget)
            if self.update_status(name):  # 방송 중이면
                vtuber_name_label.setStyleSheet("color: #404040;")  # 글자 색상을 그레이로 바꿈
                vtuber_status_label.setPixmap(QPixmap('stellive_image/online.png'))
                click(vtuber_status_label).connect(lambda name=name: self.openBroadcastNow(name))
            else:  # 방송 중이 아니면
                vtuber_name_label.setStyleSheet("color: #a5a5a3;")  # 글자 색상을 짙은 회색으로 바꿈
                vtuber_status_label.setPixmap(QPixmap('stellive_image/offline.png'))
                click(vtuber_status_label).connect(lambda name=name: self.openStationNow(name))
            
            # 상태 라벨의 상대 위치
            vtuber_status_label.move(x + resized_vtuber_image.width() + 10, y + 50)

            # 인덱스 증가
            index += 1
                
    def update_status(self, name):
        vtuber = self.vtubers[name]
        url = self.chzzk_url.format(channelID=vtuber['channel_id'])
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:  # 성공적으로 수신했을 때
            data = response.json() # HTML 말고 JSON으로 해야함
            open_live_status = data['content']['openLive']
            if open_live_status:
                return True # 채널 ID 반환하려면
            else:
                return False # 빈 값도 같이 반환해야함
    
    def openBroadcastNow(self, name): # 방송이 켜져있을 때 방송으로 바로 이동
        vtuber = self.vtubers[name]
        webbrowser.open(self.chzzk_live_url.format(channelID=vtuber['channel_id']))

    def openStationNow(self, name): # 방송이 꺼져있을 때 방송국으로 이동
        vtuber = self.vtubers[name]
        webbrowser.open(self.chzzk_station_url.format(channelID=vtuber['channel_id']))

if __name__ == '__main__':
    suppress_qt_warnings()
    app = QApplication(sys.argv) # PyQt5는 어플리케이션 객체를 생성해야 함.
    StatusWindow = StelliveLiveStatus()
    StatusWindow.show()
    sys.exit(app.exec_())