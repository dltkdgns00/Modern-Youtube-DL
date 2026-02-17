import os
import shutil
import uuid
import logging
from typing import Optional, Callable
from PyQt6.QtCore import QThread, pyqtSignal, QObject

from pytubefix import YouTube
from pytubefix.cli import on_progress

from core.utils import sanitize_filename
from core.merger import merge_video_audio

class DownloadWorker(QThread):
    """
    백그라운드에서 영상을 다운로드하는 워커 스레드
    """
    progress_signal = pyqtSignal(float, str)  # 진행률(%), 상태 메시지
    finished_signal = pyqtSignal(bool, str, str)  # 성공 여부, 파일 경로, 메시지
    
    def __init__(self, url: str, save_path: str, format_type: str = 'mp4', 
                 po_token: str = None, visitor_data: str = None):
        super().__init__()
        self.url = url
        self.save_path = save_path
        self.format_type = format_type  # 'mp4' (video+audio) or 'mp3' (audio only)
        self.po_token = po_token
        self.visitor_data = visitor_data
        self.is_running = True

    def run(self):
        try:
            self.progress_signal.emit(0, "영상 정보 분석 중...")
            
            # YouTube 객체 생성 (po_token 적용)
            try:
                if self.po_token and self.visitor_data:
                    yt = YouTube(self.url, use_po_token=True, token_file=None)
                     # 내부적으로 po_token 설정이 필요한 경우 추가 로직 필요할 수 있음
                     # pytubefix 최신 버전 기준 use_po_token=True 사용
                else:
                    yt = YouTube(self.url)
            except Exception as e:
                self.finished_signal.emit(False, "", f"YouTube 객체 생성 실패: {str(e)}")
                return

            # 제목 및 파일명 설정
            try:
                title = yt.title
            except Exception as e:
                self.finished_signal.emit(False, "", f"영상 정보를 가져올 수 없습니다: {str(e)}")
                return
            
            safe_title = sanitize_filename(title)
            self.progress_signal.emit(10, f"다운로드 시작: {title}")

            # 콜백 연결 (진행률 표시용)
            # pytubefix의 on_progress_callback은 메인 스레드에서 UI 업데이트 시 충돌 가능성 있으므로 주의
            # 여기서는 직접 청크 단위 다운로드 또는 내부 콜백 활용
            yt.register_on_progress_callback(self._on_progress)

            if self.format_type == 'mp3':
                self._download_audio(yt, safe_title)
            else:
                self._download_video(yt, safe_title)

        except Exception as e:
            self.finished_signal.emit(False, "", f"오류 발생: {str(e)}")

    def _on_progress(self, stream, chunk, bytes_remaining):
        if not self.is_running:
            return
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = (bytes_downloaded / total_size) * 100
        # 10% ~ 90% 구간을 다운로드 진행률로 매핑
        adjusted_progress = 10 + (percentage * 0.8)
        self.progress_signal.emit(adjusted_progress, f"다운로드 중... {percentage:.1f}%")

    def _download_audio(self, yt: YouTube, title: str):
        """오디오만 다운로드 (mp3 변환)"""
        stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
        if not stream:
            self.finished_signal.emit(False, "", "다운로드 가능한 오디오 스트림이 없습니다.")
            return
            
        output_file = stream.download(output_path=self.save_path, filename=f"{title}.{stream.default_filename.split('.')[-1]}")
        
        # 확장자 변경 (실제 인코딩 변환은 아님, 필요시 moviepy로 변환)
        base, ext = os.path.splitext(output_file)
        new_file = base + '.mp3'
        
        # 기존 파일 있으면 삭제
        if os.path.exists(new_file):
            os.remove(new_file)
            
        os.rename(output_file, new_file)
        
        self.progress_signal.emit(100, "완료!")
        self.finished_signal.emit(True, new_file, "다운로드가 완료되었습니다.")

    def _download_video(self, yt: YouTube, title: str):
        """고화질 비디오 다운로드 및 병합"""
        # Adaptive Stream 검색 (1080p 이상)
        video_stream = None
        adaptive_streams = yt.streams.filter(adaptive=True, file_extension='mp4', only_video=True)
        
        # 해상도 높은 순으로 정렬
        sorted_streams = sorted(adaptive_streams, key=lambda s: int(s.resolution[:-1]) if s.resolution else 0, reverse=True)
        
        for stream in sorted_streams:
            if stream.resolution and int(stream.resolution[:-1]) >= 1080:
                video_stream = stream
                break
        
        # 1080p 이상 없으면 가장 좋은 화질 선택
        if not video_stream and sorted_streams:
            video_stream = sorted_streams[0]
            
        # 오디오 스트림
        audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
        
        if not video_stream or not audio_stream:
            self.finished_signal.emit(False, "", "적절한 비디오/오디오 스트림을 찾을 수 없습니다.")
            return

        self.progress_signal.emit(20, f"비디오 다운로드 ({video_stream.resolution})")
        
        # 임시 파일 경로 (UUID 사용하여 인코딩/길이 문제 방지)
        temp_stem = str(uuid.uuid4())
        temp_video_name = f"temp_v_{temp_stem}.mp4"
        temp_audio_name = f"temp_a_{temp_stem}.mp4"
        
        temp_video_path = os.path.join(self.save_path, temp_video_name)
        temp_audio_path = os.path.join(self.save_path, temp_audio_name)
        final_path = os.path.join(self.save_path, f"{title}.mp4")

        # 비디오 다운로드
        # output_path와 filename을 분리해서 전달해야 경로가 유지됨
        video_stream.download(output_path=self.save_path, filename=temp_video_name)
        
        self.progress_signal.emit(60, "오디오 다운로드")
        # 오디오 다운로드
        audio_stream.download(output_path=self.save_path, filename=temp_audio_name)
        
        self.progress_signal.emit(90, "병합 중...")
        
        try:
           success, err = merge_video_audio(temp_video_path, temp_audio_path, final_path)
           
           if success:
               # 임시 파일 삭제
               if os.path.exists(temp_video_path): os.remove(temp_video_path)
               if os.path.exists(temp_audio_path): os.remove(temp_audio_path)
               
               self.progress_signal.emit(100, "완료!")
               self.finished_signal.emit(True, final_path, "다운로드 및 병합 완료!")
           else:
               logging.error(f"Merge failed: {err}")
               self.finished_signal.emit(False, "", f"병합 실패: {err}")
               
        except ImportError:
            logging.error("Merge module not found")
            self.finished_signal.emit(False, "", "병합 모듈을 찾을 수 없습니다.")
        except Exception as e:
            logging.error(f"Error during merge: {e}", exc_info=True)
            self.finished_signal.emit(False, "", f"병합 중 오류: {str(e)}")

    def stop(self):
        self.is_running = False
        self.wait()
