from ai_app.models import SchoolUserProfile

def user_role(request):
    user = request.user
    if user.is_authenticated:  
        profile = SchoolUserProfile.objects.filter(user=request.user).first()
        if profile:
            university = profile.university
            return {
                'user_role': profile.role,
                'primary_color': university.primary_color,
                'secondary_color': university.secondary_color,
            }
    return {}
