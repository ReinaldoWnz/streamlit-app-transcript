import streamlit as st
from pytube import YouTube
import openai
import os
import subprocess

openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("Transcrever Vídeo do YouTube 🎥➡️📝")

# Função que divide o áudio em partes usando ffmpeg diretamente
def split_audio_ffmpeg(file_path, chunk_length_sec=60):
    # Primeiro pega a duração total do áudio com ffprobe
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    duration = float(result.stdout)
    chunks = []
    i = 0
    start = 0

    while start < duration:
        output_file = f"chunk_{i}.mp3"
        subprocess.run([
            "ffmpeg", "-y",
            "-i", file_path,
            "-ss", str(start),
            "-t", str(chunk_length_sec),
            "-acodec", "mp3",
            output_file
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        chunks.append(output_file)
        i += 1
        start += chunk_length_sec
    return chunks

link = st.text_input("Cole o link do YouTube aqui:")

if link:
    if st.button("Transcrever"):
        try:
            st.info("🎵 Baixando áudio do vídeo...")
            yt = YouTube(link)
            stream = yt.streams.filter(only_audio=True, mime_type="audio/mp4").first()
            out_file = stream.download(filename="audio.mp4")

            st.info("✂️ Dividindo áudio em partes menores...")
            chunks = split_audio_ffmpeg(out_file, chunk_length_sec=60)

            st.info("📝 Enviando para transcrição...")
            full_transcript = ""

            for idx, chunk in enumerate(chunks, start=1):
                st.write(f"Transcrevendo parte {idx}/{len(chunks)}...")
                with open(chunk, "rb") as f:
                    part = openai.audio.transcriptions.create(
                        model="gpt-4o-mini-transcribe",
                        file=f,
                        response_format="text"
                    )
                    full_transcript += part + "\n"
                os.remove(chunk)

            st.success("✅ Transcrição concluída!")
            st.text_area("Texto transcrito:", full_transcript, height=400)

            os.remove(out_file)

        except Exception as e:
            st.error(f"Erro: {e}")
