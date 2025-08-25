import re
import os
import uuid
import json
from dataclasses import dataclass
from typing import List, Dict, Tuple

import streamlit as st
import chromadb
from chromadb.config import Settings
from markdown_it import MarkdownIt
import ollama

# traitement de l'icône
from PIL import Image
img = Image.open("./logo-tdr.png")
img.save("myicon.ico", format='ICO', sizes=[(64, 64)])


#configuration de la page
st.set_page_config(
    page_title='Assistant de Navigation',
    page_icon='myicon.ico',
    #layout='wide',
    #initial_sidebar_state='expanded'
)

# -----------------------------
# Config de base
# -----------------------------
PERSIST_DIR = ".rag_index"
COLLECTION_NAME = "md_docs"
EMBED_MODEL = "nomic-embed-text"
CHAT_MODEL = "llama3.1"
TOP_K = 5
CHUNK_SIZE = 1200  # caractères
CHUNK_OVERLAP = 200  # caractères

# -----------------------------
# Outils Markdown & Chunking
# -----------------------------
md = MarkdownIt()

@dataclass
class DocChunk:
    id: str
    content: str
    source: str
    meta: Dict


def read_markdown_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def simple_md_chunker(text: str, source: str) -> List[DocChunk]:
    """Découpe le Markdown par blocs de taille ~CHUNK_SIZE avec chevauchement.
    Conserve des hints (titres) dans les métadonnées.
    """
    # Extraire les titres H1/H2/H3 pour les inclure en contexte
    headings = []
    for line in text.splitlines():
        m = re.match(r"^(#{1,3})\s+(.*)", line)
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()
            headings.append((level, title))

    chunks: List[DocChunk] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(n, start + CHUNK_SIZE)
        content = text[start:end]
        meta = {
            "headings": headings[:8],  # petit échantillon pour signaler la structure
            "start": start,
            "end": end,
        }
        chunks.append(
            DocChunk(
                id=str(uuid.uuid4()),
                content=content,
                source=source,
                meta=meta,
            )
        )
        if end == n:
            break
        start = max(end - CHUNK_OVERLAP, 0)
    return chunks


# -----------------------------
# Embeddings via Ollama
# -----------------------------

def embed_texts(texts: List[str]) -> List[List[float]]:
    """Retourne les embeddings via l'API Python ollama (local)."""
    # ollama.embeddings renvoie un dict { 'embedding': [...] }
    vectors = []
    for t in texts:
        resp = ollama.embeddings(model=EMBED_MODEL, prompt=t)
        vectors.append(resp["embedding"])  # type: ignore[index]
    return vectors


# -----------------------------
# ChromaDB : création/chargement de collection
# -----------------------------

def get_or_create_collection(persist_dir: str = PERSIST_DIR, name: str = COLLECTION_NAME):
    client = chromadb.Client(Settings(persist_directory=persist_dir, anonymized_telemetry=False))
    try:
        col = client.get_collection(name)
    except Exception:
        col = client.create_collection(name)
    return client, col


def reset_collection():
    if os.path.isdir(PERSIST_DIR):
        # Efface le dossier d'index
        for root, dirs, files in os.walk(PERSIST_DIR, topdown=False):
            for f in files:
                os.remove(os.path.join(root, f))
            for d in dirs:
                os.rmdir(os.path.join(root, d))
        os.rmdir(PERSIST_DIR)
    os.makedirs(PERSIST_DIR, exist_ok=True)


# -----------------------------
# Indexation
# -----------------------------

def index_markdown_files(paths: List[str]) -> Tuple[int, int]:
    """Lit, découpe, embed et insère dans Chroma. Retourne (#chunks, #docs)."""
    client, col = get_or_create_collection()

    total_chunks = 0
    for path in paths:
        text = read_markdown_text(path)
        chunks = simple_md_chunker(text, source=os.path.basename(path))

        # Embeddings
        embeddings = embed_texts([c.content for c in chunks])

        # Ajout à Chroma
        col.add(
            ids=[c.id for c in chunks],
            documents=[c.content for c in chunks],
            metadatas=[{"source": c.source, **c.meta} for c in chunks],
            embeddings=embeddings,
        )
        total_chunks += len(chunks)

    return total_chunks, len(paths)


# -----------------------------
# Recherche + Génération
# -----------------------------

def retrieve(question: str, k: int = TOP_K) -> List[Dict]:
    _, col = get_or_create_collection()
    q_emb = embed_texts([question])[0]
    res = col.query(query_embeddings=[q_emb], n_results=k, include=["documents", "metadatas", "distances", "ids"])  # type: ignore[arg-type]
    docs = []
    if res and res.get("documents"):
        for i in range(len(res["documents"][0])):
            docs.append({
                "id": res["ids"][0][i],
                "text": res["documents"][0][i],
                "meta": res["metadatas"][0][i],
                "distance": res["distances"][0][i],
            })
    return docs


def build_prompt(question: str, contexts: List[Dict]) -> List[Dict[str, str]]:
    context_blocks = []
    for i, c in enumerate(contexts, start=1):
        src = c["meta"].get("source", "")
        context_blocks.append(f"[Doc {i} | {src}]\n{c['text']}")
    context_text = "\n\n".join(context_blocks)

    system = (
        "Tu es un assistant RAG concis et factuel. Réponds UNIQUEMENT avec les informations trouvées dans le contexte. "
        "Si la réponse n'est pas dans le contexte, dis que tu ne sais pas. Cite les [Doc i] pertinents."
    )
    user = (
        f"Question:\n{question}\n\n"
        f"Contexte (extraits de documents):\n{context_text}\n\n"
        "Réponse :"
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def generate_answer(question: str) -> Tuple[str, List[Dict]]:
    ctxs = retrieve(question, k=TOP_K)
    messages = build_prompt(question, ctxs)

    # Appel Ollama (chat)
    resp = ollama.chat(model=CHAT_MODEL, messages=messages, options={
        "temperature": 0.2,
        "num_ctx": 8192,
    })
    answer = resp.get("message", {}).get("content", "")
    return answer, ctxs


# -----------------------------
# UI Streamlit
# -----------------------------

def ui():
    st.title("AI Assistant")

    with st.sidebar:
        st.header("Paramètres")
        st.markdown("**Modèles**:")
        st.code("""ollama pull llama3\nollama pull nomic-embed-text""", language="bash")
        global CHAT_MODEL, EMBED_MODEL, TOP_K
        CHAT_MODEL = st.text_input("Modèle chat (Ollama)", CHAT_MODEL)
        EMBED_MODEL = st.text_input("Modèle embeddings (Ollama)", EMBED_MODEL)
        TOP_K = st.slider("Passages à récupérer (k)", min_value=1, max_value=10, value=TOP_K)

        st.divider()
        st.subheader("Index (persistant)")
        st.write(f"Dossier d'index : `{PERSIST_DIR}` | Collection : `{COLLECTION_NAME}`")
        if st.button("🗑️ Réinitialiser l'index"):
            reset_collection()
            st.success("Index réinitialisé.")

    st.markdown("### 1) Chargez le fichier Markdown")
    uploaded_files = st.file_uploader("Sélectionne un ou plusieurs .md", type=["md"], accept_multiple_files=True)

    if "_staged_files" not in st.session_state:
        st.session_state["_staged_files"] = []

    staged_paths: List[str] = []
    if uploaded_files:
        os.makedirs(".staged_md", exist_ok=True)
        for f in uploaded_files:
            p = os.path.join(".staged_md", f.name)
            with open(p, "wb") as out:
                out.write(f.getvalue())
            staged_paths.append(p)
        st.session_state["_staged_files"] = staged_paths
        st.success(f"{len(staged_paths)} fichier(s) prêt(s) pour indexation.")

    colA, colB = st.columns([1,1])
    with colA:
        if st.button("⚙️ Indexer / Réindexer les fichiers chargés"):
            if not st.session_state.get("_staged_files"):
                st.warning("Aucun fichier .md chargé.")
            else:
                n_chunks, n_docs = index_markdown_files(st.session_state["_staged_files"])
                st.success(f"Indexation OK — {n_docs} doc(s), {n_chunks} chunk(s) ajoutés.")

    with colB:
        st.info("Vous pouvez indexer plusieurs fichiers .md à la fois.")

    st.markdown("### 2) Poser une question")
    question = st.text_input("Ta question (basée sur les .md indexés)", placeholder="Ex: Comment se connecter ?")

    if st.button("🔍 Interroger") or (question and st.session_state.get("auto_run")):
        if not question:
            st.warning("Pose une question.")
        else:
            with st.spinner("Génération de la réponse..."):
                try:
                    answer, ctxs = generate_answer(question)
                except Exception as e:
                    st.error(f"Erreur pendant la génération: {e}")
                    return
            st.subheader("Réponse")
            st.write(answer)
            if ctxs:
                st.markdown("#### Passages utilisés")
                for i, c in enumerate(ctxs, start=1):
                    with st.expander(f"[Doc {i}] {c['meta'].get('source','')} — distance={c.get('distance'):.4f}"):
                        st.code(c["text"][:2000])

    st.divider()
    st.caption("AI ERP Assistant • Streamlit • Josias TATOU © 2025")

if __name__ == "__main__":
    ui()