from django.urls import path, reverse_lazy
from django.contrib.auth.views import PasswordChangeView, PasswordResetConfirmView, \
    PasswordResetCompleteView, PasswordResetDoneView

from .views import RegistrationView, SendPasswordResetMail, UserLoginView, ProfileUpdateView, ProfileView, \
    DeactivateUserView, WalletView, UserLogoutView, UserRewardsView, RewardsTransactionView

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(),
         name='logout'),
    path('change-password/', PasswordChangeView.as_view(template_name='users/change_password.html',
                                                        success_url=reverse_lazy('home')), name='change_password'),
    path('password-reset/', SendPasswordResetMail.as_view(),
         name='password_reset'),
    path('password-reset/done/',
         PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),
    path('profile/<str:username>/', ProfileView.as_view(), name='profile'),
    path('profile/<int:pk>/update/',
         ProfileUpdateView.as_view(), name='profile_update'),
    path('profile-delete/', DeactivateUserView.as_view(), name='delete_profile'),
    path('wallet/', WalletView.as_view(), name='wallet'),
    path('rewards/<str:username>/', UserRewardsView.as_view(), name='rewards'),
    path('rewards-transaction/<str:username>/<int:pk>/', RewardsTransactionView.as_view(), name='rewards_transaction')
]
