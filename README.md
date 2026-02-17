# Modern YouTube Downloader (TubeFlow)

![Python](https://img.shields.io/badge/Python-3.12-blue)
![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green)
![Fluent Design](https://img.shields.io/badge/Design-Fluent--Widgets-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

깔끔하고 현대적인 디자인의 YouTube 고화질 영상/음원 다운로더입니다.
복잡한 설치 없이 **실행 파일(EXE) 하나로 간편하게 사용**할 수 있습니다.

## ✨ 주요 기능

- **모던한 UI**: Windows 11 스타일의 Fluent Design 적용
- **고화질 지원**: 1080p 이상의 고해상도 영상 다운로드 가능 (자동 병합)
- **음원 추출**: MP3 (Audio Only) 변환 지원
- **단일 실행 파일**: Python이나 FFmpeg 설치가 필요 없는 Standalone EXE 제공
- **안전한 처리**: 한글/특수문자 파일명 완벽 지원 (UUID 임시 파일 처리)

## 📥 설치 및 실행

### 일반 사용자 (Windows)

1. 우측 [Releases](https://github.com/dltkdgns00/Modern-Youtube-DL/releases) 페이지에서 최신 버전의 `ModernYoutubeDL.exe`를 다운로드합니다.
2. 다운로드 받은 파일을 실행합니다. (별도의 설치 과정 없음)
   - _팁: 백신 프로그램이 경고를 띄울 경우 '추가 정보' -> '실행'을 눌러주세요._

### 개발자 (직접 빌드)

이 프로젝트를 직접 수정하거나 빌드하고 싶다면 아래 단계를 따르세요.

```bash
# 레포지토리 클론
git clone https://github.com/dltkdgns00/Modern-Youtube-DL.git
cd Modern-Youtube-DL

# 가상환경 생성 및 활성화
python -m venv .venv
.venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
pip install pyinstaller

# 실행
python main.py

# EXE 빌드
pyinstaller build.spec
```

## 🛠 기술 스택

- **Language**: Python 3.12
- **GUI Framework**: PyQt6, PyQt-Fluent-Widgets
- **Core Logic**: pytubefix (YouTube API), moviepy/imageio-ffmpeg (Media Processing)
- **Build Tool**: PyInstaller

## ⚠️ 주의사항

- 이 프로그램은 개인적인 학습 및 테스트 목적으로 제작되었습니다.
- 다운로드한 콘텐츠의 저작권 책임은 사용자 본인에게 있습니다.
- 유튜브의 정책 변화로 인해 다운로드가 일시적으로 제한될 수 있습니다.

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.
