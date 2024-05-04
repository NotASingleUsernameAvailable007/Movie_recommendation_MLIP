from flask import Flask, jsonify
import pandas as pd
import recommendation_engine
from data_loader import load_ratings_data
from config import csv_path
from datetime import datetime, timedelta
from data_collecting_monitoring.mongodb_client import get_rate_table
from model_registry_manager import get_model_version, load_model, get_latest_model_path

app = Flask(__name__)

AB_TEST_START_DATE = datetime(2024, 4, 21)
AB_TEST_END_DATE = AB_TEST_START_DATE + timedelta(days=7)

def is_ab_test_active():
    """Check if the current date is within the A/B test duration."""
    now = datetime.now()
    return AB_TEST_START_DATE <= now <= AB_TEST_END_DATE

@app.route('/recommend/<int:user_id>', methods=['GET'])
def generate_recommendations_for_user(user_id):
    # rate_table = get_rate_table()
    # query_result = rate_table.find().sort("time", -1).limit(20000)
    # ratings_df = pd.DataFrame(list(query_result))
    ratings_df = pd.read_csv("retrained_movies.csv")
    ratings_df = ratings_df[['user_id', 'movie_id', 'rating']]
    # print(ratings_df.head())
    if is_ab_test_active():
        # A/B test logic to decide between old and new model versions
        model_version = "1.1" if user_id % 2 == 0 else "1.2"  # Example criteria
        print(f"User {user_id} is in the A/B test group. Using model version {model_version}.")
    else:
        # After the A/B test, use the latest model for all users
        model_version = None  # Signify the use of the latest model
        print(f"A/B test is not active. Using the latest model for user {user_id}.")

    # Load the selected model
    model_path = get_model_version(model_version) if model_version else get_latest_model_path()
    if model_path:
        print(f"Loading model from: {model_path}")
        model = load_model(model_path)
        recommendations = recommendation_engine.return_result(user_id, ratings_df, model, 20)
        return recommendations
    else:
        print(f"No model found for version {model_version}.")
        return []

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8084)
    