# Integrating Voice Commands with iOS Apps Using Siri

Voice commands become especially valuable when users can't physically interact with their phones, such as while cooking, exercising, or driving. By combining Siri integration with App Shortcuts, App Intents, and a backend that converts natural language to SQL queries, you can enable users to perform various tasks hands-free, including:

- Checking account balances
- Ordering food
- Tracking items
- Booking movie tickets
- Accessing health data

## App-Side Implementation

### Defining App Shortcuts

First, create shortcut phrases that Siri can recognize using Swift's AppShortcutsProvider:

```swift
import AppIntents

struct AllAppShortcuts: AppShortcutsProvider {
    static var appShortcuts: [AppShortcut] {
        return [
            AppShortcut(
                intent: TalkToVillagerIntent(),
                phrases: [
                    "Talk to villager in \(.applicationName)",
                    "Call villager in \(.applicationName)",
                    "Open villager in \(.applicationName)",
                    "Open \(.applicationName)"
                ]
            ),
            // Additional shortcuts for balance checking, loading funds, etc.
        ]
    }
}
```

### Implementing App Intents

Create intents to handle user voice commands. This example shows a TalkToVillagerIntent that manages conversation history for multi-turn interactions:

```swift
import AppIntents
import SwiftUI

struct TalkToVillagerIntent: AppIntent {
    static var title: LocalizedStringResource = "Voice Assistant"
    static var description = IntentDescription("Access app features directly from Siri")
    static var openAppWhenRun: Bool = false

    @Parameter(title: "Query", description: "What do you want to do?")
    var userQuery: String?

    @MainActor
    func perform() async throws -> some IntentResult & ProvidesDialog {
        // Validate user login
        guard SharedPrefsHelper.shared.getLoggedInVillager() != nil else {
            let errMsg = "Account not found. Please log in to the app first."
            throw $userQuery.needsValueError(IntentDialog(full: errMsg, supporting: errMsg))
        }

        // Handle conversation history
        var conversationHistory = SharedPrefsHelper.shared.getVoiceConversation()
        conversationHistory.append(VoiceMessageModel(role: "user", content: userQuery ?? ""))

        let payload = VoiceAssistantPayloadModel(
            conversationHistory: conversationHistory,
            currentQuery: userQuery ?? ""
        )

        // Make API call
        let repository = DataRepository()
        guard let assistantResponse = await repository.getVoiceAssistanceForSiri(voiceAssistantPayloadModel: payload) else {
            let errMsg = "Voice Assistant Feature is not working at the moment."
            throw $userQuery.needsValueError(IntentDialog(full: errMsg, supporting: errMsg))
        }

        // Handle response
        if assistantResponse.continueConversation {
            conversationHistory.append(VoiceMessageModel(role: "assistant", content: assistantResponse.sentenceSiriShouldSay))
            SharedPrefsHelper.shared.saveVoiceConversation(messages: conversationHistory)
            throw $userQuery.needsValueError(
                IntentDialog(full: assistantResponse.sentenceSiriShouldSay, supporting: assistantResponse.sentenceSiriShouldSay)
            )
        } else {
            SharedPrefsHelper.shared.clearVoiceConversation()
            return .result(dialog: IntentDialog(full: assistantResponse.sentenceSiriShouldSay, supporting: assistantResponse.sentenceSiriShouldSay))
        }
    }
}
```

### Backend Communication

Define a payload model to send user queries and conversation history to the backend:

```swift
struct VoiceAssistantPayloadModel: Codable {
    let conversationHistory: [VoiceMessageModel]
    let currentQuery: String

    enum CodingKeys: String, CodingKey {
        case conversationHistory = "conversation_history"
        case currentQuery = "current_query"
    }
}
```

## Backend Implementation

### Creating the Endpoint

Set up an endpoint to process voice commands using Flask:

```python
from flask import Blueprint, request, jsonify
from app.services.llm_service import LLMService
from app.utils.response_processor import ResponseProcessor

bp = Blueprint('voice_assistant', __name__)
llm_service = LLMService()
response_processor = ResponseProcessor()

@bp.route('/api/voice-assistant', methods=['POST'])
def voice_assistant():
    data = request.get_json()
    conversation_history = data.get("conversation_history", [])
    current_query = data.get("current_query", "")

    llm_response = llm_service.generate_response(conversation_history, current_query)
    final_response = response_processor.process_llm_response(llm_response)
    return jsonify(final_response)
```

### LLM Integration

Implement the LLM service to generate SQL queries and natural language responses:

```python
class LLMService:
    def generate_response(self, conversation_history, current_query):
        prompt = self._construct_prompt(conversation_history, current_query)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": prompt}],
            temperature=0.7,
            max_tokens=500,
            timeout=30
        )
        llm_output = response.choices[0].message.content
        return json.loads(llm_output)

    def _construct_prompt(self, conversation_history, current_query):
        conversation_text = "\n".join(
            [f"{msg['role'].capitalize()}: {msg['content']}" for msg in conversation_history]
        )
        return f"""You are a Village Pay voice assistant. Your job is to analyze the following conversation history and current query and generate a JSON response in the following format:
{{
  "sql_query": "<SQL_QUERY_OR_NULL>",
  "siri_response_template": "<COMPLETE_RESPONSE_WITH_DUMMY_DATA>",
  "continueConversation": true | false
}}

Village Pay is a digital wallet app that lets users load money, transfer funds, check balances, pay utility bills, book flights, purchase movie tickets, and more.

Conversation History:
{conversation_text}

Current Query: {current_query}

Please provide your response in valid JSON with complete answers. If the query is incomplete, set continueConversation to true and ask for missing details.
"""
```

### Response Processing

Create a response processor to format the LLM output for Siri:

```python
class ResponseProcessor:
    @staticmethod
    def process_llm_response(llm_response):
        siri_response = llm_response.get("siri_response_template", "")
        continue_conversation = llm_response.get("continueConversation", True)
        return {
            "sentenceSiriShouldSay": siri_response,
            "continueConversation": continue_conversation
        }
```

## Conclusion

This integration of App Shortcuts, App Intents, and an LLM-powered backend creates a seamless voice-driven experience. Users can perform app actions without opening the app, with the system handling natural language processing and multi-turn conversations. This approach is particularly valuable for:

- Fintech applications
- E-commerce platforms
- Travel services
- Any app requiring hands-free interaction
