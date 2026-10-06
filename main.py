"""
Dental Appointment System — powered by LangGraph + Groq
"""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage
from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from uuid import UUID, uuid4

from dental_agents.agent import dental_graph

from db import Base, LocalSession, engine


class ChatMessageRecord(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(PostgreSQLUUID(as_uuid=True), nullable=False, index=True)
    role = Column(String(16), nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=10000)
    conversation_id: UUID | None = None


class ChatResponse(BaseModel):
    conversation_id: UUID
    reply: str


app = FastAPI(title="Dental Appointment Management API")


@app.on_event("startup")
def create_chat_history_table() -> None:
    Base.metadata.create_all(bind=engine)


def _message_text(message: AIMessage) -> str:
    content = message.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            part["text"]
            for part in content
            if isinstance(part, dict) and isinstance(part.get("text"), str)
        )
    return str(content)


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    conversation_id = request.conversation_id or uuid4()
    session: Session = LocalSession()

    try:
        stored_messages = (
            session.query(ChatMessageRecord)
            .filter(ChatMessageRecord.conversation_id == conversation_id)
            .order_by(ChatMessageRecord.created_at, ChatMessageRecord.id)
            .all()
        )
        history = [
            HumanMessage(content=row.content) if row.role == "user"
            else AIMessage(content=row.content)
            for row in stored_messages
        ]

        result = dental_graph.invoke(
            {"messages": history + [HumanMessage(content=request.message)]},
            config={"recursion_limit": 20},
        )
        assistant_message = next(
            (
                message
                for message in reversed(result.get("messages", []))
                if isinstance(message, AIMessage) and not message.tool_calls
            ),
            None,
        )
        if assistant_message is None:
            raise HTTPException(status_code=502, detail="The assistant returned no reply.")

        reply = _message_text(assistant_message)
        session.add_all(
            [
                ChatMessageRecord(
                    conversation_id=conversation_id,
                    role="user",
                    content=request.message,
                ),
                ChatMessageRecord(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=reply,
                ),
            ]
        )
        session.commit()
        return ChatResponse(conversation_id=conversation_id, reply=reply)
    except HTTPException:
        session.rollback()
        raise
    except SQLAlchemyError as exc:
        session.rollback()
        raise HTTPException(
            status_code=503,
            detail="Unable to read or save chat history in PostgreSQL.",
        ) from exc
    finally:
        session.close()

BANNER = """
╔══════════════════════════════════════════════════════════╗
║         Dental Appointment Management System             ║
║         Powered by LangGraph + Groq                      ║
╚══════════════════════════════════════════════════════════╝
Examples:
  • Show available slots for an orthodontist
  • Book patient 1000082 with Emily Johnson on 5/10/2026 9:00
  • Cancel appointment for patient 1000082 at 5/10/2026 9:00
  • Reschedule patient 1000082 from 5/10/2026 9:00 to 5/12/2026 10:00
  • What appointments does patient 1000048 have?

Type 'quit' to exit.
"""


def run():
    print(BANNER)
    history = []

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in {"quit", "exit", "bye"}:
            print("Goodbye!")
            break

        history.append(HumanMessage(content=user_input))

        print("\nAgent: ", end="", flush=True)
        final_messages = None

        try:
            for event_type, data in dental_graph.stream(
                {"messages": history},
                stream_mode=["messages", "values"],
                config={"recursion_limit": 20},
            ):
                if event_type == "messages":
                    chunk, meta = data
                    # Stream tokens only from the agent (not tool results)
                    if (
                        isinstance(chunk, AIMessageChunk)
                        and chunk.content
                        and not getattr(chunk, "tool_calls", None)
                    ):
                        print(chunk.content, end="", flush=True)
                elif event_type == "values":
                    final_messages = data.get("messages", [])
        except Exception as exc:
            print(f"\nError: {exc}")
            history.pop()  # Remove the HumanMessage to avoid consecutive user messages
            continue

        print()
        if final_messages:
            history = final_messages


if __name__ == "__main__":
    run()