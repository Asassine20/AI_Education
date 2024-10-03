from .auth_views import (
    login_view, 
    logout_view, 
    signup_view, 
    school_signup_view
)

from .teacher_dashboard_views import (
    dashboard, 
    add_class, 
    course_page, 
    students_enrolled, 
    student_questions, 
    messages_list, 
    delete_message, 
    create_message, 
    download_syllabus, 
    preview_syllabus, 
    create_assignment, 
    assignments_list,
    assignment_page,
    add_questions_and_choices,
)

from .question_views import (
    ask_question, 
    upload_materials, 
    view_questions
)

from .other_views import (
    home, 
    landing_page, 
    contact_view,
    profile_image_upload_view
)

from .student_dashboard_views import (
    student_dashboard
)
from .file_views import (
    file_upload_view, 
    file_download_view, 
    file_edit_view, 
    file_preview_view, 
    file_list_view
)
from .admin_views import (
    admin_dashboard, 
    university_logo_upload_view,
    display_logo
)
