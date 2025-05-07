from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import CustomUser, Post, Comment, Notification, Message, Service, GamingClip, GameUpload
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.contrib.auth import authenticate, login as auth_login,get_user_model, logout
from django.core.serializers import serialize
from django.utils.timezone import now
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Q
from .forms import CustomUserCreationForm
import os
import openai
import json

#Fonction qui permet de s'enregistrer ou de creer un compte

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, "Votre compte a été créé avec succès !")
            return redirect('home')  # Redirige vers la page d'accueil après login
        else:
            messages.error(request, "Erreur dans le formulaire. Veuillez vérifier vos informations.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'signup.html', {'form': form})



#Fonction qui permet de se connecter
def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()

    return render(request, 'index.html', {'form': form})


#Fonction qui affiche la page d'accueil avec les publications des evenements
@login_required(login_url='connexion')
def home(request):
    unread_notifications = Notification.objects.filter(user=request.user, seen=False).count()
    posts = Post.objects.all()
    for post in posts:
        post.is_liked = request.user in post.likes.all()
        if post.media:
            # Vérification du type de fichier basé sur l'extension
            if post.media.name.endswith(('.mp4', '.avi', '.mov')):
                post.is_video = True
            else:
                post.is_video = False
        else:
            post.is_video = False

    return render(request, 'home.html', {'posts': posts,'unread_notifications': unread_notifications})


#Fonction qui affiche le profile
@login_required(login_url='connexion')
def profile(request, username):
    user = get_object_or_404(CustomUser, username=username)

    return render(request, 'profile.html', {'user': user})

# Envoyer un message
def send_messages(request):
    # Récupère tous les utilisateurs sauf l'utilisateur connecté
    users = CustomUser.objects.exclude(id=request.user.id)
    return render(request, 'send_message.html', {'users': users})

# Afficher les messages reçus par l'utilisateur
@login_required(login_url='connexion')
def inbox(request):
    user = request.user
    # Récupérer les messages reçus par l'utilisateur, triés par date (les plus récents d'abord)
    received_messages = Message.objects.filter(receiver=user).order_by('-timestamp')

    # Renvoyer les messages reçus à la template 'inbox.html'
    return render(request, 'inbox.html', { 'received_messages': received_messages})


#Fonction pour publier un post
def post(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        media = request.FILES.get('media')  # image ou vidéo

        if content or media:
            posts=Post.objects.create(author=request.user, content=content, media=media)
            return redirect('home')

    return render(request, 'post.html')

@login_required(login_url='connexion')
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    if user in post.likes.all():
        post.likes.remove(user)
        liked = False
    else:
        post.likes.add(user)
        liked = True

    return JsonResponse({
        'liked': liked,
        'like_count': post.likes.count()
    })


# Vue pour afficher un post spécifique avec ses commentaires
@login_required(login_url='connexion')
def load_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.select_related('author').order_by('created_at')  # Accès correct

    if request.method == 'GET':
        data = []
        for comment in comments:
            data.append({
                "username": comment.author.username,
                "author_avatar": getattr(comment.author.profile_picture, 'avatar.url', ''),  # Sécurisé
                "content": comment.content,
                "created_at": comment.created_at.strftime("%d %B %Y, %H:%M"),
            })
        return JsonResponse({"comments": data})

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)


#Fonction qui affiche tous les utilisateurs
@login_required(login_url='connexion')
def get_all_users(request):
    User = get_user_model()
    users = User.objects.exclude(id=request.user.id)
    data = [
        {
            "username": user.username,
            "picture": user.profile_picture.url if user.profile_picture else "/static/default.png"
        }
        for user in users
    ]
    return JsonResponse({"users": data})


#Fonction qui s'occupe d'afficher l'hitorique de message
@login_required(login_url='connexion')
def chat_history(request, username):
    user = request.user
    other_user = CustomUser.objects.get(username=username)

    # Récupérer les messages échangés entre les deux utilisateurs
    messages = Message.objects.filter(
        (Q(sender=user) & Q(receiver=other_user)) |
        (Q(sender=other_user) & Q(receiver=user))
    ).order_by('timestamp')

    return render(request, 'send_message.html', {
        'messages': messages,
        'other_user': other_user
    })

#Fonction qui filtre les services dans marketplace
@login_required(login_url='connexion')
def filter_services(request, category):
    services = Service.objects.filter(category=category).order_by('-created_at')
    data = {
        'services': [
            {
                'title': service.title,
                'description': service.description,
                'price': str(service.price),
                'category': service.get_category_display(),
            }
            for service in services
        ]
    }
    return JsonResponse(data)

#Fonction qui affiche toutes les services
@login_required(login_url='connexion')
def marketplace_view(request):
    services = Service.objects.all().order_by('-created_at')
    return render(request, 'marketplace.html', {'services': services})


#Fonction qui affiche tous les jeux
@login_required(login_url='connexion')
def gaming_view(request):
    clips = GamingClip.objects.all().order_by('-posted_at')
    solo_games = GameUpload.objects.filter(game_mode='solo').order_by('-date_posted')
    multiplayer_games = GameUpload.objects.filter(game_mode='multiplayer').order_by('-date_posted')

    context = {
        'clips': clips,
        'solo_games': solo_games,
        'multiplayer_games': multiplayer_games,
    }
    return render(request, 'gaming.html', context)



#Fonction qui permet à un devoppeur de charger son projet en zip après developpemt
@login_required(login_url='connexion')
def upload_game(request):
    if request.method == 'POST':
        form = GameUploadForm(request.POST, request.FILES)
        if form.is_valid():
            game = form.save(commit=False)
            game.developer = request.user
            game.save()
            return redirect('game-detail', game_id=game.id)
    else:
        form = gameUploadForm()
    return render(request, 'games/upload.html', {'form': form})

#Fonction qui verifie le type de fichier fourni
@login_required(login_url='connexion')
def clean_game_file(self):
    game_file = self.cleaned_data.get('game_file')
    if game_file:
        if not game_file.name.endswith(('.zip', '.exe', '.apk')):
                raise forms.ValidationError("Le fichier doit être un .zip, .exe, .apk")
    return game_file


#Fonction qui affiche les détail du jeux
@login_required(login_url='connexion')
def game_detail(request, game_id):
    game = GameUpload.objects.get(id=game_id)
    game.views += 1
    game.save()
    return render(request, 'games/detail.html', {'game': game})


#Fonction qui gère note bot via GPT-4
@login_required(login_url='connexion')
@csrf_exempt
def gpt_chat_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message", "")

        try:
            openai.api_key = "TON_CLE_OPENAI"  # remplace par ta vraie clé API
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Tu es un assistant pour une plateforme de gaming, d’art et de freelancing."},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=300
            )

            bot_message = response['choices'][0]['message']['content']
            return JsonResponse({"reply": bot_message})

        except Exception as e:
            return JsonResponse({"reply": "Erreur de traitement : " + str(e)}, status=500)




# Envoi de notifications en temps réel
def send_notification(user, message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user_{user.id}',
        {
            'type': 'send_notification',
            'message': message
        }
    )
# Chatbot AI
def chatbot_response(request):
    user_input = request.GET.get('message', '')
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "Tu es un assistant utile."},
                  {"role": "user", "content": user_input}]
    )
    return JsonResponse({"response": response["choices"][0]["message"]["content"]})



def notifications(request):
    user = request.user
    notifications = Notification.objects.filter(user=user).order_by('-created_at')
    # Marquer comme vues
    notifications.filter(seen=False).update(seen=True)
    return render(request, 'notification.html', {'notifications': notifications})

def unread_notifications_count(request):
    if request.user.is_authenticated:
        count = request.user.notifications.filter(seen=False).count()
        return JsonResponse({'unread_count': count})
    else:
        return JsonResponse({'unread_count': 0})

def mark_notifications_as_read(request):
    if request.user.is_authenticated:
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'unauthorized'}, status=401)

def get_notifications(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:20]
        data = [
            {
                'username': n.sender.username,
                'sender_avatar': n.sender.profile_picture.url,
                'message': n.message,
                'post_id': n.post.id if n.post else None,
                'created_at': n.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'is_read': n.seen,
            }
            for n in notifications
        ]
        return JsonResponse({'notifications': data})
    return JsonResponse({'error': 'Non authentifié'}, status=403)

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post).select_related('author').order_by('-created_at')
    return render(request, 'detailPost.html', {'post': post, 'comments': comments})



def extract_keywords(interests):
    try:
        items = json.loads(interests)
        if isinstance(items, list):
            return " ".join(
                item.get("value", "").strip()
                for item in items
                if item.get("value", "").strip()
            )
    except Exception:
        pass
    return interests.strip() if isinstance(interests, str) else ""




def recommend_users(request):
    current_user = request.user
    if not current_user.is_authenticated:
        return render(request, 'recommend_list.html', {'recommended_users': []})

    users = CustomUser.objects.exclude(id=current_user.id)

    current_interest = current_user.interests or ""
    other_profiles = [(u, u.interests or "") for u in users if (u.interests or "").strip()]

    if not current_interest.strip() or not other_profiles:
        return render(request, 'recommend_list.html', {'recommended_users': []})

    # Recréer la liste des textes
    profiles = [extract_keywords(current_user.interests or "")] + [
        extract_keywords(u.interests or "") for u in users
    ]

    # TF-IDF et similarité
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(profiles)
    similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    # Associer scores et users
    filtered_users = [u for (u, _), score in zip(other_profiles, similarity_scores) if score > 0.1]

    return render(request, 'recommend_list.html', {'recommended_users': filtered_users})


@login_required(login_url='connexion')
def custom_logout(request):
    logout(request)
    return redirect('connexion')

#
