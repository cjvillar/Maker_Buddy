from django.urls import path
#from .views import public_feed
from .views import PublicFeedView

app_name = "public_feed"

urlpatterns = [
    #path("", public_feed, name="home"),
     path("", PublicFeedView.as_view(), name="home"),
]
