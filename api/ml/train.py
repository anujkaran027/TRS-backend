import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from api.models import Location, Liked
import pandas as pd
import numpy as np

def train_model():
    # Prepare the data
    data = []
    for search in Liked.objects.all():
        data.append({
            'user_id': search.user.id,
            'location_id': search.location.id,
            'description': search.description,
        })

    df = pd.DataFrame(data)

    # Transform the description text to numeric features using TF-IDF
    vectorizer = TfidfVectorizer(max_features=500)  # Adjust features as needed
    description_features = vectorizer.fit_transform(df['description']).toarray()

    # Combine location_id and description features
    location_ids = df['location_id'].values.reshape(-1, 1)
    X = np.hstack((location_ids, description_features))

    # Assuming y is a binary classification indicating if the user liked the location
    # If the task is to predict the user based on location, modify the target variable accordingly
    y = df['user_id']

    # Train the model
    model = RandomForestClassifier()
    model.fit(X, y)

    # Save the model
    with open('api/ml/saved.pkl', 'wb') as file:
        pickle.dump(model, file)

    print("Model training complete and saved to saved.pkl")