import json
from datetime import datetime
import requests
import pandas as pd
import boto3


class WeatherDataFetcher:

    def __init__(self, api_key_value):
        self.api_key = api_key_value
        self.s3_folder = "weather_data"
        self.s3_bucket = "translinkdata"
        self.lat = 49.236
        self.lon = -123.149
        self.url = f"https://api.qweather.com/v7/weather/now?location={self.lon:.2f},{self.lat:.2f}&key={self.api_key}&unit=m&lang=en"

    def get_real_time_weather(self):
        """
        Fetches the real-time weather data from QWeather API.

        Parameters:
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.
        api_key (str): Your unique API key for QWeather.

        Returns:
        dict: JSON response from the API containing the weather data.
        """

        response = requests.get(self.url, timeout=15)
        weather_json = json.loads(response.text)

        weather_df = pd.json_normalize(weather_json)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        return weather_df.to_parquet(
            f"s3://{self.s3_bucket}/{self.s3_folder}/weather_{timestamp}.parquet",
            index=False,
            storage_options={},
        )


def get_parameter(name):
    """Get QWeather API key from Parameter Store"""
    try:
        ssm = boto3.client("ssm")
        response = ssm.get_parameter(Name=name, WithDecryption=True)
        return response["Parameter"]["Value"]
    except Exception as e:
        raise


def lambda_handler(event, context):
    try:
        boto3.setup_default_session(region_name="us-east-1")
        qweather_api_key = get_parameter("/translink/qweather")
        weatherfetcher = WeatherDataFetcher(qweather_api_key)
        weatherfetcher.get_real_time_weather()  # Your existing run method
        return {"statusCode": 200, "body": "WeatherFetcher executed successfully"}
    except Exception as e:
        # return {"statusCode": 500, "body": f"Error: {str(e)}"}
        raise


# if __name__ == "__main__":
#     api_key_value = input("Enter your API key: ")
#     weatherfetcher = WeatherDataFetcher(api_key_value)
#     weatherfetcher.get_real_time_weather()

if __name__ == "__main__":
    lambda_handler(None, None)
