from typing import List
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from api.models import Recommendation, Location, Liked


def _build_corpus_and_vectorizer() -> tuple[TfidfVectorizer, np.ndarray, List[int]]:
    """Build TF-IDF vectors for all locations.

    Returns a tuple of (vectorizer, location_tfidf_matrix, location_ids).
    """
    locations = list(Location.objects.all())
    if not locations:
        return TfidfVectorizer(), np.empty((0, 0)), []

    descriptions = [loc.description or "" for loc in locations]
    vectorizer = TfidfVectorizer(max_features=2000)
    matrix = vectorizer.fit_transform(descriptions)  # shape: (num_locations, num_features)
    location_ids = [loc.id for loc in locations]
    return vectorizer, matrix, location_ids


def _build_user_profile_vector(vectorizer: TfidfVectorizer, liked_texts: List[str]) -> np.ndarray:
    """Create a user profile vector by averaging TF-IDF vectors of liked descriptions."""
    if not liked_texts:
        return np.empty((0,))
    liked_matrix = vectorizer.transform(liked_texts)  # (num_liked, num_features)
    profile = liked_matrix.mean(axis=0)  # (1, num_features)
    return np.asarray(profile)


def generate_recommendations(user, top_k: int = 10):
    """Compute content-based recommendations and store them in Recommendation.

    - Builds a TF-IDF model over all `Location` descriptions
    - Creates a user profile from liked locations' descriptions
    - Ranks all locations by cosine similarity to the profile
    - Excludes already liked locations
    - Stores top_k in `Recommendation`
    """
    liked_qs = Liked.objects.filter(user=user).select_related("location")
    if not liked_qs.exists():
        # Clear any previous recommendations if no likes
        Recommendation.objects.filter(user=user).delete()
        return

    # Build corpus for all locations
    vectorizer, location_matrix, location_ids = _build_corpus_and_vectorizer()
    if location_matrix.shape[0] == 0:
        Recommendation.objects.filter(user=user).delete()
        return

    # Build user profile from liked descriptions
    liked_texts = [liked.location.description or "" for liked in liked_qs]
    user_profile = _build_user_profile_vector(vectorizer, liked_texts)  # (1, num_features)
    if user_profile.size == 0:
        Recommendation.objects.filter(user=user).delete()
        return

    # Compute cosine similarity between user profile and all locations
    # Ensure correct shapes for sklearn cosine_similarity
    similarities = cosine_similarity(user_profile, location_matrix).ravel()  # (num_locations,)

    # Exclude already liked locations
    liked_location_ids = set(liked_qs.values_list("location_id", flat=True))

    ranked_indices = np.argsort(similarities)[::-1]
    recommended_location_ids: List[int] = []
    for idx in ranked_indices:
        loc_id = location_ids[idx]
        if loc_id in liked_location_ids:
            continue
        recommended_location_ids.append(loc_id)
        if len(recommended_location_ids) >= top_k:
            break

    recommended_locations = Location.objects.filter(id__in=recommended_location_ids)

    # Persist recommendations
    recommendation, _ = Recommendation.objects.update_or_create(user=user)
    recommendation.recommended_locations.set(recommended_locations)
    # No print; rely on API responses
