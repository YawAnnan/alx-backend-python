from datetime import datetime
from django.http import HttpResponseForbidden
class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else "Anonymous"
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"

        # Print to console for debugging
        print("LOGGED REQUEST:", log_message)

        # Append to requests.log
        try:
            with open('requests.log', 'a') as f:
                f.write(log_message + '\n')
        except Exception as e:
            print("Failed to write to requests.log:", e)

        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only restrict the chat app URLs
        if request.path.startswith('/chat/'):  # adjust path if needed
            current_hour = datetime.now().hour
            # Deny access if outside 6 AM–9 PM
            if current_hour < 6 or current_hour >= 21:
                return HttpResponseForbidden("Chat is available only between 6 AM and 9 PM.")

        response = self.get_response(request)
        return response
