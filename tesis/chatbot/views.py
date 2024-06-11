import json
from django.http import JsonResponse
from rest_framework import viewsets

from tesis.chatbot.gemini_model import model, prompt


class ChatbotView(viewsets.ViewSet):

    def post(self, request, *args, **kwargs):
        # Parse JSON data
        data = json.loads(request.body)
        user_input = data.get("input")

        if not user_input:
            return JsonResponse({"error": "Missing input field."}, status=400)

        chat_session = model.start_chat(history=[])
        response = chat_session.send_message(user_input)
        return JsonResponse({"response": response.text}, status=200)

    def get(self, request, *args, **kwargs):
        return JsonResponse({"message": prompt}, status=200)
