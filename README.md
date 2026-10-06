# Dental Recruitment Assistant

An AI-powered dental appointment assistant built with Python, FastAPI, Streamlit, and LangGraph. The app lets users ask natural-language questions about dental availability, book or cancel appointments, and check patient scheduling details.

## Overview

This project combines:

- A LangGraph-powered agent for dental scheduling workflows
- A FastAPI backend that exposes a `/chat` endpoint
- A Streamlit frontend for conversational interaction
- CSV-backed appointment data and PostgreSQL-backed chat history
- Groq-based LLM access for appointment assistance

The assistant is designed to help with tasks such as:

- Checking doctor availability
- Listing available appointment slots
- Booking appointments for a patient
- Cancelling an existing booking
- Rescheduling appointments
- Reviewing a patient's appointment history

## Tech Stack

- Python 3.10+
- FastAPI
- Streamlit
- SQLAlchemy
- LangChain / LangGraph
- Groq LLM
- PostgreSQL
- Pandas

## Project Structure

```text
.
├── .env                      # Environment configuration
├── db.py                    # Database engine and session setup
├── main.py                  # FastAPI backend + command-line agent entry
├── streamlit_app.py         # Streamlit web UI
├── requirements.txt         # Python dependencies
├── doctor_availability.csv  # Appointment and doctor availability dataset
├── dental_agents/
│   ├── agent.py            # LangGraph agent configuration
│   ├── agents/             # Agent modules
│   ├── config/             # app settings
│   ├── models/             # Typed app state and settings
│   ├── tools/              # Appointment tools (read/write CSV data)
│   ├── utils.py            # Utility helpers
│   └── ...
└── README.md
```

## Prerequisites

Before running the app, make sure you have:

- Python 3.10 or newer
- PostgreSQL database running locally or remotely
- A Groq API key
- A virtual environment (recommended)

## Environment Configuration

Create a `.env` file in the project root with values similar to the following:

```env
GROQ_API_KEY="your_groq_api_key"
MODEL_NAME="openai/gpt-oss-120b"
TEMPERATURE=0
DATABASE_URL="postgresql://username:password@localhost:5432/dental_recruitment"
BACKEND_API_URL="http://127.0.0.1:8000"
```

Notes:

- `GROQ_API_KEY` is required for the LangGraph agent to talk to Groq.
- `DATABASE_URL` is used for PostgreSQL-backed chat history.
- `BACKEND_API_URL` is used by the Streamlit app to call the backend API.

## Installation

1. Clone the repository.
2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate     # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Application

### 1) Start the backend API

```bash
uvicorn main:app --reload
```

The API will run on:

```text
http://127.0.0.1:8000
```

### 2) Start the Streamlit app

In a second terminal:

```bash
streamlit run streamlit_app.py
```

This launches the chat UI in the browser.

## API Endpoint

### `POST /chat`

Request body:

```json
{
  "message": "Show available slots for an orthodontist",
  "conversation_id": "optional-uuid"
}
```

Response:

```json
{
  "conversation_id": "uuid",
  "reply": "Here are the available orthodontist slots..."
}
```

## Features

- Natural-language appointment assistance
- State-aware conversational history
- Booking, cancellation, and rescheduling workflows
- Doctor specialization lookup
- Slot availability validation
- CSV-based schedule management

## Example Prompts

- Show available slots for an orthodontist
- Book patient 1000082 with Emily Johnson on 5/10/2026 9:00
- Cancel appointment for patient 1000082 at 5/10/2026 9:00
- Reschedule patient 1000082 from 5/10/2026 9:00 to 5/12/2026 10:00
- What appointments does patient 1000048 have?

## Notes

- The project uses a CSV file (`doctor_availability.csv`) as the operational appointment dataset for booking tools.
- Chat history is stored in PostgreSQL via SQLAlchemy.
- The assistant expects date strings in the format `M/D/YYYY H:MM`.

## Troubleshooting

- If the backend cannot connect to PostgreSQL, verify your `DATABASE_URL` and make sure the database is running.
- If the assistant cannot respond, confirm that your `GROQ_API_KEY` is valid and present in `.env`.
- If the Streamlit frontend cannot reach the API, check that the backend is running and that `BACKEND_API_URL` matches the server address.

## License

This project does not currently include a license file. If you plan to distribute or publish it, add a license appropriate for your use case.
