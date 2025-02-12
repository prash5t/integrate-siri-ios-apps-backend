# Village Pay Voice Assistant API - Product Requirements Document

## Product Information

- **Product Name**: Village Pay Voice Assistant API
- **Version**: Demo 1.0
- **Date**: February 2025

## 1. Overview / Introduction

Village Pay is a digital wallet similar to eSewa and Khalti that offers a range of financial services (e.g., loading money, transferring funds, utility payments, flight booking, etc.). The Village Pay mobile app is now being enhanced with Siri integration to allow users to use natural language voice commands. This demo API will serve as the backend conversational engine for Siri. The API receives a JSON payload with the conversation history and the current query, calls an LLM (via OpenAI's API) with a prompt that includes context and our (dummy) Village Pay features, and then returns a response that Siri will speak. The response includes a friendly sentence and a flag indicating if the conversation should continue.

## 2. Objectives

### Multi-Turn Conversation

Maintain context from the full conversation history so that follow-up queries (e.g., "transfer money to Suraj Shrestha") are understood in context.

### LLM-Powered Response

Use OpenAI's LLM (e.g., GPT-4) to dynamically generate:

- An SQL query (dummy for the demo) based on the conversation context
- A Siri response template that includes placeholders for dynamic values
- A conversation status flag (either "completed" or "pending")

### Siri Integration

Format the final API output so that the Village Pay app's Siri integration can decide whether to speak a final answer or ask follow-up questions.

### Demo-Ready

For the demo, no real database connection is required. The LLM is expected to provide dummy responses (and assume Village Pay's features) without an explicit database schema.

## 3. Functional Requirements

### 3.1 API Endpoint

- **URL**: /api/voice-assistant
- **Method**: POST
- **Content-Type**: application/json

### 3.2 Request Payload

The API expects a JSON payload with two key fields:

- `conversation_history`: An array of message objects. Each object has:
  - `role`: "user" or "assistant"
  - `content`: The text of the message
- `current_query`: A string containing the user's current voice command

**Example 1 (Multi-Turn Conversation – Transfer Money):**

```json
{
  "conversation_history": [
    { "role": "user", "content": "Transfer money" },
    { "role": "assistant", "content": "To whom you want to transfer money?" },
    { "role": "user", "content": "Suraj Shrestha" },
    {
      "role": "assistant",
      "content": "You have two Suraj Shrestha in contacts: one with number 9818483125 and another with number 9842746853. Which number do you want to use?"
    },
    { "role": "user", "content": "9842746853, transfer 50 rs" }
  ],
  "current_query": "9842746853, transfer 50 rs"
}
```

**Example 2 (Single-Turn Conversation – Check Balance):**

```json
{
  "conversation_history": [{ "role": "user", "content": "check my balance" }],
  "current_query": "check my balance"
}
```

### 3.3 LLM Prompt Construction

The API backend will construct a prompt for the LLM that includes:

- A brief description of Village Pay's features
- The full conversation history (for context)
- The current query
- A clear instruction for the LLM to return a JSON object with:
  - `sql_query`: A dummy SQL query (if applicable) or null if the query is vague
  - `siri_response_template`: A text template (with placeholders if needed) that Siri will eventually speak
  - `continueConversation`: Either true or false

**Example Prompt:**

```typescript
You are a Village Pay voice assistant. Your job is to analyze the following conversation history and current query and generate a JSON response in the following format:

{
  "sql_query": "<SQL_QUERY_OR_NULL>",
  "siri_response_template": "<STRING_WITH_PLACEHOLDERS>",
  "continueConversation": true | false
}

Village Pay is a wallet app that allows users to load money, transfer funds, check balances, make utility payments, book flights, pay bills, and more.

Conversation history:
User: Transfer money
Assistant: To whom you want to transfer money?
User: Suraj Shrestha
Assistant: You have two contacts named Suraj Shrestha: one with number 9818483125 and another with number 9842746853. Which number do you want to use?
User: 9842746853, transfer 50 rs

Current query: 9842746853, transfer 50 rs

Based on the above, generate a dummy SQL query (if applicable), a siri_response_template, and continueConversation.
```

### 3.4 LLM Response Format

The LLM is expected to respond with a JSON formatted string containing:

- `sql_query`: A dummy SQL query string (or null if not applicable)
- `siri_response_template`: A friendly sentence template that might include placeholders
- `continueConversation`: true or false

**Example Response – Check Balance:**

```json
{
  "sql_query": "SELECT balance FROM users WHERE user_id = 123;",
  "siri_response_template": "Your balance is ${balance} in Village Pay right now.",
  "continueConversation": false
}
```

**Example Response – Transfer Money (Incomplete Details):**

```json
{
  "sql_query": null,
  "siri_response_template": "You have two contacts for Suraj Shrestha: 9818483125 and 9842746853. Which number do you want to use and how much do you want to transfer?",
  "continueConversation": true
}
```

### 3.5 API Response to Siri

The final API response returned to the client (Siri) should be in the following format:

```json
{
  "sentenceSiriShouldSay": "<FINAL_SIRI_SENTENCE>",
  "continueConversation": <BOOLEAN>
}
```

- `sentenceSiriShouldSay`: The final sentence that Siri will speak
- `continueConversation`: A boolean value based on the LLM's response

**Example API Output – Check Balance:**

```json
{
  "sentenceSiriShouldSay": "Your balance is $100 in Village Pay right now.",
  "continueConversation": false
}
```

**Example API Output – Transfer Money:**

```json
{
  "sentenceSiriShouldSay": "You have two contacts for Suraj Shrestha: 9818483125 and 9842746853. Which number do you want to use and how much do you want to transfer?",
  "continueConversation": true
}
```

## 4. Non-Functional Requirements

### Demo-Ready

No actual database connectivity is required. All responses from the LLM can be dummy responses based on Village Pay features.

### Security

For the demo, the API endpoint will have no authentication or rate limiting. (In production, security measures would be required.)

### Performance

The demo should return results within an acceptable time frame (ideally less than 5 seconds per request).

### Extensibility

The design should allow later integration of a real database and more advanced error handling.

## 5. Assumptions and Limitations

### Assumptions

- The LLM (e.g., GPT-4) is capable of understanding the conversation context and Village Pay features without explicit schema details
- The conversation history provided in the API request is comprehensive enough for context

### Limitations

- This is a demo implementation; no real SQL execution or database integration is performed
- The dummy responses are based on assumptions about Village Pay's feature set

## 6. Dependencies

- Programming Language: Python 3.x
- Web Framework: Flask
- LLM Integration: OpenAI Python SDK (openai package)
- JSON Processing: Python's built-in json module
- No Database: For demo purposes, SQL queries are dummy strings only

## 7. High-Level Architecture

### Client (Siri / Village Pay App)

- Captures the conversation (with full history) and current user query
- Sends a POST request to the API endpoint with the JSON payload

### Flask API Endpoint

- Receives the JSON payload
- Constructs a prompt including conversation history, current query, and a brief description of Village Pay's services
- Sends the prompt to the OpenAI LLM
- Receives the response (in the defined JSON format)
- If an SQL query is provided, it (optionally) processes dummy data to replace placeholders
- Constructs the final API response in the Siri format

### Response (Siri)

- Uses the final response to speak to the user
- If continueConversation is true, Siri will ask the follow-up question

## 8. Deliverables

- Flask Application Code: A fully commented Python/Flask application implementing the described API endpoint
- LLM Prompt Documentation: A document outlining the prompt structure to be sent to OpenAI
- API Documentation: Documentation for how to call the API, including sample payloads and responses
- Demo Instructions: Step-by-step instructions on how to run the Flask API locally and test it with sample requests

## 9. Example Code Outline

```python
from flask import Flask, request, jsonify
import openai
import json

app = Flask(__name__)

# Set your OpenAI API key
openai.api_key = "YOUR_OPENAI_API_KEY"

def generate_prompt(conversation_history, current_query):
    # Convert conversation_history to a string for the prompt
    conversation_text = "\n".join(
        [f"{msg['role'].capitalize()}: {msg['content']}" for msg in conversation_history]
    )
    prompt = f"""
You are a Village Pay voice assistant. Your job is to analyze the following conversation history and current query and generate a JSON response in the following format:
{{
  "sql_query": "<SQL_QUERY_OR_NULL>",
  "siri_response_template": "<STRING_WITH_PLACEHOLDERS>",
  "continueConversation": true | false
}}

Village Pay is a digital wallet app that lets users load money, transfer funds, check balances, pay utility bills, book flights, purchase movie tickets, and more.

Conversation History:
{conversation_text}

Current Query: {current_query}

Please provide your response in JSON.
    """
    return prompt

@app.route('/api/voice-assistant', methods=['POST'])
def voice_assistant():
    data = request.get_json()
    conversation_history = data.get("conversation_history", [])
    current_query = data.get("current_query", "")

    prompt = generate_prompt(conversation_history, current_query)

    # Call the LLM (OpenAI API)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}]
        )
        llm_output = response["choices"][0]["message"]["content"]
        # For the demo, assume LLM returns valid JSON; otherwise, add error handling.
        llm_response = json.loads(llm_output)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # For demo purposes, we are not executing the SQL query.
    # Assume dummy data is used to replace any placeholders if necessary.
    # For example, if the response_template contains ${balance}, replace it with a dummy value.
    siri_response = llm_response.get("siri_response_template", "")
    continueConversation = llm_response.get("continueConversation", true)

    # Create the final response for Siri
    final_response = {
        "sentenceSiriShouldSay": siri_response,
        "continueConversation": continueConversation
    }

    return jsonify(final_response)

if __name__ == '__main__':
    app.run(debug=True)
```

## 10. Summary

This demo API for Village Pay's Siri integration will:

- Accept multi-turn conversation context
- Use an LLM to generate dummy SQL and a friendly response template
- Indicate via a conversation status whether Siri should continue asking questions
- Return a final JSON response for Siri to speak, enabling a natural, context-aware conversation with Village Pay's users

This PRD outlines both the functional and non-functional requirements for building the demo API. Future iterations would include real database integration, advanced error handling, and security measures.
