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
# FFmpeg
# ============================================================

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
        "FFmpeg is not installed.\n\n"
        "Create packages.txt in the project root "
        "with:\n\n"
        "ffmpeg"
    )


# ============================================================
# YouTube Downloader
# ============================================================

def download_youtube_audio(url: str) -> str:

    ffmpeg = get_ffmpeg()

    output_template = os.path.join(
        DOWNLOAD_DIR,
        "%(id)s.%(ext)s"
    )

    ydl_opts = {

        # Best available audio
        "format": "bestaudio/best",

        # Safe filename using video ID
        "outtmpl": output_template,

        # Don't download playlists
        "noplaylist": True,

        # Retry configuration
        "retries": 3,
        "fragment_retries": 3,
        "extractor_retries": 3,

        # Network timeout
        "socket_timeout": 30,

        # FFmpeg
        "ffmpeg_location": ffmpeg,

        # ----------------------------------------------------
        # PO TOKEN PROVIDER
        # ----------------------------------------------------
        #
        # bgutil-ytdlp-pot-provider installs a yt-dlp
        # extractor plugin which supplies PO tokens.
        #
        "extractor_args": {
            "youtube": {
                "player_client": ["mweb"]
            }
        },

        # Convert audio to WAV
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

        print("Extracting YouTube information...")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

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

        # If yt-dlp produced WAV directly
        if os.path.exists(wav_path):
            return wav_path

        # Look for another downloaded format
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

            return convert_to_wav(
                source_file
            )

        raise RuntimeError(
            "YouTube audio was downloaded, "
            "but the WAV file was not found."
        )

    except yt_dlp.utils.DownloadError as e:

        error = str(e)

        if "403" in error or "Forbidden" in error:

            raise RuntimeError(
                "YouTube returned HTTP 403 Forbidden.\n\n"
                "The YouTube PO-token provider could not "
                "obtain a valid token for this request.\n\n"
                "Check that bgutil-ytdlp-pot-provider is "
                "installed correctly on Streamlit Cloud."
            )

        raise RuntimeError(
            f"YouTube download failed:\n{error}"
        )

    except Exception as e:

        raise RuntimeError(
            f"YouTube processing failed:\n{e}"
        )


# ============================================================
# Convert to WAV
# ============================================================

def convert_to_wav(input_path: str):

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
        "-ac",
        "1",
        "-ar",
        "16000",
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
            "FFmpeg did not create the WAV file."
        )

    return output_path


# ============================================================
# Chunk Audio
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
