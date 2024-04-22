from django.urls import path
from .views import PhoneNumberAuthView, UserProfileView, AuthCodeCheckView, UserDetailView

urlpatterns = [
    path('auth/', PhoneNumberAuthView.as_view(), name='phone_auth'),
    path('users/<int:user_id>/', UserProfileView.as_view(), name='users_numbers'),
    path('user-profile/<int:pk>/', UserDetailView.as_view(), name='user_profile'),
    path('auth-code-check/', AuthCodeCheckView.as_view(), name='auth-code-check'),
]