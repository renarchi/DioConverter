import yt_dlp
import os
import logging

def get_available_formats(url):
    ydl_opts = {
        'listformats': True,
    }
    formats = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
    except Exception as e:
        logging.error(f"Error retrieving formats: {e}")
        print(f"Error retrieving formats: {e}")
    return formats

def download_video(url, format_id, output_path, output_filename='video', output_format='mp4', use_cuda=False, progress_callback=None):
    ydl_opts = {
        'format': f"{format_id}+bestaudio",
        'outtmpl': os.path.join(output_path, f'{output_filename}.%(ext)s'),
        'progress_hooks': [progress_callback] if progress_callback else [],
    }

    if output_format in ['mkv', 'mov']:
        ydl_opts['merge_output_format'] = 'webm'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': output_format,
        }]

    # Add CUDA support
    if use_cuda:
        ydl_opts['postprocessors'] = ydl_opts.get('postprocessors', []) + [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': output_format,
            'postprocessor_args': ['-c:v', 'h264_nvenc']
        }]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def delete_webm_file(output_path, output_filename):
    webm_file = os.path.join(output_path, f'{output_filename}.webm')
    if os.path.exists(webm_file):
        os.remove(webm_file)
        return True
    return False
