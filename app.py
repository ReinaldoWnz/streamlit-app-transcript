import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import openai
import re

# Defina a chave da API da OpenAI como uma variável de ambiente no Streamlit Cloud
# openai.api_key = st.secrets["OPENAI_API_KEY"]
# Você pode pedir para o usuário digitar a chave para testar.
openai_api_key = st.text_input("Insira sua chave da API da OpenAI:", type="password")
if openai_api_key:
    openai.api_key = openai_api_key
    
def get_video_id(url):
    """Extrai o ID do vídeo do YouTube de um URL."""
    match = re.search(r'(?:v=|\/embed\/|\/watch\?v=|\/youtu\.be\/|\/shorts\/)([a-zA-Z0-9_-]{11})', url)
    return match.group(1) if match else None

def get_transcript(video_id):
    """Obtém a transcrição do YouTube."""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['pt', 'en'])
        transcript_text = ' '.join([item['text'] for item in transcript_list])
        return transcript_text
    except Exception as e:
        st.error(f"Erro ao obter a transcrição do vídeo. Certifique-se de que as legendas estão disponíveis. Detalhes do erro: {e}")
        return None

st.set_page_config(page_title="YouTube Transcriber e Resumidor")
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
            
            if openai_api_key:
                if st.button("Gerar Resumo"):
                    with st.spinner("Gerando resumo com a IA..."):
                        summary_text = summarize_with_openai(transcript_text)
                    
                    if summary_text:
                        st.subheader("Resumo do Vídeo")
                        st.write(summary_text)

# Para usar a API da OpenAI
def summarize_with_openai(text, model="gpt-3.5-turbo"):
    """Resumir o texto usando a API da OpenAI."""
    prompt = f"Resuma o seguinte texto de forma concisa e clara em português:\n\n{text}"
    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Você é um assistente útil para resumir textos."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Erro ao se comunicar com a API da OpenAI. Detalhes do erro: {e}")
        return None
