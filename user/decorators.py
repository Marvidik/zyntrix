from rest_framework.response import Response
from rest_framework import status
from super.models import Settings
from .models import UserProfile

def kyc_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        try:
            global_settings = Settings.objects.first()
            user_profile = UserProfile.objects.get(user=request.user)
        except (Settings.DoesNotExist, UserProfile.DoesNotExist):
            return Response(
                {"detail": "Settings or user profile not found."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if global_settings and global_settings.kyc:
            if not user_profile.kyc:
                return Response(
                    {"detail": "You must complete KYC to access this feature."},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        return view_func(request, *args, **kwargs)

    return _wrapped_view
