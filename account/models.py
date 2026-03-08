from django.db import models
from django.contrib.auth.models import User
from django.db.models import UniqueConstraint
# Create your models here.

GENDER={
    ('male','Male'),
    ('female','Female'),
    ('other','Other'),
}
def user_directory_path(instance, filename):
    # ফাইলটি 'user_<username>/<filename>' এই ফরম্যাটে সেভ হবে
    # উদাহরণ: user_shuvo/my_photo.jpg
    return 'profile_pics/user_{0}/{1}'.format(instance.user.username, filename)

class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    bio=models.TextField(blank=True)
    avater=models.ImageField(default='default.jpg', upload_to=user_directory_path)
    mob=models.CharField(max_length=12,default='011111111111')
    gender=models.CharField(choices=GENDER,max_length=20,blank=True,null=True)
    dob=models.DateField(blank=True,null=True)
    created_at=models.DateTimeField(auto_now=True)
    updated_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} Profile'


class Meta:
        constraints = [
            UniqueConstraint(fields=['email'], name='unique_user_email')
        ]