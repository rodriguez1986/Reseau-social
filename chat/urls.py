from django.urls import path
from django.contrib.auth.views import LogoutView
from . views import messages,profile,home,login,load_comment, signup,home, \
    notifications,inbox,post,get_all_users,\
    gpt_chat_view,chat_history,marketplace_view,gaming_view, upload_game, \
    game_detail,gpt_chat_view,filter_services, unread_notifications_count,toggle_like\
    ,mark_notifications_as_read,get_notifications, post_detail, recommend_users,custom_logout\
    , send_messages



urlpatterns = [
    path('', login, name='connexion'),
    path('inscription/', signup, name='inscription'),
    path('home/', home, name='home'),
    path('like/<int:post_id>/', toggle_like, name='toggle_like'),

    path('post/', post, name='post'),
    path('profile/<str:username>/', profile, name='profile'),
    path('home/profile/<str:username>/', profile, name='profile'),
    path('inbox/', inbox, name='inbox'),
    path('chatbot/', gpt_chat_view, name='chatbot'),
    path('send_messages/', send_messages, name='send_messages'),
    path('notifications/unread_count/', unread_notifications_count, name='unread_notifications_count'),
    path('load_comments/<int:post_id>/', load_comment, name='load_comments'),
    path('get_all_users/', get_all_users, name='get_all_users'),
    path("chat_history/<str:username>/", chat_history, name="chat_history"),
    path('recommend/', recommend_users, name='recommend_users'),
    path('marketplace/', marketplace_view, name='marketplace'),
    path('marketplace/filter/<str:category>/', filter_services, name='filter_services'),
    path('gaming/', gaming_view, name='gaming'),
    path('upload/', upload_game, name='upload-game'),
    path('jeu/<int:game_id>/', game_detail, name='game-detail'),
    path('notifications/mark-read/', mark_notifications_as_read, name='mark_notifications_as_read'),
    path('load_notifications/', get_notifications, name='load_notifications'),
    path('post/<int:post_id>/', post_detail, name='post_detail'),
    path('logout/', custom_logout, name='logout'),






]