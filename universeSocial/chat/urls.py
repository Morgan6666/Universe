from django.urls import path, re_path
from universeSocial.chat import consumers
from universeSocial.chat import views
from django.conf.urls.static import static
from Universe import settings
app_name = 'Chat'
websocket_urlpatterns = [
    re_path(r'^chat_ws$', consumers.ChatConsumer.as_asgi()),
]

urlpatterns = [
    path('messages/', views.MessageModelList.as_view(), name = 'all_messages_list'),
    path('messages/<dialog_with>/', views.MessageModelList.as_view(), name = 'messages_list'),
    path('dialogs/', views.DialogsModelList.as_view(), name = 'dialogs_list'),
    path('self/', views.SelfInfoView.as_view(), name= 'self_info'),
    path('upload/', views.UploadView.as_view(), name = 'fileupload'),

]