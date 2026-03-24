from django.contrib import admin
from .models import (
    State, City, Category, Service, User, Project, 
    ProjectService, Quotation, Review, UserImage, 
    SavedProject, Message, Notification, UserLanguage
)

admin.site.register(State)
admin.site.register(City)
admin.site.register(Category)
admin.site.register(Service)
admin.site.register(User)
admin.site.register(Project)
admin.site.register(ProjectService)
admin.site.register(Quotation)
admin.site.register(Review)
admin.site.register(UserImage)
admin.site.register(SavedProject)
admin.site.register(Message)
admin.site.register(Notification)
admin.site.register(UserLanguage)