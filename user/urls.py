from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('addproject/', views.addproject, name='addproject'),
    path('project-details/<int:pid>/', views.project_details, name='project_details'),
    path('logout/', views.logout, name='logout'),
    path('my-projects/', views.my_projects, name='my_projects'),
    path('my-quotations/', views.my_quotations, name='my_quotations'),
    path('profile/<int:uid>/', views.profile_view, name='profile'),
    path('accept-quotation/<int:qid>/', views.accept_quotation, name='accept_quotation'),
    path('checkout/<int:qid>/', views.checkout, name='checkout'),
    path('process-payment/<int:qid>/', views.process_payment, name='process_payment'),
    path('complete-project/<int:pid>/', views.complete_project, name='complete_project'),
    path('submit-review/', views.submit_review, name='submit_review'),
    path('toggle-save/<int:pid>/', views.toggle_save_project, name='toggle_save'),
    path('saved-projects/', views.saved_projects, name='saved_projects'),
    path('upload-portfolio/', views.upload_portfolio_image, name='upload_portfolio'),
    path('delete-portfolio/<int:imgid>/', views.delete_portfolio_image, name='delete_portfolio'),
    path('inbox/', views.inbox, name='inbox'),
    path('chat/<int:other_uid>/', views.chat_thread, name='chat_thread'),
    path('notifications/', views.notifications_list, name='notifications'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('add-language/', views.add_language, name='add_language'),
    path('delete-language/<int:lid>/', views.delete_language, name='delete_language'),
    
    # Corporate Pages
    path('about-us/', views.about_us, name='about_us'),
    path('services/', views.services, name='services'),
    path('blog/', views.blog, name='blog'),
    path('contact/', views.contact, name='contact'),
    path('help-support/', views.help_support, name='help_support'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-service/', views.terms_service, name='terms_service'),
    path('faq/', views.faq, name='faq'),
]