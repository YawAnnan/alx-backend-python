from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

User = get_user_model()


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_user(request):
    """
    Allow an authenticated user to delete their account.
    """
    user = request.user
    username = user.username
    user.delete()
    return Response(
        {"detail": f"User {username} and related data deleted successfully."},
        status=status.HTTP_204_NO_CONTENT
    )