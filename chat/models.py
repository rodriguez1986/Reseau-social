from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings

#Modèle utilisateur personnalisé avec des champs supplémentaires
class CustomUser(AbstractUser):
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_artist = models.BooleanField(default=False)
    is_freelancer = models.BooleanField(default=False)
    is_gamer = models.BooleanField(default=False)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following')
    interests = models.TextField(blank=True, null=True)


# Modèle de publication
class Post(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    media = models.FileField(upload_to='post_media/', blank=True, null=True)  #image/vidéo
    created_at = models.DateTimeField(default=timezone.now)
    likes = models.ManyToManyField(CustomUser, related_name='liked_posts', blank=True)


# Modèle de commentaire
class Comment(models.Model):
    # Référence à la publication à laquelle appartient ce commentaire
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    # Référence à l'utilisateur qui a écrit le commentaire
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    # Le texte du commentaire
    content = models.TextField()
    # Date de création du commentaire
    created_at = models.DateTimeField(default=timezone.now)

# Modèle de notification
class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_notifications', null=True,
                               blank=True)  # l’émetteur
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)  # 🔥 Ajout ici
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    seen = models.BooleanField(default=False)

# Modèle de messagerie privée
class Message(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    seen = models.BooleanField(default=False)

# Modèle de service
class Service(models.Model):
    CATEGORY_CHOICES = [
        ('design', 'Design'),
        ('music', 'Musique'),
        ('dev', 'Développement'),
        ('video', 'Vidéo'),
        ('freelance', 'Freelance'),
        ('art', 'Œuvre / Art'),
        ('service', 'Service Divers'),
        ('gaming', 'Gaming'),
        ('multiplayer', 'Jeu Multijoueur'),
        ('solo', 'Jeu Solo'),
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='post_services')
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# Modèle de gaming
class GamingClip(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='post_gaming')
    title = models.CharField(max_length=100)
    video_url = models.URLField(max_length=500, blank=False, null=False)
    game = models.CharField(max_length=100)
    posted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

#Upload du jeu par le deveppeur
# models.py

class GameUpload(models.Model):
    GAME_MODE_CHOICES = [
        ('solo', 'Jeu Solo'),
        ('multiplayer', 'Jeu Multijoueur'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    developer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='upload_game')
    game_file = models.FileField(upload_to="uploaded_games/")
    thumbnail = models.ImageField(upload_to="thumbnails/", blank=True, null=True)
    views = models.PositiveIntegerField(default=0)
    players = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    game_mode = models.CharField(max_length=20, choices=GAME_MODE_CHOICES, default='solo')
    date_posted = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.title

