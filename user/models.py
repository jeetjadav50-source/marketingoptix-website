from django.db import models

# STATE
class State(models.Model):
    stateid = models.AutoField(primary_key=True)
    statename = models.CharField(max_length=50)

    class Meta:
        db_table = 'user_state'

    def __str__(self):
        return self.statename


# CITY
class City(models.Model):
    cityid = models.AutoField(primary_key=True)
    cityname = models.CharField(max_length=50)
    stateid = models.ForeignKey(State, on_delete=models.CASCADE)

    class Meta:
        db_table = 'user_city'

    def __str__(self):
        return self.cityname


# CATEGORY
class Category(models.Model):
    catid = models.AutoField(primary_key=True)
    catname = models.CharField(max_length=50)

    class Meta:
        db_table = 'user_category'

    def __str__(self):
        return self.catname


# SERVICES
class Service(models.Model):
    serviceid = models.AutoField(primary_key=True)
    servicename = models.CharField(max_length=50)
    catid = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        db_table = 'user_services'

    def __str__(self):
        return self.servicename


# USER
class User(models.Model):
    USER_ROLES = (
        ('admin', 'Admin'),
        ('marketer', 'Marketer'),
        ('client', 'Client'),
    )
    userid = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=20)
    email = models.CharField(max_length=30)
    profilepic = models.ImageField(upload_to="images/")
    gender = models.CharField(max_length=10)
    dob = models.DateField()
    role = models.CharField(max_length=20, choices=USER_ROLES, default='client')
    
    # Marketer specific fields
    displayname = models.CharField(max_length=50, null=True, blank=True)
    displayimage = models.ImageField(upload_to="images/", null=True, blank=True)
    bio = models.TextField(max_length=200, null=True, blank=True)
    displayaddress = models.CharField(max_length=100, null=True, blank=True)
    displaycontact = models.CharField(max_length=20, null=True, blank=True)
    website = models.CharField(max_length=50, null=True, blank=True)
    
    # Client specific fields
    fullname = models.CharField(max_length=50, null=True, blank=True)
    cityid = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'user_user'

    def __str__(self):
        return f"{self.username}"




# PROJECT
class Project(models.Model):
    PROJECT_MODES = (
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('mix', 'Mix'),
    )
    projectid = models.AutoField(primary_key=True)
    userid = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    status = models.IntegerField(default=1) # 1: Active, 2: In-Progress, 3: Completed
    createdDT = models.DateTimeField(auto_now_add=True)
    budget = models.FloatField()
    mode = models.CharField(max_length=20, choices=PROJECT_MODES, default='online')

    class Meta:
        db_table = 'user_project'

    def __str__(self):
        return self.title


# PROJECT SERVICE
class ProjectService(models.Model):
    projectserviceid = models.AutoField(primary_key=True)
    projectid = models.ForeignKey(Project, on_delete=models.CASCADE)
    serviceid = models.ForeignKey(Service, on_delete=models.CASCADE)

    class Meta:
        db_table = 'user_projectservice'

    def __str__(self):
        return f"{self.projectid} - {self.serviceid}"


# QUOTATION
class Quotation(models.Model):
    quotationid = models.AutoField(primary_key=True)
    userid = models.ForeignKey(User, on_delete=models.CASCADE)
    projectid = models.ForeignKey(Project, on_delete=models.CASCADE)
    budget = models.FloatField()
    pdf = models.FileField(upload_to="pdfs/")
    description = models.TextField(max_length=200)
    status = models.CharField(max_length=20, default='pending') # pending, accepted, rejected
    addedDT = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_quotation'
        unique_together = ('userid', 'projectid')

    def __str__(self):
        return f"Quotation {self.quotationid}"


# REVIEW
class Review(models.Model):
    reviewid = models.AutoField(primary_key=True)
    marketer_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='marketer_reviews')
    client_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_reviews')
    projectid = models.ForeignKey(Project, on_delete=models.CASCADE)
    review = models.TextField(max_length=500)
    rating = models.IntegerField()
    reviewdate = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_review'
        unique_together = ('client_user', 'projectid')

    def __str__(self):
        return f"Review {self.reviewid}"


# MARKETER IMAGE
class UserImage(models.Model):
    userimageid = models.AutoField(primary_key=True)
    userid= models.ForeignKey(User, on_delete=models.CASCADE)
    imageurl = models.ImageField(upload_to="images/")

    class Meta:
        db_table = 'user_userimage'

    def __str__(self):
        return f"Image {self.userimageid}"


# SAVED PROJECT
class SavedProject(models.Model):
    saveid = models.AutoField(primary_key=True)
    userid = models.ForeignKey(User, on_delete=models.CASCADE)
    projectid = models.ForeignKey(Project, on_delete=models.CASCADE)

    class Meta:
        db_table = 'user_savedproject'

    def __str__(self):
        return f"Saved {self.saveid}"


# MESSAGE
class Message(models.Model):
    messageid = models.AutoField(primary_key=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_message'

    def __str__(self):
        return f"From {self.sender} to {self.receiver}"


# NOTIFICATION
class Notification(models.Model):
    notificationid = models.AutoField(primary_key=True)
    userid = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    link = models.CharField(max_length=255, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_notification'

    def __str__(self):
        return f"To {self.userid}: {self.content[:30]}..."


# USER LANGUAGE
class UserLanguage(models.Model):
    userlanguageid = models.AutoField(primary_key=True)
    userid = models.ForeignKey(User, on_delete=models.CASCADE)
    language = models.CharField(max_length=50)

    class Meta:
        db_table = 'user_userlanguage'
        unique_together = ('userid', 'language')

    def __str__(self):
        return f"{self.userid.username} - {self.language}"