from .models import UserAuthentication


def autheduser_context(request):
    try:
        user_authentication = UserAuthentication.objects.get(
            user__id = request.user.pk
            )
        print(
            'User authenticateion found:', user_authentication.user.username
            )
        return {
            'userauth': user_authentication
        }
    except UserAuthentication.DoesNotExist:
        return {}