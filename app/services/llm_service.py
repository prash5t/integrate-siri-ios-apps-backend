from openai import OpenAI
from app.config.config import Config
import json
import os


class LLMService:
    def __init__(self):
        try:
            # Set the API key in environment variable as OpenAI client looks for it there
            os.environ["OPENAI_API_KEY"] = Config.OPENAI_API_KEY
            if not Config.OPENAI_API_KEY:
                raise ValueError(
                    "OpenAI API key is not set in environment variables")
            self.client = OpenAI()  # Initialize without explicit api_key parameter
            self.model = Config.OPENAI_MODEL
            print("OpenAI client initialized successfully")  # Debug log
        except Exception as e:
            print(f"Error initializing OpenAI client: {str(e)}")
            raise

    def generate_response(self, conversation_history, current_query):
        """
        Generate a response using the OpenAI API
        """
        prompt = self._construct_prompt(conversation_history, current_query)
        print(f"Using model: {self.model}")  # Debug log
        print("Sending request to OpenAI...")  # Debug log

        try:
            # Add timeout and max retries
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": prompt}],
                temperature=0.7,
                max_tokens=500,
                timeout=30  # 30 seconds timeout
            )
            print("Received response from OpenAI")  # Debug log

            llm_output = response.choices[0].message.content
            print(f"Raw LLM output: {llm_output}")  # Debug log

            return json.loads(llm_output)

        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            raise Exception(f"Invalid JSON response from LLM: {str(e)}")
        except Exception as e:
            print(f"OpenAI API error: {str(e)}")
            if "connect" in str(e).lower():
                raise Exception(
                    "Unable to connect to OpenAI API. Please check your internet connection and try again.")
            raise Exception(f"Error generating LLM response: {str(e)}")

    def _construct_prompt(self, conversation_history, current_query):
        """
        Construct the prompt for the LLM
        """
        conversation_text = "\n".join(
            [f"{msg['role'].capitalize()}: {msg['content']}"
             for msg in conversation_history]
        )

        return f"""You are a Village Pay voice assistant. Your job is to analyze the following conversation history and current query and generate a JSON response in the following format:
{{
  "sql_query": "<SQL_QUERY_OR_NULL>",
  "siri_response_template": "<COMPLETE_RESPONSE_WITH_DUMMY_DATA>",
  "continueConversation": true | false
}}

Village Pay is a digital wallet app that lets users load money, transfer funds, check balances, pay utility bills, book flights, purchase movie tickets, and more.

IMPORTANT: Instead of using placeholders, provide complete responses with realistic dummy data. For example:
- Say "Your balance is ₹1,000"
- Say "Transferred ₹50 to Suraj Shrestha"
- For bills, use dummy amounts like "₹750 for electricity bill"
- For movie tickets, use dummy prices like "₹350 per ticket"
- For flight bookings, use dummy flight numbers like "NK455"

Conversation History:
{conversation_text}

Current Query: {current_query}

Please provide your response in JSON format only. Make sure the response is valid JSON.
For money transfer queries, if all details (recipient and amount) are provided, set continueConversation to false.
For balance queries, always set continueConversation to false.
For incomplete queries, set continueConversation to true and ask for missing information.
"""
