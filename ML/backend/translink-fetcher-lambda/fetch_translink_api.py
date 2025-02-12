#!/usr/bin/env python3
"""
Translink Data Fetcher

This script defines a TranslinkDataFetcher class that fetches GTFS realtime and position data
from Translink's API and saves them as Parquet files with timestamps in the filenames.
"""

import os
from datetime import datetime
from pathlib import Path
import logging
import sys
import boto3

import pandas as pd
import requests
from google.transit import gtfs_realtime_pb2
# from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

# load_dotenv()
AWS_S3_BUCKET = "translinkdata"


class TranslinkDataFetcher:
    """A class to fetch Translink GTFS realtime and position data and save as Parquet files."""

    def __init__(self, output_dir: str = "/tmp"):
        """
        Initialize the TranslinkDataFetcher.

        Args:
            env_path (str): Path to the .env file containing environment variables.
            output_dir (str): Directory where Parquet files will be saved.
        """
        # self.load_environment(env_path)
        # self.api_key = os.getenv("TRANSLINK_KEY")
        self.api_key = self._get_parameter('/translink/api-key')
        # self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        # self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.position_url = (
            f"https://gtfsapi.translink.ca/v3/gtfsposition?apikey={self.api_key}"
        )
        self.realtime_url = (
            f"https://gtfsapi.translink.ca/v3/gtfsrealtime?apikey={self.api_key}"
        )
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logging.info(f"Output directory set to: {self.output_dir}")

    def _get_parameter(self, name):
        """Get Translink API key from Parameter Store"""
        try:
            ssm = boto3.client('ssm')
            response = ssm.get_parameter(
                Name=name,
                WithDecryption=True
            )
            return response['Parameter']['Value']
        except Exception as e:
            logging.error(f"Error fetching parameter: {e}")
            raise

    def load_environment(self, env_path: str):
        """
        Load environment variables from a .env file.

        Args:
            env_path (str): Path to the .env file.
        """
        load_dotenv(env_path)
        if not os.getenv("TRANSLINK_KEY"):
            logging.error("TRANSLINK_KEY not found in environment variables.")
            sys.exit(1)
        logging.info("Environment variables loaded successfully.")

    def fetch_gtfs_data(self, url: str) -> bytes:
        """
        Fetch GTFS data from the given URL.

        Args:
            url (str): The API endpoint to fetch data from.

        Returns:
            bytes: The raw response content if successful, else None.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            logging.info(f"Successfully fetched data from {url}")
            return response.content
        except requests.RequestException as e:
            logging.error(f"Error fetching data from {url}: {e}")
            return None

    def parse_gtfs_realtime_data(self, response: bytes) -> pd.DataFrame:
        """
        Parse GTFS realtime data from the response.

        Args:
            response (bytes): The raw GTFS realtime data.

        Returns:
            pd.DataFrame: A DataFrame containing parsed realtime data.
        """
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response)

        rows = []
        for entity in feed.entity:
            if not entity.HasField("trip_update"):
                continue  # Skip if there's no trip_update

            trip_update = entity.trip_update
            trip = trip_update.trip
            vehicle = trip_update.vehicle

            base_row = {
                "id": entity.id,
                "is_deleted": entity.is_deleted,
                "trip_id": trip.trip_id,
                "start_date": trip.start_date,
                "schedule_relationship": trip.schedule_relationship,
                "route_id": trip.route_id,
                "direction_id": trip.direction_id,
                "vehicle_id": vehicle.id if vehicle.HasField("id") else None,
                "vehicle_label": vehicle.label if vehicle.HasField("label") else None,
                "current_datetime": datetime.utcnow(),  # Use UTC for consistency
            }

            for stop_time_update in trip_update.stop_time_update:
                row = base_row.copy()
                row.update(
                    {
                        "stop_sequence": stop_time_update.stop_sequence,
                        "stop_id": stop_time_update.stop_id,
                        "arrival_delay": (
                            stop_time_update.arrival.delay
                            if stop_time_update.HasField("arrival")
                            else None
                        ),
                        "arrival_time": (
                            stop_time_update.arrival.time
                            if stop_time_update.HasField("arrival")
                            else None
                        ),
                        "departure_delay": (
                            stop_time_update.departure.delay
                            if stop_time_update.HasField("departure")
                            else None
                        ),
                        "departure_time": (
                            stop_time_update.departure.time
                            if stop_time_update.HasField("departure")
                            else None
                        ),
                        "stop_schedule_relationship": stop_time_update.schedule_relationship,
                    }
                )
                rows.append(row)

        if rows:
            logging.info(f"Parsed {len(rows)} realtime records.")
            return pd.DataFrame(rows)
        else:
            logging.warning("No realtime records parsed.")
            return pd.DataFrame()

    def parse_gtfs_position_data(self, response: bytes) -> pd.DataFrame:
        """
        Parse GTFS position data from the response.

        Args:
            response (bytes): The raw GTFS position data.

        Returns:
            pd.DataFrame: A DataFrame containing parsed position data.
        """
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response)

        rows = []
        for entity in feed.entity:
            if not entity.HasField("vehicle"):
                continue  # Skip if there's no vehicle information

            vehicle = entity.vehicle
            trip = vehicle.trip
            position = vehicle.position

            row = {
                "id": entity.id,
                "trip_id": trip.trip_id,
                "start_date": trip.start_date,
                "schedule_relationship": trip.schedule_relationship,
                "route_id": trip.route_id,
                "direction_id": trip.direction_id,
                "vehicle_id": (
                    vehicle.vehicle.id if vehicle.vehicle.HasField("id") else None
                ),
                "vehicle_label": (
                    vehicle.vehicle.label if vehicle.vehicle.HasField("label") else None
                ),
                "latitude": (
                    position.latitude if position.HasField("latitude") else None
                ),
                "longitude": (
                    position.longitude if position.HasField("longitude") else None
                ),
                "current_stop_sequence": (
                    vehicle.current_stop_sequence
                    if vehicle.HasField("current_stop_sequence")
                    else None
                ),
                "current_status": (
                    vehicle.current_status
                    if vehicle.HasField("current_status")
                    else None
                ),
                "timestamp": (
                    vehicle.timestamp if vehicle.HasField("timestamp") else None
                ),
                "stop_id": vehicle.stop_id if vehicle.HasField("stop_id") else None,
                "current_datetime": datetime.utcnow(),  # Use UTC for consistency
            }
            rows.append(row)

        if rows:
            logging.info(f"Parsed {len(rows)} position records.")
            return pd.DataFrame(rows)
        else:
            logging.warning("No position records parsed.")
            return pd.DataFrame()

    def save_to_parquet(self, df: pd.DataFrame, data_type: str):
        """
        Save the DataFrame to a Parquet file with a timestamp in the filename.

        Args:
            df (pd.DataFrame): The DataFrame to save.
            data_type (str): The type of data ('position' or 'realtime').
        """
        if df.empty:
            logging.warning(f"No data to save for {data_type}.")
            return

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{data_type}_data_{timestamp}.parquet"
        file_path = self.output_dir / filename
        try:
            df.to_parquet(
                f"s3://{AWS_S3_BUCKET}/raw_data/translink_{timestamp}_{data_type}.parquet",
                index=False,
                storage_options={
                    # "key": self.aws_access_key_id,
                    # "secret": self.aws_secret_access_key,
                        # "use_ssl": True
                },
            )
            logging.info(f"Saved {data_type} data to {file_path}")
        except Exception as e:
            logging.error(f"Error saving {data_type} data to Parquet: {e}")
            raise

    def run(self):
        """
        Execute the data fetching and saving process.
        """
        # Fetch data
        realtime_data_raw = self.fetch_gtfs_data(self.realtime_url)
        position_data_raw = self.fetch_gtfs_data(self.position_url)

        if not realtime_data_raw or not position_data_raw:
            logging.error("Failed to fetch one or more data sources. Exiting.")
            sys.exit(1)

        # Parse data
        realtime_df = self.parse_gtfs_realtime_data(realtime_data_raw)
        position_df = self.parse_gtfs_position_data(position_data_raw)

        # Save data to Parquet
        self.save_to_parquet(position_df, "position")
        self.save_to_parquet(realtime_df, "realtime")


# def main():
#     """Main function to execute the TranslinkDataFetcher."""
#     fetcher = TranslinkDataFetcher()
#     fetcher.run()


# if __name__ == "__main__":
#     main()


def lambda_handler(event, context):
    try:
        boto3.setup_default_session(region_name='us-east-1')
        fetcher = TranslinkDataFetcher(output_dir="/tmp")  # Use /tmp for Lambda
        fetcher.run()  # Your existing run method
        return {
            'statusCode': 200,
            'body': 'TranslinkDataFetcher executed successfully'
        }
    except Exception as e:
        logging.error(f"Error in Lambda execution: {str(e)}")
        # return {
        #     'statusCode': 500,
        #     'body': f"Error: {str(e)}"
        # }
        raise

if __name__ == "__main__":
    lambda_handler(None, None)