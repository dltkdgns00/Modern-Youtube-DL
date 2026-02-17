import os
import subprocess
import imageio_ffmpeg
from moviepy.editor import VideoFileClip, AudioFileClip

def merge_video_audio(video_path: str, audio_path: str, output_path: str) -> tuple[bool, str]:
    """
    비디오와 오디오 파일을 병합합니다.
    imageio-ffmpeg을 통해 확보된 FFmpeg 바이너리를 우선 사용합니다.
    """
    
    # 1. FFmpeg 바이너리 경로 확보
    try:
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        ffmpeg_exe = 'ffmpeg' # 시스템 PATH 시도

    # FFmpeg 명령어 구성
    ffmpeg_cmd = [
        ffmpeg_exe, '-y',
        '-i', video_path,
        '-i', audio_path,
        '-c:v', 'copy',
        '-c:a', 'aac',
        output_path
    ]
    
    try:
        # 윈도우에서 콘솔 창 숨기기
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
        subprocess.run(ffmpeg_cmd, check=True, capture_output=True, startupinfo=startupinfo)
        return True, "FFmpeg 병합 성공"
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"FFmpeg 병합 실패: {e}")
        # 실패 시 MoviePy 시도 (이미지오 의존성이 있긴 하나, 직접 subprocess가 실패했을 경우 대비)

    # 2. MoviePy 시도
    try:
        video_clip = VideoFileClip(video_path)
        audio_clip = AudioFileClip(audio_path)
        final_clip = video_clip.set_audio(audio_clip)
        
        final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", verbose=False, logger=None)
        
        video_clip.close()
        audio_clip.close()
        final_clip.close()
        return True, "MoviePy 병합 성공"
    except Exception as e:
        return False, f"병합 실패: {str(e)}"
