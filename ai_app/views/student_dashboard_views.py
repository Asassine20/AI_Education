from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from ai_app.models import SchoolUserProfile, ClassRoom

@login_required
def student_dashboard(request):
    profile = get_object_or_404(SchoolUserProfile, user=request.user, role='student')
    if request.method == 'POST':
        room_code = request.POST['room_code']
        try:
            classroom = ClassRoom.objects.get(room_code=room_code)
            profile.classes.add(classroom)
            return redirect('student_dashboard')
        except ClassRoom.DoesNotExist:
            return render(request, 'ai_app/dashboards/student/student_dashboard.html', {
                'error': 'Invalid class code',
                'classes': classes
            })

    classes = profile.classes.all()
    return render(request, 'ai_app/dashboards/student/student_dashboard.html', {'classes': classes})