import json

from django.http import JsonResponse

from rest_framework.views import APIView

from tesis.users.models import User
from tesis.chatbot.gemini_model import model, prompt
from tesis.chatbot.models import ChatMessage


class ChatbotView(APIView):

    def post(self, request, *args, **kwargs):
        # Parse JSON data
        data = json.loads(request.body)
        user_input = data.get("input")

        if not user_input:
            return JsonResponse({"error": "Missing input field."}, status=400)

        history = []
        if hasattr(request, 'usuario'):
            user = User.objects.get(id=request.usuario.id)

            # Retrieve all messages linked to the user
            messages = ChatMessage.objects.filter(user=user).order_by('timestamp')

            # Structure the messages in the desired format
            for message in messages:
                history.append({
                    "role": message.role,
                    "parts": [message.content],
                })

        chat_session = model.start_chat(history=history)

        response = chat_session.send_message(user_input)

        if hasattr(request, 'usuario'):
            user = User.objects.get(id=request.usuario.id)

            # Guardar el mensaje del usuario en la base de datos
            ChatMessage.objects.create(user=user, role='user', content=user_input)

            # Guardar la respuesta del modelo en la base de datos
            ChatMessage.objects.create(user=user, role='model', content=response.text)

        return JsonResponse({"response": response.text}, status=200)

    def get(self, request, *args, **kwargs):
        return JsonResponse({"message": prompt}, status=200)
