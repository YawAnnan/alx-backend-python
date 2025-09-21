from django.http import JsonResponse

def index(request):
    return JsonResponse({"message": "Messaging app API is running 🚀"})
