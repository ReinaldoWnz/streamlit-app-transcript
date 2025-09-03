import streamlit as st
from pytube import YouTube
import openai
import os
from moviepy.editor import AudioFileClip

# 🔑 chave da API (configure em .streamlit/secrets.toml)
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("Transcrever Vídeo do YouTube 🎥➡️📝")

# Função para dividir áudio em partes menores
def split_audio(file_path, chunk_length_sec=60):
    audio = AudioFileClip(file_path)
    duration = int(audio.duration)
    chunks = []
    for i in range(0, duration, chunk_length_sec):
        chunk_name = f"chunk_{i//chunk_length_sec}.mp3"
        subclip = audio.subclip(i, min(i + chunk_length_sec, duration))
        subclip.write_audiofile(chunk_name, codec="mp3", verbose=False, logger=None)
        chunks.append(chunk_name)
    audio.close()
    return chunks

# Entrada do link
link = st.text_input("Cole o link do YouTube aqui:")

if link:
    if st.button("Transcrever"):
        try:
            st.info("🎵 Baixando áudio do vídeo...")
            yt = YouTube(link)
            stream = yt.streams.filter(only_audio=True, mime_type="audio/mp4").first()
            out_file = stream.download(filename="audio.mp4")

            st.info("✂️ Dividindo áudio em partes menores...")
            chunks = split_audio(out_file, chunk_length_sec=60)  # 1 min cada parte

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
