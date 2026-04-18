from rest_framework.decorators import api_view
from rest_framework.response import Response
from .services import ask_ai

@api_view(['POST'])
def ai_chat_view(request):
    user_query = request.data.get("message")
    if not user_query:
        return Response({"error": "No message provided"}, status=400)
    
    # Отримуємо історію з сесії (якщо є)
    history = request.session.get("ai_history", [])
    
    try:
        response_text, _ = ask_ai(user_query, history=history)
        return Response({"response": response_text})
    except Exception as e:
        print(f"AI Chat Error: {str(e)}") # Це виведе помилку в логи Docker
        return Response({"error": str(e)}, status=500)
