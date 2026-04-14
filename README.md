# Airbnb Concierge

Automatically processes incoming Airbnb emails via Gmail and classifies them using a local LLM (Ollama).

## Architecture

```
Gmail (Airbnb emails)
    └── GmailService.fetch_airbnb_emails()   # fetches & decodes emails
            └── ConciergeAgent.process_email()   # classifies via Ollama
                    └── Message(name, message, type)   # structured output
```

### Key files

| File | Responsibility |
|------|---------------|
| `src/services/email_service.py` | Gmail OAuth, email fetching, orchestration |
| `src/agent/concierge.py` | Ollama-backed email classifier |
| `src/models/message.py` | `Message` Pydantic model |
| `src/models/booking.py` | `Booking` Pydantic model |
| `src/models/enums.py` | `MessageType` enum (problem, question, complaint, other) |

## Recent changes

### `src/services/email_service.py`
- Replaced stub `query_email` with `fetch_airbnb_emails(max_results)` — queries Gmail with `from:@airbnb.com`, fetches full message content, decodes base64 bodies, handles multipart MIME
- Added `_get_email_body(payload)` — recursively walks MIME parts to extract plain text
- Added `process_airbnb_emails(agent)` — feeds each fetched email into the agent and returns a list of `Message` objects
- Fixed `_get_credentials` to use `self.token_path` consistently

### `src/agent/concierge.py`
- Completed `process_email` — now calls `self.client.chat(...)` correctly (was incorrectly passing client as model), parses the LLM's JSON response, and returns a `Message` object
- Returns `None` on any parsing/LLM failure so the caller can skip bad results gracefully

---

## TODOs before going live

### Ollama / LLM
- [ ] Pull and test the model: `ollama pull <model-name>` (currently hardcoded as `"concierge"` — rename or create a Modelfile)
- [ ] Validate that the model reliably returns valid JSON matching `{name, type, message}`; add a retry or stricter prompt if not
- [ ] Handle booking emails: `ConciergeAgent` system prompt already mentions booking extraction, but `process_email` always returns `Message` — decide whether booking emails should return a `Booking` object instead and wire that up

### Gmail / Auth
- [ ] Place `credentials.json` (OAuth client secret from Google Cloud Console) in the project root or configure its path
- [ ] Run the app once interactively to complete the OAuth flow and generate `token.json`
- [ ] Restrict the Gmail OAuth scope if write access is eventually needed (e.g. marking emails as read)

### Application entry point
- [ ] Create a main entry point (e.g. `main.py`) that instantiates `GmailService` and `ConciergeAgent` and calls `process_airbnb_emails`
- [ ] Decide on a polling strategy: cron job, `schedule` library, or a long-running loop with a sleep interval

### Persistence
- [ ] Store processed `Message` / `Booking` objects somewhere (database, file, etc.) to avoid re-processing the same emails on every run
- [ ] Track the last-processed email timestamp or use Gmail's `historyId` for incremental fetching

---

## How to test

### 1. Unit test the email body parser

```python
from src.services.email_service import GmailService

# Minimal fake payload
payload = {
    "mimeType": "text/plain",
    "body": {"data": __import__("base64").urlsafe_b64encode(b"Hello world").decode()},
}
svc = object.__new__(GmailService)   # skip __init__ / OAuth
assert svc._get_email_body(payload) == "Hello world"
```

### 2. Test the agent with a fake Ollama client

```python
from unittest.mock import MagicMock
from src.agent.concierge import ConciergeAgent

mock_client = MagicMock()
mock_client.chat.return_value = MagicMock(
    message=MagicMock(content='{"name": "Alice", "type": "question", "message": "What is the wifi password?"}')
)

agent = ConciergeAgent(client=mock_client)
msg = agent.process_email("Wifi question", "Hi, what is the wifi password?", __import__("datetime").datetime.now())

assert msg.name == "Alice"
assert msg.type.value == "question"
```

### 3. End-to-end with real Gmail

```python
import ollama
from src.services.email_service import GmailService
from src.agent.concierge import ConciergeAgent

client = ollama.Client()
agent = ConciergeAgent(client)
gmail = GmailService()   # triggers OAuth browser flow on first run

messages = gmail.process_airbnb_emails(agent)
for m in messages:
    print(m)
```
