import os
import wave
import shutil
import yt_dlp
import subprocess

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def get_ffmpeg():

    ffmpeg = shutil.which("ffmpeg")

    if ffmpeg:
        return ffmpeg

    possible = [
        "/usr/bin/ffmpeg",
        "/usr/local/bin/ffmpeg",
    ]

    for path in possible:
        if os.path.exists(path):
            return path

    raise RuntimeError(
        "FFmpeg is not installed. Add packages.txt containing only:\nffmpeg"
    )


def download_youtube_audio(url: str) -> str:

    output_path = os.path.join(
        DOWNLOAD_DIR,
        "%(title)s.%(ext)s",
    )

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "quiet": True,
        "noplaylist": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(url, download=True)

        filename = (
            ydl.prepare_filename(info)
            .replace(".webm", ".wav")
            .replace(".m4a", ".wav")
            .replace(".mp4", ".wav")
        )

    return filename


def convert_to_wav(input_path: str):

    ffmpeg = get_ffmpeg()

    output_path = (
        os.path.splitext(input_path)[0]
        + "_converted.wav"
    )

    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-i",
            input_path,
            "-ac",
            "1",
            "-ar",
            "16000",
            output_path,
        ],
        check=True,
    )

    return output_path


def chunk_audio(wav_path, chunk_minutes=10):

    chunk_paths = []

    with wave.open(wav_path, "rb") as wf:

        params = wf.getparams()

        frame_rate = wf.getframerate()

        chunk_frames = chunk_minutes * 60 * frame_rate

        index = 0

        while True:

            frames = wf.readframes(chunk_frames)

            if not frames:
                break

            chunk_path = f"{wav_path}_chunk_{index}.wav"

            with wave.open(chunk_path, "wb") as out:
                out.setparams(params)
                out.writeframes(frames)

            chunk_paths.append(chunk_path)

            index += 1

    return chunk_paths


def process_input(source):

    if source.startswith(("http://", "https://")):

        print("Downloading YouTube audio...")

        wav_path = download_youtube_audio(source)

    else:

        print("Converting local video...")

        wav_path = convert_to_wav(source)

    print("Chunking audio...")

    chunks = chunk_audio(wav_path)

    return chunks
