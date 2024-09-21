from ai_app.models import SchoolUserProfile

def user_role(request):
    user = request.user
    if user.is_authenticated:  # Remove the parentheses
        profile = SchoolUserProfile.objects.filter(user=request.user).first()
        if profile:
            return {'user_role': profile.role}
    return {}
