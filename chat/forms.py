from django import forms
from chat.models import CustomUser, GameUpload
from .models import Message
from django.contrib.auth import get_user_model

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    bio = forms.CharField(
        label="Biographie",
        widget=forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Parlez un peu de vous...'}),
        required=False
    )
    profile_picture = forms.ImageField(
        label="Photo de profil",
        required=False
    )
    is_artist = forms.BooleanField(
        label="Artiste",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'})
    )
    is_freelancer = forms.BooleanField(
        label="Freelance",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'})
    )
    is_gamer = forms.BooleanField(
        label="Gamer",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'})
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'bio', 'profile_picture','interests', 'is_artist', 'is_freelancer', 'is_gamer')

        def clean_interests(self):
            raw_interests = self.cleaned_data.get('interests', '')
            return extract_keywords(raw_interests)




class MessageForm(forms.ModelForm):
    # Choisir un destinataire parmi les utilisateurs
    receiver = forms.ModelChoiceField(queryset=get_user_model().objects.all(), required=True)
    content = forms.CharField(widget=forms.Textarea, required=True, label="Message", max_length=1000)

    class Meta:
        model = Message
        fields = ['receiver', 'content']


class GameUploadForm(forms.ModelForm):
    class Meta:
        model = GameUpload
        fields = ['title', 'description', 'game_file', 'thumbnail', 'game_mode']

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full p-2 border rounded',
                'placeholder': 'Titre du jeu'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full p-2 border rounded',
                'placeholder': 'Décrivez votre jeu...',
                'rows': 4
            }),
            'game_file': forms.ClearableFileInput(attrs={
                'class': 'w-full'
            }),
            'thumbnail': forms.ClearableFileInput(attrs={
                'class': 'w-full'
            }),
            'game_mode': forms.Select(attrs={
                'class': 'w-full p-2 border rounded'
            }),
        }