import streamlit as st
from pytube import YouTube
import openai
import os
from pydub import AudioSegment

# 🔑 Sua chave vai em .streamlit/secrets.toml no Streamlit Cloud
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("Transcrever Vídeo do YouTube 🎥➡️📝")

# Função para dividir o áudio em blocos menores
def split_audio(file_path, chunk_length_ms=60_000):
    audio = AudioSegment.from_file(file_path)
    chunks = []
    for i in range(0, len(audio), chunk_length_ms):
        chunk = audio[i:i+chunk_length_ms]
        chunk_name = f"chunk_{i//chunk_length_ms}.mp3"
        chunk.export(chunk_name, format="mp3")
        chunks.append(chunk_name)
    return chunks

# Entrada do link do YouTube
link = st.text_input("Cole o link do YouTube aqui:")

if link:
    if st.button("Transcrever"):
        try:
            st.info("🎵 Baixando áudio do vídeo...")
            yt = YouTube(link)
            stream = yt.streams.filter(only_audio=True, mime_type="audio/mp4").first()
            out_file = stream.download(filename="audio.mp4")

            st.info("✂️ Dividindo áudio em partes menores...")
            chunks = split_audio(out_file, chunk_length_ms=60_000)  # 1 min cada parte

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
