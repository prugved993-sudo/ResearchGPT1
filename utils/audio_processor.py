```python
import os
import wave
import shutil
import subprocess
import yt_dlp


# ============================================================
# Configuration
# ============================================================

DOWNLOAD_DIR = "downloads"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# ============================================================
# Find FFmpeg
# ============================================================

def get_ffmpeg():
    """
    Find the FFmpeg executable.
    Works locally and on Streamlit Cloud.
    """

    ffmpeg = shutil.which("ffmpeg")

    if ffmpeg:
        return ffmpeg

    possible_paths = [
        "/usr/bin/ffmpeg",
        "/usr/local/bin/ffmpeg",
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    raise RuntimeError(
        "FFmpeg is not installed.\n\n"
        "For Streamlit Cloud, create packages.txt "
        "in the project root containing:\n\n"
        "ffmpeg"
    )


# ============================================================
# Download YouTube Audio
# ============================================================

def download_youtube_audio(url: str) -> str:
    """
    Download audio from a YouTube URL and convert it to WAV.

    Returns:
        Path to the downloaded WAV file.
    """

    # Make sure FFmpeg exists before starting
    ffmpeg = get_ffmpeg()

    # Use video ID instead of title.
    # This avoids problems with special characters in titles.
    output_template = os.path.join(
        DOWNLOAD_DIR,
        "%(id)s.%(ext)s"
    )

    ydl_opts = {
        # Prefer audio
        "format": "bestaudio/best",

        # Output filename
        "outtmpl": output_template,

        # Only download one video
        "noplaylist": True,

        # Retry settings
        "retries": 3,
        "fragment_retries": 3,
        "extractor_retries": 3,

        # Network timeout
        "socket_timeout": 30,

        # FFmpeg location
        "ffmpeg_location": ffmpeg,

        # Convert downloaded audio to WAV
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
            }
        ],

        # Keep console output limited
        "quiet": True,
        "no_warnings": False,
    }

    try:

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            print("Extracting YouTube information...")

            info = ydl.extract_info(
                url,
                download=True
            )

            video_id = info.get("id")

            if not video_id:
                raise RuntimeError(
                    "Could not determine YouTube video ID."
                )

            wav_path = os.path.join(
                DOWNLOAD_DIR,
                f"{video_id}.wav"
            )

            if not os.path.exists(wav_path):

                # yt-dlp may create a different extension
                # depending on the source.
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

                source_file = None

                for file in possible_files:
                    if os.path.exists(file):
                        source_file = file
                        break

                if source_file:

                    wav_path = convert_to_wav(
                        source_file
                    )

                else:
                    raise RuntimeError(
                        "YouTube audio was downloaded, "
                        "but the WAV file could not be found."
                    )

            return wav_path

    except yt_dlp.utils.DownloadError as e:

        error_message = str(e)

        if "403" in error_message or "Forbidden" in error_message:

            raise RuntimeError(
                "YouTube returned HTTP 403 Forbidden.\n\n"
                "YouTube is blocking the download request. "
                "This is usually caused by YouTube's current "
                "anti-bot / PO-token requirements.\n\n"
                "Make sure you are using the latest yt-dlp "
                "and a supported PO-token provider."
            )

        raise RuntimeError(
            f"YouTube download failed:\n{error_message}"
        )

    except Exception as e:

        raise RuntimeError(
            f"YouTube processing failed:\n{str(e)}"
        )


# ============================================================
# Convert Audio/Video to WAV
# ============================================================

def convert_to_wav(input_path: str) -> str:
    """
    Convert an audio/video file to:
        WAV
        Mono
        16 kHz

    This format works well with Whisper.
    """

    ffmpeg = get_ffmpeg()

    output_path = (
        os.path.splitext(input_path)[0]
        + "_converted.wav"
    )

    command = [
        ffmpeg,
        "-y",
        "-i",
        input_path,

        # Mono
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

    except subprocess.CalledProcessError as e:

        raise RuntimeError(
            "FFmpeg conversion failed:\n"
            + e.stderr[-2000:]
        )

    if not os.path.exists(output_path):

        raise RuntimeError(
            "FFmpeg completed but the output WAV "
            "file was not created."
        )

    return output_path


# ============================================================
# Split Audio into Chunks
# ============================================================

def chunk_audio(
    wav_path,
    chunk_minutes=10
):
    """
    Split WAV audio into chunks.

    Default:
        10 minutes per chunk
    """

    chunk_paths = []

    with wave.open(wav_path, "rb") as wf:

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

            chunk_paths.append(chunk_path)

            index += 1

    return chunk_paths


# ============================================================
# Process Input
# ============================================================

def process_input(source):
    """
    Process either:

    1. YouTube URL
    2. Local audio/video file

    Returns:
        List of audio chunks
    """

    if source.startswith(
        ("http://", "https://")
    ):

        print(
            "Downloading YouTube audio..."
        )

        wav_path = download_youtube_audio(
            source
        )

    else:

        print(
            "Converting local video..."
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
