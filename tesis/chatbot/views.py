import json

from django.http import JsonResponse, Http404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from tesis.users.models import User
from tesis.chatbot.gemini_model import model
from tesis.chatbot.models import ChatMessage, Instruction
from .serializers import InstructionSerializer
from .utils import get_combined_instructions


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
        prompt = get_combined_instructions()
        return JsonResponse({"message": prompt}, status=200)

# tesis/chatbot/views.py


class InstructionListCreateAPIView(APIView):
    def get(self, request):
        instructions = Instruction.objects.all().order_by('created_at')
        for instruction in instructions:
            print(instruction.content)
        serializer = InstructionSerializer(instructions, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = InstructionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InstructionDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return Instruction.objects.get(pk=pk)
        except Instruction.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        instruction = self.get_object(pk)
        serializer = InstructionSerializer(instruction)
        return Response(serializer.data)

    def put(self, request, pk):
        instruction = self.get_object(pk)
        serializer = InstructionSerializer(instruction, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        instruction = self.get_object(pk)
        instruction.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)