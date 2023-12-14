from django.urls import path
from painting.views.ExpertisesViews import *
from painting.views.RequestsViews import *
from painting.views.UsersViews import *

urlpatterns = [
    # Набор методов для услуг (Экспертиз)
    path('api/expertises/', get_expertises),  # GET
    path('api/expertises/<int:expertise_id>/', get_expertise_by_id),  # GET
    path('api/expertises/create/', create_expertise),  # POST
    path('api/expertises/<int:expertise_id>/update/', update_expertise),  # PUT
    path('api/expertises/<int:expertise_id>/delete/', delete_expertise),  # DELETE
    path('api/expertises/<int:expertise_id>/add_to_request/', add_expertise_to_request),  # POST

    # Набор методов для заявок (Занятий)
    path('api/requests/', get_requests),  # GET
    path('api/requests/<int:request_id>/', get_request_by_id),  # GET
    path('api/requests/<int:request_id>/update/', update_request),  # PUT
    path('api/requests/<int:request_id>/update_status_user/', update_request_user),  # PUT
    path('api/requests/<int:request_id>/update_status_admin/', update_request_admin),  # PUT
    path('api/requests/<int:request_id>/delete/', delete_request),  # DELETE
    path('api/requests/<int:request_id>/delete_expertise/<int:expertise_id>/', delete_expertise_from_request),  # DELETE

    path('api/private/requests/<int:request_id>/update_request/', update_request_internal),  # PUT

    # Аутентификация
    path("api/register/", register, name="register"),
    path("api/login/", login, name="login"),
    path("api/check/", check, name="check_access_token"),
    path("api/logout/", logout, name="logout"),
]
