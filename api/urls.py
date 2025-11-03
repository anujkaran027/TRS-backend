from django.urls import path
from . import views

urlpatterns = [
    path('locations/', views.LocationListView.as_view(), name='home'),
    path('like-location/', views.LikeLocationView.as_view(), name='like-location'),
    path('suggest/', views.RecommendationView.as_view(), name='recommend-locations'),
    path('liked/', views.LikedLocationsView.as_view(), name='liked-locations'),
    path('toggle-like/<int:location_id>/', views.ToggleLikeView.as_view(), name='toggle-like'),
    path('is-liked/<int:location_id>/', views.IsLikedView.as_view(), name='is-liked'),
]
