from urllib.parse import urlparse, parse_qs

from youtube_transcript_api import YouTubeTranscriptApi

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from langchain_community.vectorstores import FAISS

from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import (
    RunnableParallel,
    RunnablePassthrough,
    RunnableLambda
)


def extract_video_id(url):
    if "youtu.be/" in url:
        return url.split("/")[-1].split("?")[0]

    parsed = urlparse(url)

    if "youtube.com" in parsed.netloc:
        return parse_qs(parsed.query).get("v", [None])[0]

    return None


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def get_transcript(video_id):
    try:
        api = YouTubeTranscriptApi()

        transcript_list = api.list(video_id)

        try:
            transcript_data = transcript_list.find_transcript(["en"]).fetch()
        except:
            transcript_data = next(iter(transcript_list)).fetch()

        transcript = " ".join(
            chunk.text for chunk in transcript_data
        )

        return transcript

    except Exception as e:
        raise Exception(
            f"Transcript fetch failed.\n\n{str(e)}"
        )


def build_rag_components(youtube_url):

    video_id = extract_video_id(youtube_url)

    if not video_id:
        raise ValueError("Invalid YouTube URL")

    transcript = get_transcript(video_id)

    if not transcript.strip():
        raise Exception("Empty transcript received")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    docs = splitter.create_documents([transcript])

    embeddings = MistralAIEmbeddings(
        model="mistral-embed"
    )

    vector_store = FAISS.from_documents(
        docs,
        embeddings
    )

    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}
    )

    llm = ChatMistralAI(
        model="mistral-large-latest",
        temperature=0,
        streaming=True
    )

    prompt = PromptTemplate(
        template="""
You are a helpful assistant.

Use the transcript context when relevant.

Transcript Context:
{context}

Question:
{question}

Answer:
""",
        input_variables=["context", "question"]
    )

    chain = (
        RunnableParallel(
            {
                "context": retriever | RunnableLambda(format_docs),
                "question": RunnablePassthrough()
            }
        )
        | prompt
        | llm
    )

    return chain