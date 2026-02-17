from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFileDialog
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from qfluentwidgets import (SettingCardGroup, SwitchSettingCard, FolderListSettingCard,
                            OptionsSettingCard, PrimaryPushSettingCard, ScrollArea,
                            ExpandLayout, Theme, setTheme, PushSettingCard)
from qfluentwidgets import FluentIcon as FIF
from core.utils import get_default_download_path

class MockConfigItem(QObject):
    valueChanged = pyqtSignal(object)
    def __init__(self, name, default):
        super().__init__()
        self.name = name
        self._value = default
        self.options = ["Light", "Dark", "Auto"]
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, v):
        self._value = v
        self.valueChanged.emit(v)

class SettingInterface(ScrollArea):
    """설정 화면 인터페이스"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settingInterface")
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)
        
        self.settingLabel = None
        
        # 설정 변수들 (나중에 설정 파일로 저장/로드 구현 필요)
        self.download_path = get_default_download_path()
        self.themeItem = MockConfigItem("Theme", "Auto") # Mock item
        
        self.__initWidget()
        self.__initLayout()
    
    def __initWidget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 0, 0, 0)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        
        # === 다운로드 설정 그룹 ===
        self.downloadGroup = SettingCardGroup("다운로드", self.scrollWidget)
        
        self.downloadPathCard = PushSettingCard(
            "폴더 선택",
            FIF.FOLDER,
            "저장 위치",
            self.download_path,
            self.downloadGroup
        )
        self.downloadPathCard.clicked.connect(self.__onDownloadPathClicked)
        
        # === 유튜브 설정 그룹 ===
        self.youtubeGroup = SettingCardGroup("YouTube 설정", self.scrollWidget)
        
        self.poTokenCard = PushSettingCard(
            "입력",
            FIF.EDIT,
            "PO Token 설정",
            "봇 탐지 우회를 위한 토큰 설정 (준비 중)",
            self.youtubeGroup
        )
        # TODO: PO Token 입력 다이얼로그 연동
        
        # === 앱 설정 그룹 ===
        self.appGroup = SettingCardGroup("앱 설정", self.scrollWidget)
        
        self.themeCard = OptionsSettingCard(
            self.themeItem,
            FIF.BRUSH,
            "테마",
            "애플리케이션 테마 변경",
            texts=["Light", "Dark", "Auto"],
            parent=self.appGroup
        )
        
    def __initLayout(self):
        self.settingLabel = None  # 타이틀 라벨 등 필요시 추가
        
        self.downloadGroup.addSettingCard(self.downloadPathCard)
        self.youtubeGroup.addSettingCard(self.poTokenCard)
        self.appGroup.addSettingCard(self.themeCard)
        
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(60, 10, 60, 0)
        self.expandLayout.addWidget(self.downloadGroup)
        self.expandLayout.addWidget(self.youtubeGroup)
        self.expandLayout.addWidget(self.appGroup)
        
    def __onDownloadPathClicked(self):
        path = QFileDialog.getExistingDirectory(self, "다운로드 경로 선택", self.download_path)
        if path:
            self.download_path = path
            self.downloadPathCard.setContent(path)

