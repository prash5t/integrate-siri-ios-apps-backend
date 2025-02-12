from flask import Blueprint, request, jsonify
from app.services.llm_service import LLMService
from app.utils.response_processor import ResponseProcessor

bp = Blueprint('voice_assistant', __name__)
llm_service = LLMService()
response_processor = ResponseProcessor()


@bp.route('/api/voice-assistant', methods=['POST'])
def voice_assistant():
    try:
        data = request.get_json()

        # Validate input
        if not data:
            return jsonify({"error": "No data provided"}), 400

        conversation_history = data.get("conversation_history", [])
        current_query = data.get("current_query", "")

        if not current_query:
            return jsonify({"error": "No query provided"}), 400

        print("conversation_history: ", conversation_history)
        print("current_query: ", current_query)

        # Generate LLM response
        llm_response = llm_service.generate_response(
            conversation_history,
            current_query
        )

        # Process response and return
        final_response = response_processor.process_llm_response(llm_response)
        return jsonify(final_response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
