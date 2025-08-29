import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import glob
import tempfile
from gtts import gTTS
import base64

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Charger les fichiers Markdown
def load_markdown_files(directory="docs"):
    try:
        markdown_content = ""
        # Find all .md files in the specified directory
        for file_path in glob.glob(os.path.join(directory, "*.md", "*.mdx")):
            with open(file_path, "r", encoding="utf-8") as file:
                markdown_content += f"\n\n## Contenu du fichier : {os.path.basename(file_path)}\n\n"
                markdown_content += file.read()
        return markdown_content
    except Exception as e:
        return f"Erreur lors du chargement des fichiers Markdown : {str(e)}"
    
# chargement des fichiers de la documentation
docs_directory = "docs"  
markdown_content = load_markdown_files(docs_directory)

# Instruction à suivre par l'IA
system_prompt = f""" 
Tu es une intelligence artificielle spécialement conçue pour guider les utilisateurs de l'ERP Uptiimum durant leur navigation. Tu devras les guider en te basant sur les descriptions de chacune des procédures renseignées dans les fichiers de la documentation. l'application ne compte que 5 modules : gestion des patients, gestion de la caisse, gestion du laboratoire, gestion de la pharmacie et gestion des ressources humaines, qui sont mentionner dans l'entête de chaque fichier de la documentation. les éléments à l'intérieur sont des sections et des sous sections des modules principaux.
{markdown_content}
Suis ces intructions:
- Ne répond qu'aux questions liées à la documentation renseignée plus haut.
- Si une question n'ayant aucun trait avec les modules de l'application est posée, réponds par : "J'aimerai bien répondre à votre préoccupation, mais je ne pourrai vous aider qu'en ce qui concerne l'application Uptiimum."
- Produit une réponse détaillée et précise basée sur la documentation.
- Si la documentation ne contient pas assez d'informations pour répondre à une question, indique : "Je n'ai pas assez d'informations pour répondre à cette question."
- Ne renseigne jamais tes sources d'information.
- Tu dois répondre en français, toujours rester poli et respectueux.
- Ne dis bonjour qu'au début de la conversation (à moins que l'utilisateur t'y oblige), ne dis plus à chaque fois "selon la documentation" et prononce "E R P Uptimum".
- Consulte toujours les fichiers de la documentation avant de répondre
"""

# Streamlit app configuration
# traitement de l'icône
from PIL import Image
img = Image.open("../logo.png")
img.save("myicon.ico", format='ICO', sizes=[(64, 64)])

#configuration de la page
st.set_page_config(
    page_title='Assistant de Navigation',
    page_icon='myicon.ico',
    #layout='wide',
    #initial_sidebar_state='expanded'
)

# Design de la page
st.markdown("""
    <style>
    .stApp {
        background-color: #09034A;
        color: white;
    }
    .fixed-title {
        position: sticky;
        text-align: center;
        top: 0;
        background-color: #09034A;
        z-index: 1000;
        padding: 10px 0;
        border-bottom: 1px solid #ffffff33;
        margin-bottom: 20px;
    }
    .stChatFloatingInputContainer {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
    }
    .user-message {
        # background-color: #0B0475;
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
        text-align: right;
    }
    .bot-message {
        background-color: #FFFFFF;
        text-align: left;
        color: black;
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
            .sidebar .sidebar-content {
        background-color: #1a1a4d;
        color: white;
        padding: 10px;
    }
    .speaker-icon {
        position: absolute;
        bottom: 5px;
        right: 5px;
        width: 24px;
        height: 24px;
        cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar for navigation
st.sidebar.title("Navigation")
if st.sidebar.button("Chatbot"):
    st.session_state.page = "Chatbot"
if st.sidebar.button("Prédictions"):
    st.session_state.page = "Prédictions"

# Set default page if none is selected
if "page" not in st.session_state:
    st.session_state.page = "Chatbot"


# Display content based on selected page
if st.session_state.page == "Chatbot":
    # Initialize session state for messages
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": system_prompt}
        ]

    # Titre
    st.markdown('<div class="fixed-title"><h1>Uptiimum AI</h1></div>', unsafe_allow_html=True)

   
    # Conserver l'historique des messages
    for message in st.session_state.messages[1:]:  # Alterner les locuteurs
        if message["role"] == "user":
            st.markdown(f'<div class="user-message"><strong>🙍🏾‍♂️:</strong> {message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-message"><strong>🧠:</strong> {message["content"]}</div>', unsafe_allow_html=True)

          # Generate and display audio for bot responses
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                tts = gTTS(message["content"], lang="fr", slow=True)  
                tts.save(tmp_file.name)
                # Encode audio in base64
                with open(tmp_file.name, "rb") as audio_file:
                    audio_bytes = audio_file.read()
                    audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
                st.audio(tmp_file.name, format="audio/mp3", start_time=0)
                # Clean up temporary file after display
                # os.unlink(tmp_file.name)

    # User input
    user_input = st.chat_input("Posez votre question ici...")

    if user_input:
        # AJouter à la suite la question de l'utilisateur
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Simulate thinking with a placeholder
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown("Réflexion de l'IA...")
        
        # Réponse via Groq API
        chat_completion = client.chat.completions.create(
            messages=st.session_state.messages,
            model="llama3-70b-8192",  # You can change this to other models
            temperature=0.7,
            max_tokens=1024,
        )

        #for chunk in stream:
            #if chunk.choices[0].delta.content is not None:
                #response += chunk.choices[0].delta.content
                #thinking_placeholder.markdown(f"Je réfléchis... {response}")
        
        # Clear the thinking placeholder and append the final response
        thinking_placeholder.empty()

        response = chat_completion.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

elif st.session_state.page == "Prédictions":    
    # Page "Prédictions"
    st.title("Prédictions")
    st.markdown("""
    ## Bienvenue sur la page Prédictions
    Cette section est un exemple d'un autre module accessible via la barre latérale.
    Vous pouvez personnaliser ce module pour inclure d'autres fonctionnalités, comme :
    - Une page d'informations sur le projet
    - Un tableau de bord de statistiques
    - Une interface pour gérer les paramètres du chatbot
    """)        