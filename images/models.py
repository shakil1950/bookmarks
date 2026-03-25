from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import redis
from django.conf import settings

# রেডিস কানেকশন
r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
from django.utils.text import slugify
def user_directory_path(instance, filename):
    # ফাইলটি 'user_<id>/<filename>' এই ফরম্যাটে আপলোড হবে
    # উদাহরণ: user_shakil/my_photo.jpg
    return 'user_{0}/{1}'.format(instance.user.username, filename)
class Image(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='image_create')
    title=models.CharField(max_length=200)
    slug=models.SlugField(max_length=200,blank=True)
    url=models.URLField(max_length=2000)
    image=models.ImageField(upload_to=user_directory_path)
    description=models.CharField(max_length=200,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    users_like = models.ManyToManyField(
        User,
        related_name='images_liked',
        blank=True
        )

    class Meta:
        
        indexes = [
        models.Index(fields=['-created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            super().save(*args, **kwargs)

    def get_absolute_url(self):
        # এটি 'images:detail' নামে আপনার তৈরি করা URL-এ পাঠিয়ে দিবে
        return reverse('detail', args=[self.id, self.slug])
    
    @property
    def total_views(self):
        # রেডিস থেকে সরাসরি ভিউ সংখ্যা নিয়ে আসবে
        v = r.get(f'image:{self.id}:views')
        return int(v) if v else 0

class Comment(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments_created')
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'Comment by {self.user} on {self.image}'