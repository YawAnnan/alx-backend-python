from datetime import datetime
import time
from django.http import HttpResponseForbidden, JsonResponse

# -------------------------------
# Middleware 1: Request Logging
# -------------------------------
class RequestLoggingMiddleware:
    """
    Logs every user request to requests.log with timestamp, user, and path.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', 'Anonymous')
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}\n"
        print(log_message)  # optional: print to console
        with open('requests.log', 'a') as log_file:
            log_file.write(log_message)

        response = self.get_response(request)
        return response


# -----------------------------------------
# Middleware 2: Restrict Access By Time
# -----------------------------------------
class RestrictAccessByTimeMiddleware:
    """
    Restricts chat access outside 6 AM – 9 PM.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Restrict only chat URLs
        if request.path.startswith('/chat/'):
            current_hour = datetime.now().hour
            if current_hour < 6 or current_hour >= 21:
                return HttpResponseForbidden(
                    "Chat is available only between 6 AM and 9 PM."
                )

        response = self.get_response(request)
        return response


# -----------------------------------------
# Middleware 3: Offensive Language / Rate Limiting
# -----------------------------------------
class OffensiveLanguageMiddleware:
    """
    Limits chat messages per IP: 5 messages per minute.
    """
    ip_requests = {}  # {ip: [timestamps]}

    LIMIT = 5
    WINDOW = 60  # seconds

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/chat/') and request.method == 'POST':
            ip = self.get_client_ip(request)
            now = time.time()

            if ip not in self.ip_requests:
                self.ip_requests[ip] = []

            # Keep timestamps only within the WINDOW
            self.ip_requests[ip] = [t for t in self.ip_requests[ip] if now - t < self.WINDOW]

            if len(self.ip_requests[ip]) >= self.LIMIT:
                return JsonResponse(
                    {"error": "Rate limit exceeded. You can send up to 5 messages per minute."},
                    status=429
                )

            self.ip_requests[ip].append(now)

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        """Get client IP from headers or REMOTE_ADDR."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RolePermissionMiddleware:
    """
    Middleware to enforce role-based permissions.
    Only allows access to admins or moderators for restricted actions.
    """

    # Define restricted paths where role check applies
    RESTRICTED_PATHS = [
        '/admin-action/',  # replace with actual restricted paths
        '/delete-message/',
        '/manage-users/',
    ]

    ALLOWED_ROLES = ['admin', 'moderator']

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only check restricted paths
        for path in self.RESTRICTED_PATHS:
            if request.path.startswith(path):
                user = getattr(request, 'user', None)

                # If user is not authenticated or role not allowed
                if not user or not hasattr(user, 'role') or user.role not in self.ALLOWED_ROLES:
                    return HttpResponseForbidden(
                        "You do not have permission to perform this action."
                    )

        response = self.get_response(request)
        return response
