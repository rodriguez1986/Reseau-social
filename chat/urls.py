from django.urls import path
from . views import messages,profile,home,login,load_comment, signup,home\
    ,notifications,inbox,post,get_all_users\
    ,gpt_chat_view,chat_history,marketplace_view,gaming_view, publish_game\
    ,gpt_chat_view,filter_services, unread_notifications_count,toggle_like\
    ,mark_notifications_as_read,get_notifications, post_detail, recommend_users,custom_logout\
    ,load_messages,upload_game, my_games,play_game, upload_clipGame,add_service



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
    path('load_messages/', load_messages, name='load_messages'),
    path('notifications/unread_count/', unread_notifications_count, name='unread_notifications_count'),
    path('load_comments/<int:post_id>/', load_comment, name='load_comments'),
    path('get_all_users/', get_all_users, name='get_all_users'),
    path("chat_history/<str:username>/", chat_history, name="chat_history"),
    path('recommend/', recommend_users, name='recommend_users'),
    path('marketplace/', marketplace_view, name='marketplace'),
    path('marketplace/filter/<str:category>/', filter_services, name='filter_services'),
    path('gaming/', gaming_view, name='gaming'),
    path('upload_game/', upload_game, name='upload_game'),
    path('upload_clipGame/', upload_clipGame, name='upload_clipGame'),
    path('publish_game/<int:game_id>/', publish_game, name='publish_game'),
    path('home/add_service', add_service, name='add_service'),
    path('my_games/', my_games, name='my_games'),
    path('play_game/<int:game_id>/', play_game, name='play_game'),
    path('notifications/mark-read/', mark_notifications_as_read, name='mark_notifications_as_read'),
    path('load_notifications/', get_notifications, name='load_notifications'),
    path('post/<int:post_id>/', post_detail, name='post_detail'),
    path('logout/', custom_logout, name='logout'),






]