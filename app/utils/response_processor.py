class ResponseProcessor:
    @staticmethod
    def process_llm_response(llm_response):
        """
        Process the LLM response. The response should already contain natural language
        with dummy data from the LLM itself.
        """
        siri_response = llm_response.get("siri_response_template", "")
        continue_conversation = llm_response.get("continueConversation", True)

        return {
            "sentenceSiriShouldSay": siri_response,
            "continueConversation": continue_conversation
        }
