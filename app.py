import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import openai
import re

# Configuração da página do Streamlit
st.set_page_config(page_title="YouTube Transcriber e Resumidor", layout="wide")
st.title("📹 Transcrever, Resumir e Analisar Vídeos do YouTube")
st.markdown("---")

# Carrega a chave da API do arquivo secrets.toml
if "OPENAI_API_KEY" in st.secrets:
    openai.api_key = st.secrets.OPENAI_API_KEY
else:
    st.error("Chave da API da OpenAI não encontrada. Por favor, configure-a no secrets.toml.")
    st.stop()

# Seção de Entrada do Vídeo
st.header("🔗 Insira o Link do Vídeo")
youtube_url = st.text_input("Cole o link do vídeo do YouTube aqui:")

def get_video_id(url):
    """Extrai o ID do vídeo do YouTube de um URL."""
    match = re.search(r'(?:v=|\/embed\/|\/watch\?v=|\/youtu\.be\/|\/shorts\/)([a-zA-Z0-9_-]{11})', url)
    return match.group(1) if match else None

def get_transcript(video_id):
    """Obtém a transcrição do YouTube."""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['pt', 'en'])
        return transcript_list
    except Exception as e:
        st.error(f"Erro ao obter a transcrição do vídeo. Verifique se as legendas estão disponíveis. Detalhes do erro: {e}")
        return None

def summarize_and_tag(transcript_text):
    """Resumir o texto e gerar tags usando a API da OpenAI."""
    try:
        summary_response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente útil."},
                {"role": "user", "content": f"Escreva um resumo conciso e claro de 100 palavras sobre este vídeo em português: {transcript_text}"}
            ],
            max_tokens=200
        )
        summary = summary_response.choices[0].message.content

        tags_response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente útil."},
                {"role": "user", "content": f"Gere uma lista de 5 a 10 tags relevantes para este vídeo em formato de lista Python, como ['tag1', 'tag2']: {transcript_text}"}
            ],
            max_tokens=100
        )
        tags = tags_response.choices[0].message.content
        return summary, tags
    except Exception as e:
        st.error(f"Erro ao se comunicar com a API da OpenAI. Detalhes do erro: {e}")
        return None, None

def get_timecodes(transcript_json):
    """Obtém os tópicos e seus códigos de tempo usando a API da OpenAI."""
    try:
        timecode_response = openai.chat.completions.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {"role": "system", "content": "Você é um computador de banco de dados. Os dados são armazenados em JSON {text:'', start:'', duration:''}. Com base no JSON a seguir, quais são os principais tópicos discutidos? Para cada tópico, forneça o código de tempo inicial em segundos e também no formato HH:MM:SS. Forneça a resposta como uma lista clara e formatada."},
                {"role": "user", "content": str(transcript_json)}
            ]
        )
        return timecode_response.choices[0].message.content
    except Exception as e:
        st.error(f"Erro ao obter os códigos de tempo com a API da OpenAI. Detalhes do erro: {e}")
        return None

# Processamento do formulário
if youtube_url:
    video_id = get_video_id(youtube_url)
    if not video_id:
        st.error("URL do YouTube inválido. Por favor, insira um URL válido.")
    else:
        with st.spinner("🚀 Analisando o vídeo..."):
            # Obtendo a transcrição
            transcript_list = get_transcript(video_id)
            if transcript_list:
                full_text = ' '.join([item['text'] for item in transcript_list])
                
                # Gerando resumo, tags e tópicos
                summary, tags = summarize_and_tag(full_text)
                timecode_info = get_timecodes(transcript_list)

                st.success("✔️ Análise concluída com sucesso!")
                st.markdown("---")
                
                # Exibindo resultados
                if summary:
                    st.header("📝 Resumo do Vídeo")
                    st.write(summary)
                
                if tags:
                    st.header("🏷️ Tags Relevantes")
                    st.write(tags)
                    
                if timecode_info:
                    st.header("⏰ Tópicos e Códigos de Tempo")
                    st.write(timecode_info)
                
                st.header("📜 Transcrição Completa")
                with st.expander("Clique para ver a transcrição completa"):
                    st.write(full_text)
