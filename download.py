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
    initial_format = 'webm' if output_format in ['mkv', 'mov'] else output_format
    ydl_opts = {
        'format': f"{format_id}+bestaudio",
        'outtmpl': os.path.join(output_path, f'{output_filename}.%(ext)s'),
        'progress_hooks': [progress_callback] if progress_callback else [],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Convert to the desired format if necessary
    if output_format in ['mkv', 'mov']:
        convert_to_format(output_path, output_filename, output_format, use_cuda)

def convert_to_format(output_path, output_filename, output_format, use_cuda):
    input_file = os.path.join(output_path, f'{output_filename}.webm')
    output_file = os.path.join(output_path, f'{output_filename}.{output_format}')

    if use_cuda:
        ffmpeg_command = f"ffmpeg -i {input_file} -c:v h264_nvenc -c:a aac {output_file}"
    else:
        ffmpeg_command = f"ffmpeg -i {input_file} {output_file}"

    os.system(ffmpeg_command)
    os.remove(input_file)  # Remove the intermediate .webm file

def delete_webm_file(output_path, output_filename):
    webm_file = os.path.join(output_path, f'{output_filename}.webm')
    if os.path.exists(webm_file):
        os.remove(webm_file)
        return True
    return False
