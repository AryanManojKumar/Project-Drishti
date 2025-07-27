"""Vertex AI Forecasting for bottleneck prediction."""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd
from google.cloud import aiplatform
from google.cloud import bigquery
from google.cloud import pubsub_v1

from .config import Config

class BottleneckForecaster:
    """Predicts crowd bottlenecks using Vertex AI Forecasting."""
    
    def __init__(self):
        self.config = Config()
        self.bq_client = bigquery.Client(project=self.config.PROJECT_ID)
        self.publisher = pubsub_v1.PublisherClient()
        
        # Initialize Vertex AI
        aiplatform.init(
            project=self.config.PROJECT_ID,
            location=self.config.VERTEX_AI_LOCATION
        )
        
        self.prediction_topic_path = self.publisher.topic_path(
            self.config.PROJECT_ID,
            self.config.PREDICTION_TOPIC
        )
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def prepare_training_data(self, lookback_days: int = 30) -> pd.DataFrame:
        """
        Prepare historical data for model training.
        
        Args:
            lookback_days: Number of days of historical data to use
            
        Returns:
            DataFrame with features for training
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=lookback_days)
        
        query = f"""
        SELECT 
            timestamp,
            zone_id,
            person_count,
            density,
            device_count,
            flow_velocity,
            flow_direction,
            hour_of_day,
            day_of_week,
            is_weekend,
            weather_condition,
            event_nearby
        FROM `{self.config.PROJECT_ID}.{self.config.DATASET_ID}.{self.config.CROWD_DATA_TABLE}`
        WHERE timestamp >= '{start_date.isoformat()}'
        AND timestamp <= '{end_date.isoformat()}'
        ORDER BY zone_id, timestamp
        """
        
        try:
            df = self.bq_client.query(query).to_dataframe()
            
            # Feature engineering
            df = self._engineer_features(df)
            
            self.logger.info(f"Prepared {len(df)} rows of training data")
            return df
            
        except Exception as e:
            self.logger.error(f"Error preparing training data: {e}")
            return pd.DataFrame()
    
    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer additional features for forecasting."""
        if df.empty:
            return df
        
        # Time-based features
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        # Lag features (previous values)
        for col in ['person_count', 'density', 'device_count']:
            if col in df.columns:
                df[f'{col}_lag_1'] = df.groupby('zone_id')[col].shift(1)
                df[f'{col}_lag_2'] = df.groupby('zone_id')[col].shift(2)
        
        # Rolling averages
        for col in ['person_count', 'density']:
            if col in df.columns:
                df[f'{col}_rolling_mean_5'] = df.groupby('zone_id')[col].rolling(5).mean().reset_index(0, drop=True)
                df[f'{col}_rolling_std_5'] = df.groupby('zone_id')[col].rolling(5).std().reset_index(0, drop=True)
        
        # Bottleneck indicator (target variable)
        df['is_bottleneck'] = (df['density'] > self.config.BOTTLENECK_DENSITY_THRESHOLD).astype(int)
        
        return df
    
    def create_forecasting_dataset(self, df: pd.DataFrame) -> str:
        """
        Create a Vertex AI dataset for forecasting.
        
        Args:
            df: Prepared training data
            
        Returns:
            Dataset resource name
        """
        try:
            # Upload data to BigQuery table for Vertex AI
            table_id = f"{self.config.PROJECT_ID}.{self.config.DATASET_ID}.forecasting_training_data"
            
            job_config = bigquery.LoadJobConfig(
                write_disposition="WRITE_TRUNCATE",
                autodetect=True
            )
            
            job = self.bq_client.load_table_from_dataframe(df, table_id, job_config=job_config)
            job.result()
            
            # Create Vertex AI dataset
            dataset = aiplatform.TabularDataset.create(
                display_name="crowd-forecasting-dataset",
                bq_source=f"bq://{table_id}"
            )
            
            self.logger.info(f"Created dataset: {dataset.resource_name}")
            return dataset.resource_name
            
        except Exception as e:
            self.logger.error(f"Error creating dataset: {e}")
            return ""
    
    def train_forecasting_model(self, dataset_name: str) -> str:
        """
        Train a forecasting model using Vertex AI.
        
        Args:
            dataset_name: Dataset resource name
            
        Returns:
            Model resource name
        """
        try:
            dataset = aiplatform.TabularDataset(dataset_name)
            
            # Create and run training job
            job = aiplatform.AutoMLForecastingTrainingJob(
                display_name="crowd-bottleneck-forecasting",
                optimization_objective="minimize-rmse",
                column_specs={
                    "timestamp": "timestamp",
                    "zone_id": "categorical",
                    "is_bottleneck": "target"
                },
                data_granularity_unit="minute",
                data_granularity_count=5,
                forecast_horizon=self.config.PREDICTION_WINDOW_MINUTES // 5,  # 5-minute intervals
            )
            
            model = job.run(
                dataset=dataset,
                target_column="is_bottleneck",
                time_column="timestamp",
                time_series_identifier_column="zone_id",
                training_fraction_split=0.8,
                validation_fraction_split=0.1,
                test_fraction_split=0.1,
            )
            
            self.logger.info(f"Model trained: {model.resource_name}")
            return model.resource_name
            
        except Exception as e:
            self.logger.error(f"Error training model: {e}")
            return ""
    
    def predict_bottlenecks(self, current_data: Dict) -> List[Dict]:
        """
        Generate bottleneck predictions for all zones.
        
        Args:
            current_data: Current crowd and device data
            
        Returns:
            List of predictions per zone
        """
        try:
            # Prepare prediction input
            prediction_input = self._prepare_prediction_input(current_data)
            
            # Get predictions from deployed model
            predictions = self._get_model_predictions(prediction_input)
            
            # Process and format predictions
            formatted_predictions = self._format_predictions(predictions)
            
            # Publish predictions
            self._publish_predictions(formatted_predictions)
            
            return formatted_predictions
            
        except Exception as e:
            self.logger.error(f"Error generating predictions: {e}")
            return []
    
    def _prepare_prediction_input(self, current_data: Dict) -> List[Dict]:
        """Prepare input data for prediction."""
        # This would format current crowd and device data
        # into the structure expected by the trained model
        
        prediction_instances = []
        
        for zone_id, zone_data in current_data.get('zones', {}).items():
            instance = {
                'zone_id': zone_id,
                'timestamp': datetime.utcnow().isoformat(),
                'person_count': zone_data.get('person_count', 0),
                'density': zone_data.get('density', 0),
                'device_count': zone_data.get('device_count', 0),
                'flow_velocity': zone_data.get('flow_velocity', 0),
                'hour': datetime.utcnow().hour,
                'day_of_week': datetime.utcnow().weekday(),
                'is_weekend': int(datetime.utcnow().weekday() >= 5)
            }
            prediction_instances.append(instance)
        
        return prediction_instances
    
    def _get_model_predictions(self, instances: List[Dict]) -> List[Dict]:
        """Get predictions from deployed Vertex AI model."""
        # This would call the deployed forecasting model
        # For now, return mock predictions
        
        predictions = []
        for instance in instances:
            # Mock prediction logic
            current_density = instance.get('density', 0)
            bottleneck_probability = min(current_density / self.config.BOTTLENECK_DENSITY_THRESHOLD, 1.0)
            
            prediction = {
                'zone_id': instance['zone_id'],
                'prediction_time': datetime.utcnow().isoformat(),
                'forecast_time': (datetime.utcnow() + timedelta(minutes=self.config.PREDICTION_WINDOW_MINUTES)).isoformat(),
                'bottleneck_probability': bottleneck_probability,
                'predicted_density': current_density * (1 + bottleneck_probability * 0.5),
                'confidence_interval': [
                    current_density * 0.8,
                    current_density * 1.3
                ]
            }
            predictions.append(prediction)
        
        return predictions
    
    def _format_predictions(self, predictions: List[Dict]) -> List[Dict]:
        """Format predictions with alert levels."""
        formatted = []
        
        for pred in predictions:
            alert_level = self._determine_alert_level(pred['bottleneck_probability'])
            
            formatted_pred = {
                **pred,
                'alert_level': alert_level,
                'requires_intervention': pred['bottleneck_probability'] > self.config.ALERT_PROBABILITY_THRESHOLD
            }
            formatted.append(formatted_pred)
        
        return formatted
    
    def _determine_alert_level(self, probability: float) -> str:
        """Determine alert level based on bottleneck probability."""
        if probability >= 0.8:
            return 'critical'
        elif probability >= 0.6:
            return 'high'
        elif probability >= 0.4:
            return 'medium'
        else:
            return 'low'
    
    def _publish_predictions(self, predictions: List[Dict]):
        """Publish predictions to Pub/Sub."""
        try:
            message_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'predictions': predictions,
                'data_type': 'bottleneck_predictions'
            }
            
            message_json = json.dumps(message_data).encode('utf-8')
            future = self.publisher.publish(self.prediction_topic_path, message_json)
            future.result()
            
            self.logger.info(f"Published {len(predictions)} predictions")
            
        except Exception as e:
            self.logger.error(f"Failed to publish predictions: {e}")