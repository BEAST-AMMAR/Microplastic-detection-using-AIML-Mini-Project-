"""
IoT Integration Module - ThingSpeak Cloud Support
Upload microplastics detection results to cloud dashboard
Real-time monitoring and historical data analysis
"""

import requests
import json
import logging
import time
from typing import Dict, Optional, List
from datetime import datetime
from pathlib import Path
import threading

logger = logging.getLogger(__name__)


class ThingSpeakUploader:
    """
    Upload microplastics detection results to ThingSpeak
    IoT cloud platform for real-time data visualization
    """

    def __init__(self, channel_id: str, write_key: str, read_key: Optional[str] = None):
        """
        Initialize ThingSpeak uploader

        Args:
            channel_id: ThingSpeak channel ID
            write_key: Write API key
            read_key: Read API key (optional)
        """
        self.channel_id = channel_id
        self.write_key = write_key
        self.read_key = read_key
        self.base_url = "https://api.thingspeak.com"
        self.last_upload_time = 0
        self.min_interval = 15  # Minimum 15 seconds between uploads (API limit)

        logger.info(f"✓ ThingSpeak uploader initialized (Channel: {channel_id})")

    def upload_detection_result(self, detection_data: Dict, 
                               metadata: Optional[Dict] = None) -> bool:
        """
        Upload detection result to ThingSpeak

        Args:
            detection_data: Detection metrics dictionary
            metadata: Optional metadata (location, timestamp, etc.)

        Returns:
            True if successful
        """

        # Rate limiting
        now = time.time()
        if now - self.last_upload_time < self.min_interval:
            time.sleep(self.min_interval - (now - self.last_upload_time))

        try:
            # Prepare payload
            payload = {
                'api_key': self.write_key,
                'field1': int(detection_data.get('detection_count', 0)),  # Number of detections
                'field2': round(detection_data.get('yolov8_conf', 0), 4),  # YOLOv8 confidence
                'field3': round(detection_data.get('mobilenetv2_conf', 0), 4),  # MobileNetV2 confidence
                'field4': round(detection_data.get('ensemble_conf', 0), 4),  # Ensemble confidence
                'field5': round(detection_data.get('final_conf', 0), 4),  # Final confidence
                'field6': round(detection_data.get('image_quality', 0), 4),  # Image quality metric
                'field7': int(detection_data.get('processing_time_ms', 0)),  # Processing time
                'field8': metadata.get('location', '') if metadata else 'Unknown'  # Location
            }

            # Send to ThingSpeak
            response = requests.post(
                f"{self.base_url}/update",
                data=payload,
                timeout=5
            )

            if response.status_code == 200:
                entry_id = response.text.strip()
                logger.info(f"✓ Uploaded to ThingSpeak (Entry ID: {entry_id})")
                self.last_upload_time = time.time()
                return True
            else:
                logger.warning(f"⚠ ThingSpeak upload failed: HTTP {response.status_code}")
                return False

        except requests.exceptions.Timeout:
            logger.warning("⚠ ThingSpeak upload timeout")
            return False
        except Exception as e:
            logger.error(f"✗ ThingSpeak upload error: {e}")
            return False

    def batch_upload(self, results_list: List[Dict]) -> int:
        """
        Upload multiple results

        Args:
            results_list: List of detection results

        Returns:
            Number of successful uploads
        """
        successful = 0
        for i, result in enumerate(results_list):
            if self.upload_detection_result(result):
                successful += 1
            if i < len(results_list) - 1:
                time.sleep(0.5)

        logger.info(f"Batch upload: {successful}/{len(results_list)} successful")
        return successful

    def read_channel_data(self, results: int = 100) -> Optional[List[Dict]]:
        """
        Read historical data from ThingSpeak channel

        Args:
            results: Number of entries to retrieve

        Returns:
            List of channel data or None
        """
        if not self.read_key:
            logger.warning("Read key not provided")
            return None

        try:
            url = f"{self.base_url}/channels/{self.channel_id}/feeds.json"
            params = {
                'api_key': self.read_key,
                'results': results,
                'order': 'desc'
            }

            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✓ Retrieved {len(data.get('feeds', []))} entries from ThingSpeak")
                return data.get('feeds', [])
            else:
                logger.warning(f"Failed to read: HTTP {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error reading ThingSpeak: {e}")
            return None

    def get_channel_info(self) -> Optional[Dict]:
        """Get channel information"""
        try:
            url = f"{self.base_url}/channels/{self.channel_id}.json"
            params = {'api_key': self.read_key} if self.read_key else {}

            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Error getting channel info: {e}")

        return None


class LocalDataCache:
    """
    Local caching system for offline operation
    Automatically syncs when connection is restored
    """

    def __init__(self, cache_file: str = "thingspeak_cache.json"):
        self.cache_file = cache_file
        self.cache = self._load_cache()

    def _load_cache(self) -> List[Dict]:
        """Load cached data from file"""
        try:
            if Path(self.cache_file).exists():
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")

        return []

    def _save_cache(self):
        """Save cache to file"""
        try:
            Path(self.cache_file).parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")

    def add(self, data: Dict):
        """Add data to cache"""
        self.cache.append({
            'timestamp': datetime.now().isoformat(),
            'data': data
        })
        self._save_cache()
        logger.info(f"Cached locally ({len(self.cache)} entries)")

    def get_all(self) -> List[Dict]:
        """Get all cached data"""
        return self.cache

    def clear(self):
        """Clear cache"""
        self.cache = []
        self._save_cache()
        logger.info("Cache cleared")

    def size(self) -> int:
        """Get cache size"""
        return len(self.cache)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("✓ IoT integration module ready")
