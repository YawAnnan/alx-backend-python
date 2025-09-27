from datetime import datetime

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
