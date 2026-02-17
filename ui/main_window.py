import sys
import os
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt6.QtCore import Qt, QSize
from qfluentwidgets import (FluentWindow, NavigationItemPosition, SubtitleLabel, 
                            LineEdit, PrimaryPushButton, ProgressBar, InfoBar, 
                            InfoBarPosition, ComboBox, FluentIcon as FIF)

from core.downloader import DownloadWorker
from core.utils import get_default_download_path
from .setting_interface import SettingInterface

class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self.initWindow()
        
        # 메인 인터페이스 (홈)
        self.homeInterface = QWidget()
        self.homeInterface.setObjectName("homeInterface")
        self.initHomeInterface()
        
        # 설정 인터페이스
        self.settingInterface = SettingInterface(self)
        
        # 네비게이션 추가
        self.addSubInterface(self.homeInterface, FIF.HOME, '홈')
        self.addSubInterface(self.settingInterface, FIF.SETTING, '설정', NavigationItemPosition.BOTTOM)
        
        # 다운로드 워커
        self.worker = None

    def initWindow(self):
        self.setWindowTitle('Modern YouTube Downloader')
        self.resize(800, 600)
        self.setWindowIcon(FIF.VIDEO.icon())
        
        # 윈도우 중앙 배치 (선택사항)
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def initHomeInterface(self):
        layout = QVBoxLayout(self.homeInterface)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # 타이틀
        titleLabel = SubtitleLabel('YouTube 고화질 다운로더', self.homeInterface)
        layout.addWidget(titleLabel, alignment=Qt.AlignmentFlag.AlignTop)
        
        # URL 입력
        self.urlInput = LineEdit(self.homeInterface)
        self.urlInput.setPlaceholderText('YouTube URL을 입력하세요 (예: https://youtu.be/...)')
        self.urlInput.setClearButtonEnabled(True)
        layout.addWidget(self.urlInput)
        
        # 옵션 선택 (해상도/포맷)
        optionLayout = QHBoxLayout()
        self.formatCombo = ComboBox(self.homeInterface)
        self.formatCombo.addItems(['MP4 (Video + Audio)', 'MP3 (Audio Only)'])
        self.formatCombo.setCurrentIndex(0)
        optionLayout.addWidget(self.formatCombo)
        
        layout.addLayout(optionLayout)
        
        # 다운로드 버튼
        self.downloadBtn = PrimaryPushButton('다운로드 시작', self.homeInterface)
        self.downloadBtn.setIcon(FIF.DOWNLOAD)
        self.downloadBtn.clicked.connect(self.startDownload)
        layout.addWidget(self.downloadBtn)
        
        # 진행률 바
        self.progressBar = ProgressBar(self.homeInterface)
        self.progressBar.setValue(0)
        self.progressBar.hide()
        layout.addWidget(self.progressBar)
        
        # 상태 메시지
        self.statusLabel = SubtitleLabel('', self.homeInterface)
        self.statusLabel.hide()
        layout.addWidget(self.statusLabel)
        
        layout.addStretch(1)

    def startDownload(self):
        url = self.urlInput.text().strip()
        if not url:
            InfoBar.warning(
                title='경고',
                content='URL을 입력해주세요.',
                parent=self.homeInterface,
                position=InfoBarPosition.TOP_RIGHT
            )
            return
            
        # 설정값 가져오기
        save_path = self.settingInterface.download_path
        po_token = None  # TODO: 설정에서 가져오기
        
        format_type = 'mp4' if 'MP4' in self.formatCombo.currentText() else 'mp3'
        
        # UI 상태 업데이트
        self.downloadBtn.setEnabled(False)
        self.progressBar.setValue(0)
        self.progressBar.show()
        self.statusLabel.setText("준비 중...")
        self.statusLabel.show()
        
        # 워커 스레드 시작
        self.worker = DownloadWorker(url, save_path, format_type, po_token)
        self.worker.progress_signal.connect(self.updateProgress)
        self.worker.finished_signal.connect(self.downloadFinished)
        self.worker.start()

    def updateProgress(self, value, msg):
        self.progressBar.setValue(int(value))
        self.statusLabel.setText(msg)

    def downloadFinished(self, success, path, msg):
        self.downloadBtn.setEnabled(True)
        self.progressBar.hide()
        
        # 상태 메시지도 너무 길면 자르기
        status_msg = msg
        if not success and len(msg) > 80:
             status_msg = msg[:80] + "..."
        self.statusLabel.setText(status_msg)
        
        if success:
            InfoBar.success(
                title='성공',
                content=f'다운로드 완료: {os.path.basename(path)}',
                parent=self,
                position=InfoBarPosition.TOP_RIGHT,
                duration=5000
            )
        else:
            # 메시지가 너무 길면 잘라서 표시하고 로그 확인 유도
            display_msg = msg
            if len(msg) > 100:
                display_msg = msg[:100] + "... (자세한 내용은 error.log 확인)"
            
            InfoBar.error(
                title='실패',
                content=display_msg,
                parent=self,
                position=InfoBarPosition.TOP_RIGHT,
                duration=5000
            )
