
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class DebugSocialAccountAdapter(DefaultSocialAccountAdapter):
    def authentication_error(
        self,
        request,
        provider_id,
        error=None,
        exception=None,
        extra_context=None,
    ):
        raise exception or Exception("Unknown social authentication error")
