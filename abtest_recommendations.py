# ab_test_recommendations.py
from config import user_id_input
from datetime import datetime, timedelta
import pandas as pd
from model_registry_manager import get_model_version, load_model, get_latest_model_path
import recommendation_engine
from data_collecting_monitoring.mongodb_client import get_rate_table
# Assuming the A/B test starts on April 5, 2024, and lasts for 7 days
AB_TEST_START_DATE = datetime(2024, 4, 5)
AB_TEST_END_DATE = AB_TEST_START_DATE + timedelta(days=7)

def is_ab_test_active():
    """Check if the current date is within the A/B test duration."""
    now = datetime.now()
    return AB_TEST_START_DATE <= now <= AB_TEST_END_DATE


def generate_recommendations_for_user(user_id):
    rate_table = get_rate_table()
    query_result = rate_table.find().sort("time", -1).limit(20000)
    ratings_df = pd.DataFrame(list(query_result))
    ratings_df = ratings_df[['user_id', 'movie_id', 'rating']]
    print(ratings_df.head())
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
    recommendations = generate_recommendations_for_user(user_id_input)
    print(recommendations)
