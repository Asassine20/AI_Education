from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from ai_app.models import Question, CourseMaterial, ClassRoom
from openai import OpenAI
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)
@csrf_exempt
def ask_question(request):
    if request.method == 'POST':
        topic = request.POST.get('topic')
        classroom_id = request.POST.get('classroom_id')  # Get the classroom ID from the form
        user = request.user
        
        # Ensure the classroom exists
        classroom = get_object_or_404(ClassRoom, id=classroom_id)

        try:
            # Use the ChatCompletion API for the AI response (not saving it in the DB)
            response = client.chat.completions.create(
                model="gpt-4o-mini",  
                messages=[
                    {"role": "system", "content": "You are an educational assistant."},
                    {"role": "user", "content": f"Explain the topic '{topic}' in detail for a student to understand."}
                ],
                max_tokens=500,
                temperature=0.7
            )

            ai_response = response.choices[0].message.content  # Extract the AI's response

            # Save only the question (topic) in the DB
            Question.objects.create(user=user, topic=topic, classroom=classroom)

            return JsonResponse({'response': ai_response})  # Return AI response, but don't save it

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return render(request, 'ai_app/questions/ask_question.html')



@login_required
def upload_materials(request):
    if request.method == 'POST':
        course_name = request.POST.get('course_name')
        material = request.POST.get('material')
        professor = request.user
        CourseMaterial.objects.create(professor=professor, course_name=course_name, material=material)
        return JsonResponse({'message': 'Course material uploaded successfully'})

    return render(request, 'ai_app/questions/upload_materials.html')


@login_required
def view_questions(request):
    questions = Question.objects.all().order_by('-timestamp')
    return render(request, 'ai_app/questions/view_questions.html', {'questions': questions})
