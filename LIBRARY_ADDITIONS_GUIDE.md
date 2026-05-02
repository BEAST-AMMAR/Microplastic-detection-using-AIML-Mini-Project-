# 📋 DETAILED GUIDE: ADDING THINGSPEAK & OTHER INTEGRATIONS

## PART 1: ADDING THINGSPEAK INTEGRATION (IoT Cloud Logging)

### Why ThingSpeak?
- Real-time data visualization
- Cloud-based monitoring dashboard
- Multi-device aggregation
- Alert notifications
- Historical data analysis

### Complete Implementation Guide

#### Step 1: Create iot_integration.py module

```python
# iot_integration.py - ThingSpeak Integration Module

import requests
import json
import logging
import time
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ThingSpeakUploader:
    """
    Upload microplastics detection results to ThingSpeak
    Cloud-based IoT monitoring platform
    """
    
    def __init__(self, channel_id: str, write_key: str):
        """
        Initialize ThingSpeak uploader
        
        Args:
            channel_id: Your ThingSpeak channel ID
            write_key: Your ThingSpeak write API key
        """
        self.channel_id = channel_id
        self.write_key = write_key
        self.base_url = "https://api.thingspeak.com"
        self.field_mapping = {
            'detection_count': 'field1',
            'yolov8_confidence': 'field2',
            'mobilenetv2_confidence': 'field3',
            'ensemble_confidence': 'field4',
            'final_confidence': 'field5',
            'image_quality': 'field6',
            'processing_time_ms': 'field7',
            'location': 'field8'  # GPS coordinates or location name
        }
    
    def upload_detection_result(self, 
                               detection_data: Dict,
                               metadata: Optional[Dict] = None) -> bool:
        """
        Upload single detection result to ThingSpeak
        
        Args:
            detection_data: Dictionary with detection metrics
            metadata: Optional metadata (location, timestamp, etc.)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare ThingSpeak payload
            payload = {
                'api_key': self.write_key,
                'field1': detection_data.get('detection_count', 0),
                'field2': round(detection_data.get('yolov8_conf', 0), 3),
                'field3': round(detection_data.get('mobilenetv2_conf', 0), 3),
                'field4': round(detection_data.get('ensemble_conf', 0), 3),
                'field5': round(detection_data.get('final_conf', 0), 3),
                'field6': round(detection_data.get('image_quality', 0), 3),
                'field7': int(detection_data.get('processing_time', 0)),
                'field8': metadata.get('location', '') if metadata else ''
            }
            
            # Send to ThingSpeak
            response = requests.post(
                f"{self.base_url}/update",
                data=payload,
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info(f"✓ Data uploaded to ThingSpeak. Entry ID: {response.text}")
                return True
            else:
                logger.error(f"✗ ThingSpeak upload failed: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Network error uploading to ThingSpeak: {e}")
            return False
        except Exception as e:
            logger.error(f"✗ Error uploading to ThingSpeak: {e}")
            return False
    
    def batch_upload(self, results_list: list) -> int:
        """
        Upload multiple results to ThingSpeak
        
        Args:
            results_list: List of detection results
            
        Returns:
            Number of successfully uploaded entries
        """
        successful = 0
        for result in results_list:
            if self.upload_detection_result(result):
                successful += 1
            time.sleep(0.5)  # Rate limiting (ThingSpeak allows 1/15 sec)
        
        logger.info(f"Batch upload complete: {successful}/{len(results_list)} successful")
        return successful
    
    def read_channel_data(self, results: int = 100) -> Optional[list]:
        """
        Read historical data from ThingSpeak channel
        
        Args:
            results: Number of recent entries to retrieve
            
        Returns:
            List of data entries or None if failed
        """
        try:
            url = f"{self.base_url}/channels/{self.channel_id}/feeds.json"
            params = {'api_key': self.write_key, 'results': results}
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get('feeds', [])
            else:
                logger.error(f"Failed to read channel: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error reading ThingSpeak data: {e}")
            return None
    
    def create_alert(self, threshold: float, field_number: int) -> bool:
        """
        Create alert if confidence exceeds threshold
        
        Args:
            threshold: Confidence threshold for alert
            field_number: Which field to monitor
            
        Returns:
            True if alert created successfully
        """
        try:
            # This would integrate with ThingSpeak's alert service
            # Implementation depends on ThingSpeak tier
            logger.info(f"Alert configured: field{field_number} > {threshold}")
            return True
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            return False


class LocalDataCache:
    """
    Local caching for offline operation
    Syncs with ThingSpeak when connection restored
    """
    
    def __init__(self, cache_file: str = "thingspeak_cache.json"):
        self.cache_file = cache_file
        self.cache = self._load_cache()
    
    def _load_cache(self) -> list:
        """Load cached data from file"""
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def _save_cache(self):
        """Save cache to file"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def add(self, data: Dict):
        """Add data to cache"""
        self.cache.append({
            'timestamp': datetime.now().isoformat(),
            'data': data
        })
        self._save_cache()
    
    def get_all(self) -> list:
        """Get all cached data"""
        return self.cache
    
    def clear(self):
        """Clear cache after successful upload"""
        self.cache = []
        self._save_cache()
```

#### Step 2: Integrate with inference.py

```python
# Add to inference.py

from iot_integration import ThingSpeakUploader, LocalDataCache

class MicroplasticsDetectionPipeline:
    """Complete inference pipeline with ThingSpeak integration"""
    
    def __init__(self, config_dict: Optional[Dict] = None,
                 thingspeak_channel_id: Optional[str] = None,
                 thingspeak_write_key: Optional[str] = None):
        """Initialize pipeline with optional ThingSpeak"""
        
        # ... existing initialization code ...
        
        # Initialize ThingSpeak uploader if credentials provided
        self.thingspeak = None
        self.offline_cache = None
        
        if thingspeak_channel_id and thingspeak_write_key:
            self.thingspeak = ThingSpeakUploader(
                thingspeak_channel_id,
                thingspeak_write_key
            )
            self.offline_cache = LocalDataCache()
            logger.info("✓ ThingSpeak integration enabled")
    
    def process_image_with_cloud_sync(self, image_path: str) -> Tuple[Dict, np.ndarray]:
        """Process image and sync results with ThingSpeak"""
        
        # Existing processing
        results, vis_image = self.process_image(image_path)
        
        # Upload to ThingSpeak if enabled
        if self.thingspeak and results:
            metadata = {
                'location': 'River_Monitoring_Station_1',
                'timestamp': datetime.now().isoformat()
            }
            
            if not self.thingspeak.upload_detection_result(
                results, 
                metadata
            ):
                # Cache locally if upload fails
                self.offline_cache.add(results)
                logger.warning("⚠ Stored in local cache (offline)")
        
        return results, vis_image
    
    def sync_offline_data(self) -> bool:
        """Sync cached data to ThingSpeak when connection restored"""
        if not self.thingspeak or not self.offline_cache:
            return False
        
        cached_data = self.offline_cache.get_all()
        if cached_data:
            logger.info(f"Syncing {len(cached_data)} cached entries to ThingSpeak...")
            uploaded = self.thingspeak.batch_upload(cached_data)
            
            if uploaded == len(cached_data):
                self.offline_cache.clear()
                logger.info("✓ Cache synced successfully")
                return True
        
        return False
```

#### Step 3: Update config.py

```python
# Add to config.py

# ═══════════════════════════════════════════════════════════════════════════
# THINGSPEAK IOT INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════

# ThingSpeak Channel Configuration
THINGSPEAK_ENABLED = True  # Set to False to disable cloud sync

# Get these from your ThingSpeak account
# 1. Go to https://thingspeak.com
# 2. Create a new channel
# 3. Copy Channel ID and Write API Key
THINGSPEAK_CHANNEL_ID = os.getenv('THINGSPEAK_CHANNEL_ID', 'YOUR_CHANNEL_ID')
THINGSPEAK_WRITE_KEY = os.getenv('THINGSPEAK_WRITE_KEY', 'YOUR_WRITE_KEY')

# Update interval (seconds)
THINGSPEAK_UPDATE_INTERVAL = 15

# Offline caching
OFFLINE_CACHE_ENABLED = True
OFFLINE_CACHE_FILE = "thingspeak_cache.json"
```

#### Step 4: Update .env file

```
# Add to .env

# ThingSpeak IoT Configuration
THINGSPEAK_CHANNEL_ID=2411999
THINGSPEAK_WRITE_KEY=ABC1DEF2GHI3
```

#### Step 5: Update main.py with cloud option

```python
# Add to main.py

def run_inference_with_cloud(image_path: Optional[str] = None,
                            image_dir: Optional[str] = None,
                            thingspeak: bool = False,
                            output_dir: str = "outputs"):
    """
    Run inference with optional ThingSpeak cloud sync
    
    Usage:
        python main.py inference --image path/to/image.jpg --cloud
        python main.py inference --image-dir data/test/ --cloud
    """
    
    logger = logging.getLogger(__name__)
    
    # Initialize pipeline
    thingspeak_creds = None
    if thingspeak:
        thingspeak_creds = {
            'channel_id': THINGSPEAK_CHANNEL_ID,
            'write_key': THINGSPEAK_WRITE_KEY
        }
    
    pipeline = MicroplasticsDetectionPipeline(
        thingspeak_channel_id=thingspeak_creds.get('channel_id') if thingspeak_creds else None,
        thingspeak_write_key=thingspeak_creds.get('write_key') if thingspeak_creds else None
    )
    
    # Process and sync
    if thingspeak_creds:
        logger.info("🌐 Cloud sync enabled (ThingSpeak)")
    
    # ... existing inference code ...

# Update argparse
inference_parser.add_argument('--cloud', action='store_true',
                            help='Enable ThingSpeak cloud sync')
```

---

## PART 2: ADDING TENSORFLOW ALTERNATIVE

### Create tensorflow_backend.py

```python
# tensorflow_backend.py - Optional TensorFlow implementation

import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D
from tensorflow.keras.models import Model
import tensorflow.lite as tflite

class TensorFlowMobileNetV2:
    """TensorFlow alternative implementation"""
    
    def __init__(self, num_classes=2):
        self.num_classes = num_classes
        self.model = self._build_model()
    
    def _build_model(self):
        """Build MobileNetV2 with TensorFlow"""
        base_model = MobileNetV2(
            input_shape=(224, 224, 3),
            include_top=False,
            weights='imagenet'
        )
        
        # Freeze base layers
        base_model.trainable = False
        
        # Add custom top
        x = GlobalAveragePooling2D()(base_model.output)
        x = Dropout(0.2)(x)
        outputs = Dense(self.num_classes, activation='softmax')(x)
        
        model = Model(inputs=base_model.input, outputs=outputs)
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def export_to_tflite(self, output_path):
        """Export to TensorFlow Lite for mobile"""
        converter = tflite.TFLiteConverter.from_keras_model(self.model)
        tflite_model = converter.convert()
        
        with open(output_path, 'wb') as f:
            f.write(tflite_model)
        
        print(f"✓ Model exported to {output_path}")
```

---

## PART 3: ADDING DOCKER CONTAINERIZATION

### Create Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p data/{train,val,test} models outputs

# Run inference by default
ENTRYPOINT ["python", "main.py"]
CMD ["config"]
```

### Create docker-compose.yml

```yaml
version: '3.8'

services:
  microplastics-detection:
    build: .
    container_name: microplastics-detection
    volumes:
      - ./data:/app/data
      - ./outputs:/app/outputs
      - ./models:/app/models
    environment:
      - THINGSPEAK_CHANNEL_ID=YOUR_CHANNEL_ID
      - THINGSPEAK_WRITE_KEY=YOUR_WRITE_KEY
    command: ["inference", "--image-dir", "data/test/"]
```

---

## PART 4: ADDING FLASK WEB API

### Create flask_api.py

```python
from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import io
from PIL import Image
import json

app = Flask(__name__)
CORS(app)

pipeline = MicroplasticsDetectionPipeline()

@app.route('/api/predict', methods=['POST'])
def predict():
    """REST endpoint for prediction"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    image = Image.open(io.BytesIO(file.read()))
    
    # Predict
    results, _ = pipeline.process_image_pil(image)
    
    return jsonify(results)

@app.route('/api/status', methods=['GET'])
def status():
    """Check system status"""
    return jsonify({'status': 'operational'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

---

## SUMMARY: WHAT WAS INCLUDED VS WHAT CAN BE ADDED

| Component | Status | Lines of Code | Complexity |
|-----------|--------|---------------|-----------|
| PyTorch (core) | ✅ Included | 300+ | High |
| OpenCV (preprocessing) | ✅ Included | 200+ | High |
| YOLOv8 (detection) | ✅ Included | 150+ | High |
| XGBoost (ensemble) | ✅ Included | 100+ | Medium |
| MobileNetV2 (classification) | ✅ Included | 200+ | High |
| Visualization (Matplotlib) | ✅ Included | 100+ | Medium |
| **ThingSpeak Integration** | ❌ Can add | 200+ | Medium |
| **TensorFlow Alternative** | ❌ Can add | 150+ | Medium |
| **Docker Container** | ❌ Can add | 30 lines | Low |
| **Flask Web API** | ❌ Can add | 100+ | Medium |
| **Mobile App** | ❌ Can add | 500+ | High |

**Quick Addition Priority:**
1. ThingSpeak (1-2 hours) - Adds IoT capability
2. Docker (30 minutes) - Production deployment
3. Flask API (1 hour) - Web accessibility
4. TensorFlow (2-3 hours) - Alternative backend
