# Task 2: Structured Output 

This repository demonstrates how to force a Large Language Model to return strictly typed JSON data, validate it, and automatically repair it if the initial output fails validation. It uses LangChain, Pydantic, and Google's free-tier Gemini API.

## Core Features Implemented

This project fulfills the three core requirements of the task:

1. **Schema Definition:** A Pydantic `BaseModel` (`DeveloperProfile`) strictly defines the expected fields and data types (strings, integers, booleans, and lists) for the AI's response.
2. **Validation:** A `PydanticOutputParser` translates the Pydantic schema into formatting instructions for the LLM and strictly validates the incoming response against those rules.
3. **Retry/Repair Path:** A `RetryOutputParser` (via `langchain_classic`) catches validation exceptions. If the LLM generates malformed output, this mechanism automatically sends the bad output and the original prompt back to the LLM with instructions to fix it.

## Prerequisites

- Python 3.9+
- A free-tier Google Gemini API Key
- `uv` package manager (recommended)

## Setup & Execution

**1. Clone the repository and navigate to the folder:**

```bash
git clone <your-repo-url>
cd <your-folder-name>
```

**2. Create and activate a virtual environment:**

```bash
uv venv

# On Windows:
.venv\Scripts\activate

# On macOS/Linux:
source .venv/bin/activate
```

**3. Install dependencies:**

```bash
uv pip install -r requirements.txt
```

**4. Configure Environment Variables:** Create a `.env` file in the root directory and add your Gemini API key:

```text
GOOGLE_API_KEY="your_api_key_here"
```

**5. Run the script:**

```bash
python main.py
```

## Expected Output

The script reads a sample text snippet containing unstructured developer information, extracts it, and prints the status of the validation process followed by the clean, machine-readable JSON object:

```text
Extracting data...

✅ Success on first attempt.

--- Final Validated JSON ---
{
  "name": "Alex Chen",
  "years_of_experience": 10,
  "primary_skills": [
    "Python",
    "RAG pipelines",
    "Docker"
  ],
  "is_available": false
}
```
