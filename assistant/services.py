import os
import google.generativeai as genai
from rooms.models import Room

# Налаштування API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def list_rooms(min_price=None, max_price=None, rooms=None):
    """Пошук кімнат у базі даних."""
    queryset = Room.objects.filter(is_available=True)
    if min_price: queryset = queryset.filter(price__gte=min_price)
    if max_price: queryset = queryset.filter(price__lte=max_price)
    if rooms: queryset = queryset.filter(rooms=rooms)
    
    return [{
        "id": r.id, "title": r.title, "price": float(r.price),
        "address": r.address, "rooms": r.rooms
    } for r in queryset[:10]]

def get_room_details(room_id):
    """Деталі конкретної кімнати."""
    try:
        r = Room.objects.get(id=room_id)
        return {
            "title": r.title, "price": float(r.price), "address": r.address,
            "description": r.description, "rooms": r.rooms, "area": r.area
        }
    except Room.DoesNotExist:
        return {"error": "Кімнату не знайдено"}

model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    tools=[list_rooms, get_room_details],
    system_instruction="Ти — AI-помічник Roosh-Rent. Допомагай користувачам шукати житло. Відповідай українською."
)

def ask_ai(user_query, history=None):
    chat = model.start_chat(history=history, enable_automatic_function_calling=True)
    response = chat.send_message(user_query)
    return response.text, chat.history
