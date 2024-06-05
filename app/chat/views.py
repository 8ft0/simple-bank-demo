from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt  # Import csrf_exempt
from .chat import handle_user_query

@csrf_exempt
def chat_view(request):
    if request.method == "POST":
        user_query = request.POST.get("query")
        user_id = request.user.id  # Assuming user is authenticated and user ID is available
        response = handle_user_query(user_query, user_id)
        return JsonResponse({"response": response})
    return JsonResponse({"error": "Invalid request method"}, status=400)

def chat_page_view(request):
    return render(request, 'chat.html')
