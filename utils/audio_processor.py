```python
import os
import wave
import shutil
import subprocess
import yt_dlp
import streamlit as st


# ============================================================
# Configuration
# ============================================================

DOWNLOAD_DIR = "downloads"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# ============================================================
# Find FFmpeg
# ============================================================

def get_ffmpeg():

    # First try PATH
    ffmpeg = shutil.which("ffmpeg")

    if ffmpeg:
        return ffmpeg

    # Common Linux locations
    possible_paths = [
        "/usr/bin/ffmpeg",
        "/usr/local/bin/ffmpeg",
        "/bin/ffmpeg",
    ]

    for path in possible_paths:

        if os.path.isfile(path):
            return path

    raise RuntimeError(
        "FFmpeg was not found on Streamlit Cloud.\n\n"
        "Make sure packages.txt exists in the ROOT "
        "of your GitHub repository and contains:\n\n"
        "ffmpeg\n\n"
        "Then reboot the Streamlit app."
    )


# ============================================================
# Convert MP3 / MP4 / Other Media to WAV
# ============================================================

def convert_to_wav(input_path: str):

    ffmpeg = get_ffmpeg()

    if not os.path.exists(input_path):

        raise FileNotFoundError(
            f"Input file not found: {input_path}"
        )

    output_path = (
        os.path.splitext(input_path)[0]
        + "_converted.wav"
    )

    command = [
        ffmpeg,

        "-y",

        "-i",
        input_path,

        # Mono audio
        "-ac",
        "1",

        # 16 kHz
        "-ar",
        "16000",

        # PCM WAV
        "-acodec",
        "pcm_s16le",

        output_path,
    ]

    try:

        subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    except FileNotFoundError:

        raise RuntimeError(
            "FFmpeg executable was not found.\n\n"
            "Check packages.txt and redeploy "
            "the Streamlit application."
        )

    except subprocess.CalledProcessError as e:

        raise RuntimeError(
            "FFmpeg conversion failed.\n\n"
            + e.stderr[-3000:]
        )

    if not os.path.exists(output_path):

        raise RuntimeError(
            "FFmpeg finished but the WAV file "
            "was not created."
        )

    return output_path


# ============================================================
# Download YouTube Audio
# ============================================================

def download_youtube_audio(url: str):

    ffmpeg = get_ffmpeg()

    output_template = os.path.join(
        DOWNLOAD_DIR,
        "%(id)s.%(ext)s"
    )

    po_server_url = st.secrets.get(
        "BGUTIL_POT_URL",
        ""
    )

    ydl_opts = {

        "format": "bestaudio/best",

        "outtmpl": output_template,

        "noplaylist": True,

        "retries": 3,

        "fragment_retries": 3,

        "extractor_retries": 3,

        "socket_timeout": 30,

        "ffmpeg_location": ffmpeg,

        "extractor_args": {

            "youtube": {
                "player_client": ["mweb"]
            },

            "youtubepot-bgutilhttp": {
                "base_url": po_server_url
            },
        },

        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
            }
        ],

        "quiet": True,
        "no_warnings": False,
    }

    try:

        with yt_dlp.YoutubeDL(
            ydl_opts
        ) as ydl:

            info = ydl.extract_info(
                url,
                download=True
            )

            video_id = info["id"]

        wav_path = os.path.join(
            DOWNLOAD_DIR,
            f"{video_id}.wav"
        )

        if os.path.exists(wav_path):
            return wav_path

        # Search for downloaded media
        possible_files = [
            os.path.join(
                DOWNLOAD_DIR,
                f"{video_id}.webm"
            ),
            os.path.join(
                DOWNLOAD_DIR,
                f"{video_id}.m4a"
            ),
            os.path.join(
                DOWNLOAD_DIR,
                f"{video_id}.mp4"
            ),
        ]

        for file in possible_files:

            if os.path.exists(file):

                return convert_to_wav(file)

        raise RuntimeError(
            "YouTube audio was downloaded but "
            "the WAV file could not be found."
        )

    except yt_dlp.utils.DownloadError as e:

        error = str(e)

        if "403" in error:

            raise RuntimeError(
                "YouTube returned HTTP 403 Forbidden.\n\n"
                "Check your PO-token server configuration."
            )

        raise RuntimeError(
            f"YouTube download failed:\n{error}"
        )


# ============================================================
# Split WAV into Chunks
# ============================================================

def chunk_audio(
    wav_path,
    chunk_minutes=10
):

    chunk_paths = []

    with wave.open(
        wav_path,
        "rb"
    ) as wf:

        params = wf.getparams()

        frame_rate = wf.getframerate()

        chunk_frames = (
            chunk_minutes
            * 60
            * frame_rate
        )

        index = 0

        while True:

            frames = wf.readframes(
                chunk_frames
            )

            if not frames:
                break

            chunk_path = (
                f"{wav_path}_chunk_{index}.wav"
            )

            with wave.open(
                chunk_path,
                "wb"
            ) as out:

                out.setparams(params)

                out.writeframes(frames)

            chunk_paths.append(
                chunk_path
            )

            index += 1

    return chunk_paths


# ============================================================
# Process Input
# ============================================================

def process_input(source):

    if source.startswith(
        ("http://", "https://")
    ):

        print(
            "Downloading YouTube audio..."
        )

        wav_path = (
            download_youtube_audio(source)
        )

    else:

        print(
            "Converting uploaded media..."
        )

        wav_path = convert_to_wav(
            source
        )

    print(
        "Chunking audio..."
    )

    chunks = chunk_audio(
        wav_path
    )

    return chunks
```
