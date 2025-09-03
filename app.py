import streamlit as st
from pytube import YouTube
import openai
import os

openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("Transcrever Vídeo do YouTube 🎥➡️📝")

link = st.text_input("Cole o link do YouTube aqui:")

if link:
    if st.button("Transcrever"):
        try:
            st.info("Baixando áudio do vídeo...")
            yt = YouTube(link)
            stream = yt.streams.filter(only_audio=True, mime_type="audio/mp4").first()
            out_file = stream.download(filename="audio.mp4")


            st.info("Enviando áudio para transcrição...")
            with open(out_file, "rb") as f:
                transcript = openai.audio.transcriptions.create(
                    model="gpt-4o-mini-transcribe",
                    file=f,
                    response_format="text"  # força resposta só em texto
                )
            
            st.success("Transcrição concluída!")
            st.text_area("Texto transcrito:", transcript, height=300)

            os.remove(out_file)

        except Exception as e:
            st.error(f"Erro: {e}")
