from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth.models import User
from rest_framework import generics,status
from .serializers import UserSerializer
from .serializers import LocationSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from api.models import Location,Liked, Recommendation
from .serializers import LikedSerializer
from .ml.recommend import generate_recommendations

# Create your views here.

class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class LocationListView(generics.ListAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]

class LikeLocationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        location_id = request.data.get("location_id")

        try:
            location = Location.objects.get(id=location_id)
        except Location.DoesNotExist:
            return Response({"error": "Location not found"}, status=status.HTTP_404_NOT_FOUND)

        liked_location, created = Liked.objects.get_or_create(
            user=user,
            location=location,
        )

        if not created:
            return Response({"message": "You already liked this location"}, status=status.HTTP_400_BAD_REQUEST)

        # Generate new recommendations after liking
        generate_recommendations(user)

        serializer = LikedSerializer(liked_location)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class ToggleLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, location_id):
        user = request.user
        location = Location.objects.filter(id=location_id).first()
        if not location:
            return Response({"error": "Location not found"}, status=404)

        liked, created = Liked.objects.get_or_create(user=user, location=location)
        if not created:
            liked.delete()
            message = "Location unliked"
        else:
            message = "Location liked"

        # Generate new recommendations after liking/unliking
        generate_recommendations(user)

        return Response({"message": message})
    
class IsLikedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, location_id):
        user = request.user
        liked = Liked.objects.filter(user=user, location_id=location_id).exists()
        return Response({"liked": liked})
    
def get_fallback_locations(user):
    # Get the descriptions of liked locations
    liked_locations = Liked.objects.filter(user=user)
    liked_descriptions = liked_locations.values_list('location__description', flat=True)

    # Find similar locations based on description
    if liked_descriptions.exists():
        query = Q()
        for description in liked_descriptions:
            query |= Q(description__icontains=description)
        
        # Exclude already liked locations
        similar_locations = Location.objects.filter(query).exclude(
            id__in=liked_locations.values_list('location_id', flat=True)
        )
        return similar_locations[:10]  # Limit the number of results
    return Location.objects.none()

class LikedLocationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        liked_locations = Liked.objects.filter(user=user).select_related('location')
        
        locations_data = [
            {
                'id': liked.location.id,
                'name': liked.location.name,
                'description': liked.location.description,
                'state': liked.location.state,
                'city': liked.location.city,
                'zone': liked.location.zone,
                'entryprice': liked.location.entryprice,
                'liked_at': liked.id  # Using the Liked model ID as a timestamp proxy
            }
            for liked in liked_locations
        ]
        
        return Response(locations_data)

class RecommendationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Fetch recommendations
        recommendation = Recommendation.objects.filter(user=user).first()
        if recommendation and recommendation.recommended_locations.exists():
            locations = recommendation.recommended_locations.all()
        else:
            # Fallback to similar locations
            locations = get_fallback_locations(user)

        serializer = LocationSerializer(locations, many=True)
        return Response(serializer.data)