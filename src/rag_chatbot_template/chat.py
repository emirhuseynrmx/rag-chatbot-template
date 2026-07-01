from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated

import typer
from pydantic import BaseModel, ConfigDict

from rag_chatbot_template.retrieve import RetrievedChunk, retrieve
from rag_chatbot_template.store import VectorStore

app = typer.Typer(help="Ask questions against a local RAG vector store.")


class RagAnswer(BaseModel):
    model_config = ConfigDict(frozen=True)

    question: str
    answer: str
    sources: list[str]
    retrieved_chunks: list[dict[str, str | float]]
    used_llm: bool = False


def _call_claude(question: str, context: str) -> str | None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)
        system = (
            "You are a helpful business assistant. "
            "Answer the user's question using ONLY the provided context. "
            "Be concise and factual. "
            "If the answer is not in the context, say: 'This information is not covered in my knowledge base.'"
        )
        user_message = (
            f"Context:\n{context}\n\n"
            f"Question: {question}"
        )
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            system=system,
            messages=[{"role": "user", "content": user_message}],
        )
        return message.content[0].text
    except Exception:
        return None


def build_answer(question: str, retrieved: list[RetrievedChunk]) -> RagAnswer:
    if not retrieved:
        return RagAnswer(
            question=question,
            answer="No relevant document chunks were found for this question.",
            sources=[],
            retrieved_chunks=[],
            used_llm=False,
        )

    context = "\n\n".join(
        f"[{index}] Source: {item.chunk.source}\n{item.chunk.text}"
        for index, item in enumerate(retrieved, start=1)
    )

    llm_answer = _call_claude(question, context)

    if llm_answer:
        answer = llm_answer
        used_llm = True
    else:
        # Retrieval-only fallback — shows context for the user or a downstream LLM
        answer = (
            "Retrieved context (set ANTHROPIC_API_KEY for AI-generated answers):\n\n"
            + context
        )
        used_llm = False

    return RagAnswer(
        question=question,
        answer=answer,
        sources=sorted({item.chunk.source for item in retrieved}),
        retrieved_chunks=[
            {
                "id": item.chunk.id,
                "source": item.chunk.source,
                "score": item.score,
                "preview": item.chunk.text[:240],
            }
            for item in retrieved
        ],
        used_llm=used_llm,
    )


def ask_question(question: str, store: VectorStore, *, top_k: int = 3) -> RagAnswer:
    return build_answer(question, retrieve(question, store, top_k=top_k))


@app.command()
def ask(
    question: Annotated[str, typer.Argument(help="Question to ask.")],
    store: Annotated[Path, typer.Option(help="Vector store JSON path.")] = Path(
        "vector_store/store.json"
    ),
    top_k: Annotated[int, typer.Option(help="Number of chunks to retrieve.")] = 3,
) -> None:
    answer = ask_question(question, VectorStore.load(store), top_k=top_k)
    if answer.used_llm:
        typer.echo(f"[Claude] {answer.answer}")
    else:
        typer.echo(answer.answer)
    if answer.sources:
        typer.echo("\nSources:")
        for source in answer.sources:
            typer.echo(f"- {source}")
