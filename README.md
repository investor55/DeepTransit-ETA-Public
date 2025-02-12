# TransitML: Smart Transit Predictions for UBC Students

**Note: This project is highly in progress!**

See a more completed Transit payment app (now a NWHacks 2025 Telus Finalist): https://github.com/Farhan-Faisal/drift_nw

## Background & Motivation

UBC students commuting from Vancouver face a common challenge: planning their bus trips effectively. While existing apps like Transit and Google Maps provide some information, they don't offer comprehensive solutions for advance planning and delay prediction. Current planning typically follows this pattern:

- Need to arrive at campus by 9:30am
- Google Maps shows 30-minute bus ride
- Should be at bus stop by 9:00am
- 5-minute walk to stop means leaving at 8:55am

However, this assumes buses arrive on schedule, which often isn't the case. Delays of 5-20 minutes are common, making reliable trip planning difficult.

## Project Goals

This project aims to answer three critical questions for UBC students:

1. **How long might the actual trip take?**
   - Predict average trip duration based on:
     - Time of day
     - Day of week
     - Location
     - Weather conditions

2. **Will I be able to get on the bus or have a seat?**
   - Predict bus clustering patterns
   - Identify optimal bus choices when multiple arrive together
   - Rank buses based on likelihood of getting a seat

3. **When should I leave to catch the bus?**
   - Provide personalized departure time recommendations
   - Account for walking time to stops using TomTom routing
   - Send smart notifications with contextual information

### Real-World Example

Taking the 25 bus from Dunbar to UBC revealed an interesting pattern: the 8:40 bus, while earlier, often runs slower due to high school rush hour traffic. The 9:05 bus consistently provides a faster, more reliable journey. Our ML models aim to uncover similar patterns across the network.

## System Architecture

The system consists of three main components:

![image](https://github.com/user-attachments/assets/1de7708f-9b03-4b53-bfd6-3f70a6032b31)


### 1. Data Ingestion
- TransLink API integration for real-time bus data
- Weather API integration
- TomTom Routing Engine for walking paths
- Apache Spark for data cleaning and extraction
- S3 Data Lake / Apache Iceberg for storage

### 2. Model Training
- Feature Engineering using:
  - Pandas
  - Jupyter
  - Apache Spark
- XGBoost implementation with PyTorch
- Model evaluation using RMSE, MAE, MAPE

### 3. Prediction Service
- FastAPI for real-time predictions
- Feature Store for real-time feature serving
- ModelStoreService for model weights and versioning

## Smart Notifications

The system provides contextual SMS notifications like:

```
Leave home by 8:55 to reach Dunbar station at 9:05 to take the 25.
3 buses are predicted to arrive between 9:05 - 9:11 for a trip to UBC before 9:30.
```

## Technical Implementation

This project implements concepts from Uber's DeeprETA paper, adapting their approach for public transit prediction. Key features include:

- Multi-resolution geospatial embeddings
- Linear transformer architecture for feature interactions
- Calibration layer for different trip types
- Asymmetric Huber loss for prediction optimization

## Current Status

The data ingestion pipeline is currently operational. Next steps include:
- Model training implementation
- Prediction service development
- User notification system integration

## Contributing



## License

