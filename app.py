import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import openai
import re

# Esta linha deve ser definida de acordo com sua chave, seja por
# st.secrets ou por uma variável de ambiente.
# openai.api_key = "SUA_CHAVE_AQUI" 

def get_video_id(url):
    """Extrai o ID do vídeo do YouTube de um URL."""
    match = re.search(r'(?:v=|\/embed\/|\/watch\?v=|\/youtu\.be\/|\/shorts\/)([a-zA-Z0-9_-]{11})', url)
    return match.group(1) if match else None

def get_transcript(video_id):
    """Obtém a transcrição do YouTube."""
    try:
        # A chamada correta para a função
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['pt', 'en'])
        transcript_text = ' '.join([item['text'] for item in transcript_list])
        return transcript_text
    except Exception as e:
        st.error(f"Erro ao obter a transcrição do vídeo. Certifique-se de que as legendas estão disponíveis. Detalhes do erro: {e}")
        return None

# O restante do seu aplicativo Streamlit
st.title("📹 Transcrever e Resumir Vídeos do YouTube")
youtube_url = st.text_input("Insira o link do vídeo do YouTube:")

if youtube_url:
    video_id = get_video_id(youtube_url)
    if not video_id:
        st.error("URL do YouTube inválido. Por favor, insira um URL válido.")
    else:
        with st.spinner("Obtendo transcrição..."):
            transcript_text = get_transcript(video_id)
        
        if transcript_text:
            st.success("Transcrição obtida com sucesso!")
            
            st.subheader("Transcrição Completa")
            with st.expander("Clique para ver a transcrição"):
                st.write(transcript_text)
