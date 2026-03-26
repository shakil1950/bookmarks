from django.db import models
from django.contrib.auth.models import User
from django.db.models import UniqueConstraint
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
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


class Contact(models.Model):
    user_from = models.ForeignKey(User,
                                  related_name='rel_from_set',
                                  on_delete=models.CASCADE)
    user_to = models.ForeignKey(User,
                                related_name='rel_to_set',
                                on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['-created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user_from} follows {self.user_to}'





class Action(models.Model):
    user = models.ForeignKey('auth.User',
                             related_name='actions',
                             db_index=True,
                             on_delete=models.CASCADE)
    verb = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True,
                                   db_index=True)
    target_ct = models.ForeignKey(ContentType,
                                  blank=True,
                                  null=True,
                                  related_name='target_obj',
                                  on_delete=models.CASCADE)
    target_id = models.PositiveIntegerField(null=True,
                                            blank=True,
                                            db_index=True)
    target = GenericForeignKey('target_ct', 'target_id')

    class Meta:
        ordering = ('-created',)

user_model = get_user_model()
user_model.add_to_class('following',
                        models.ManyToManyField('self',
                                              through=Contact,
                                              related_name='followers',
                                              symmetrical=False))


