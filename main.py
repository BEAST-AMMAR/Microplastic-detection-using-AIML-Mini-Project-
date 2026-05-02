#!/usr/bin/env python3
# ==================================================================================
# MINIPROJECT 1.0 - MAIN CLI APPLICATION
# Microplastics Detection System - Command Line Interface
# ==================================================================================

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
import yaml
import json
import numpy as np
import time
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from data.dataset_loader import DatasetLoader
from models.yolo_detector import YOLODetector
from models.mobilenet_classifier import MobileNetClassifier
from models.ensemble_model import EnsembleModel


class MicroplasticsDetector:
    """Main application class for microplastics detection"""

    def __init__(self, config_path: str = 'config.yaml'):
        """Initialize the detector"""
        self.config_path = config_path
        self.config = self.load_config()
        self.setup_logging()

        # Initialize components
        self.dataset_loader = DatasetLoader(config_path)
        self.yolo_detector = None
        self.mobilenet_classifier = None
        self.ensemble_model = None

        print("🎯 MINIProject 1.0 - Microplastics Detection System")
        print("=" * 60)

    def load_config(self) -> Dict[str, Any]:
        """Load configuration file"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            print(f"✅ Configuration loaded from {self.config_path}")
            return config
        except FileNotFoundError:
            print(f"❌ Configuration file not found: {self.config_path}")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"❌ Error parsing configuration: {e}")
            sys.exit(1)

    def setup_logging(self):
        """Setup logging configuration"""
        log_config = self.config.get('logging', {})
        logging.basicConfig(
            level=getattr(logging, log_config.get('level', 'INFO')),
            format=log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            handlers=[
                logging.FileHandler(log_config.get('filename', 'outputs/logs/app.log')),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def initialize_models(self):
        """Initialize all models"""
        print("\n🔧 Initializing models...")

        # Initialize YOLO detector
        try:
            self.yolo_detector = YOLODetector(config_path=self.config_path)
            print("✅ YOLO detector initialized")
        except Exception as e:
            print(f"❌ Failed to initialize YOLO detector: {e}")
            return False

        # Initialize MobileNet classifier
        try:
            self.mobilenet_classifier = MobileNetClassifier(config_path=self.config_path)
            self.mobilenet_classifier.build_model()
            print("✅ MobileNet classifier initialized")
        except Exception as e:
            print(f"❌ Failed to initialize MobileNet classifier: {e}")
            self.mobilenet_classifier = None

        # Initialize ensemble model
        try:
            self.ensemble_model = EnsembleModel(config_path=self.config_path)
            print("✅ Ensemble model initialized")
        except Exception as e:
            print(f"❌ Failed to initialize ensemble model: {e}")
            self.ensemble_model = None

        return True

    def download_dataset(self, dataset_name: str = "Kili/plastic_in_river"):
        """Download and prepare dataset"""
        print(f"\n📥 Downloading dataset: {dataset_name}")
        try:
            output_dir = self.dataset_loader.download_and_prepare_dataset(dataset_name)
            print(f"✅ Dataset downloaded and prepared in: {output_dir}")
            return True
        except Exception as e:
            print(f"❌ Failed to download dataset: {e}")
            return False

    def prepare_data(self, source_dir: Optional[str] = None, output_dir: Optional[str] = None):
        """Prepare data for training"""
        # Use config defaults when args are not provided
        source_dir = source_dir or self.config.get('data', {}).get('train_dir') or self.config.get('data', {}).get('raw_dir')
        print(f"\n🔄 Preparing data from: {source_dir}")
        try:
            if output_dir is None:
                output_dir = self.config.get('data', {}).get('processed_dir')

            # Split dataset
            splits = self.dataset_loader.split_dataset(source_dir)
            print(f"✅ Data split: {len(splits['train'])} train, {len(splits['val'])} val, {len(splits['test'])} test")

            # Create YOLO labels
            labels_dir = self.dataset_loader.prepare_yolo_labels(source_dir, output_dir)
            print(f"✅ YOLO labels prepared in: {labels_dir}")

            return True
        except Exception as e:
            print(f"❌ Failed to prepare data: {e}")
            return False

    def train_yolo(self, data_yaml: str, **kwargs):
        """Train YOLO model"""
        print("\n🚀 Training YOLO model...")
        if not self.yolo_detector:
            if not self.initialize_models():
                return False

        try:
            start_time = time.time()
            metrics = self.yolo_detector.train(data_yaml, **kwargs)
            training_time = time.time() - start_time

            print(f"   ⏱️ Training time: {training_time:.2f}s")
            print(f"   📊 Final mAP: {metrics.get('metrics/mAP50-95', 'N/A')}")
            return True
        except Exception as e:
            print(f"❌ YOLO training failed: {e}")
            return False

    def train_mobilenet(self, train_dir: Optional[str] = None, val_dir: Optional[str] = None, **kwargs):
        """Train MobileNet model"""
        print("\n🚀 Training MobileNet model...")
        if not self.mobilenet_classifier:
            if not self.initialize_models():
                return False

        # Use config defaults if arguments are not provided
        train_dir = train_dir or self.config.get('data', {}).get('train_dir') or self.config.get('data', {}).get('raw_dir')
        val_dir = val_dir or self.config.get('data', {}).get('val_dir') or str(Path(train_dir).parent / '2_Validation')

        try:
            # Create data generators
            train_gen, val_gen, _ = self.mobilenet_classifier.create_data_generators(
                train_dir, val_dir
            )

            start_time = time.time()
            history = self.mobilenet_classifier.train(train_gen, val_gen, **kwargs)
            training_time = time.time() - start_time

            final_accuracy = history.history['val_accuracy'][-1]
            print(f"   ⏱️ Training time: {training_time:.2f}s")
            print(f"   🎯 Final validation accuracy: {final_accuracy:.4f}")
            return True
        except Exception as e:
            print(f"❌ MobileNet training failed: {e}")
            return False

    def train_ensemble(self, train_features: np.ndarray, train_labels: np.ndarray, **kwargs):
        """Train ensemble model"""
        print("\n🚀 Training ensemble model...")
        if not self.ensemble_model:
            if not self.initialize_models():
                return False

        try:
            start_time = time.time()
            metrics = self.ensemble_model.train(train_features, train_labels, **kwargs)
            training_time = time.time() - start_time

            print(f"   ⏱️ Training time: {training_time:.2f}s")
            print(f"   📊 Ensemble training metrics: {metrics}")
            return True
        except Exception as e:
            print(f"❌ Ensemble training failed: {e}")
            return False

    def predict_single(self, image_path: str, save_results: bool = True):
        """Predict on single image"""
        print(f"\n🔍 Analyzing image: {image_path}")
        if not self.yolo_detector:
            if not self.initialize_models():
                return None

        try:
            # YOLO detection
            yolo_detections = self.yolo_detector.detect(image_path)
            print(f"   📍 YOLO detections: {len(yolo_detections)}")

            # Check if we have ensemble model
            if self.ensemble_model and self.mobilenet_classifier:
                # MobileNet classification (simplified - would need proper ROI extraction)
                # For demo, we'll use dummy predictions
                mobilenet_predictions = [(0, 0.5)] * len(yolo_detections)

                # Ensemble prediction
                ensemble_score = self.ensemble_model.predict_single(
                    yolo_detections, mobilenet_predictions
                )
                microplastic_detected = ensemble_score > 0.5
            else:
                # YOLO-only prediction: assume microplastic if any detections
                microplastic_detected = len(yolo_detections) > 0
                ensemble_score = float(microplastic_detected)

            # Results
            results = {
                'image_path': image_path,
                'yolo_detections': len(yolo_detections),
                'ensemble_score': ensemble_score,
                'microplastic_detected': microplastic_detected,
                'timestamp': datetime.now().isoformat()
            }

            print(f"   🎯 Microplastic detected: {results['microplastic_detected']}")

            if save_results:
                self.save_results(results, image_path)

            return results

        except Exception as e:
            print(f"❌ Prediction failed: {e}")
            return None

    def predict_batch(self, image_dir: str, output_dir: Optional[str] = None, **kwargs):
        """Predict on batch of images"""
        print(f"\n🔍 Analyzing images in: {image_dir}")

        if output_dir is None:
            output_dir = self.config['output']['results_dir']

        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Find all images
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        image_paths = []
        for ext in image_extensions:
            image_paths.extend(Path(image_dir).glob(f"**/*{ext}"))
            image_paths.extend(Path(image_dir).glob(f"**/*{ext.upper()}"))

        if not image_paths:
            print(f"❌ No images found in {image_dir}")
            return False

        print(f"   📁 Found {len(image_paths)} images")

        # Process images
        results = []
        successful = 0

        for i, img_path in enumerate(image_paths):
            print(f"   🔄 Processing {i+1}/{len(image_paths)}: {img_path.name}")
            result = self.predict_single(str(img_path), save_results=False)
            if result:
                results.append(result)
                successful += 1

        # Save batch results
        batch_results = {
            'total_images': len(image_paths),
            'successful_predictions': successful,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }

        results_file = Path(output_dir) / 'batch_results.json'
        with open(results_file, 'w') as f:
            json.dump(batch_results, f, indent=2)

        print(f"\n✅ Batch processing completed: {successful}/{len(image_paths)} successful")
        print(f"   💾 Results saved to: {results_file}")

        return True

    def save_results(self, results: Dict[str, Any], image_path: str):
        """Save prediction results"""
        output_dir = Path(self.config['output']['results_dir'])
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save JSON results
        results_file = output_dir / f"{Path(image_path).stem}_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"   💾 Results saved to: {results_file}")

    def show_config(self):
        """Display current configuration"""
        print("\n⚙️  Current Configuration:")
        print("-" * 40)

        # System info
        print(f"Config file: {self.config_path}")
        print(f"Python version: {sys.version.split()[0]}")

        # Data config
        data_config = self.config.get('data', {})
        print(f"Data directory: {data_config.get('raw_dir', 'N/A')}")

        # Model config
        yolo_config = self.config.get('yolo', {})
        print(f"YOLO model: {yolo_config.get('model_variant', 'N/A')}")

        mobilenet_config = self.config.get('mobilenet', {})
        print(f"MobileNet input shape: {mobilenet_config.get('input_shape', 'N/A')}")

        ensemble_config = self.config.get('ensemble', {})
        print(f"Ensemble method: {ensemble_config.get('method', 'N/A')}")

        # Output config
        output_config = self.config.get('output', {})
        print(f"Output directory: {output_config.get('results_dir', 'N/A')}")

    def run_diagnostics(self):
        """Run system diagnostics"""
        print("\n🔍 Running system diagnostics...")
        print("-" * 40)

        # Check dependencies
        dependencies_ok = True

        try:
            import torch
            print(f"✅ PyTorch: {torch.__version__}")
            print(f"   CUDA available: {torch.cuda.is_available()}")
        except ImportError:
            print("❌ PyTorch not found")
            dependencies_ok = False

        try:
            import tensorflow as tf
            print(f"✅ TensorFlow: {tf.__version__}")
        except ImportError:
            print("❌ TensorFlow not found")
            dependencies_ok = False

        try:
            import cv2
            print(f"✅ OpenCV: {cv2.__version__}")
        except ImportError:
            print("❌ OpenCV not found")
            dependencies_ok = False

        try:
            import ultralytics
            print(f"✅ Ultralytics: {ultralytics.__version__}")
        except ImportError:
            print("❌ Ultralytics not found")
            dependencies_ok = False

        try:
            import xgboost
            print(f"✅ XGBoost: {xgboost.__version__}")
        except ImportError:
            print("❌ XGBoost not found")
            dependencies_ok = False

        # Check directories (derived from config where possible)
        dirs_ok = True
        data_cfg = self.config.get('data', {})
        output_cfg = self.config.get('output', {})

        required_dirs = [
            data_cfg.get('raw_dir', 'data/raw'),
            data_cfg.get('processed_dir', 'data/processed'),
            data_cfg.get('train_dir', None),
            data_cfg.get('val_dir', None),
            data_cfg.get('test_dir', None),
            output_cfg.get('models_dir', 'models'),
            output_cfg.get('results_dir', 'outputs/results'),
            output_cfg.get('logs_dir', 'outputs/logs')
        ]

        # Filter out None entries
        required_dirs = [d for d in required_dirs if d]

        for dir_path in required_dirs:
            if not Path(dir_path).exists():
                print(f"❌ Directory missing: {dir_path}")
                dirs_ok = False
            else:
                print(f"✅ Directory exists: {dir_path}")

        # Overall status
        if dependencies_ok and dirs_ok:
            print("\n✅ All diagnostics passed!")
            return True
        else:
            print("\n❌ Some issues found. Run setup scripts to fix.")
            return False


def create_parser():
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="MINIProject 1.0 - Microplastics Detection System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""
Examples:
  python main.py config
  python main.py download
  python main.py prepare --source-dir Resources/1_Training
  python main.py train-yolo --data-yaml data/datasets.yaml
  python main.py predict --image sample.jpg
  python main.py predict --image-dir Resources/3_Testing
    """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Config command
    subparsers.add_parser('config', help='Show current configuration')

    # Diagnostics command
    subparsers.add_parser('diagnostics', help='Run system diagnostics')

    # Download command
    download_parser = subparsers.add_parser('download', help='Download dataset')
    download_parser.add_argument('--dataset', default='Kili/plastic_in_river',
                                help='Dataset name to download')

    # Prepare command
    prepare_parser = subparsers.add_parser('prepare', help='Prepare data for training')
    prepare_parser.add_argument('--source-dir', required=False, default=None,
                               help='Source directory with raw data (defaults to config.data.train_dir)')
    prepare_parser.add_argument('--output-dir',
                               help='Output directory for processed data')

    # Train YOLO command
    train_yolo_parser = subparsers.add_parser('train-yolo', help='Train YOLO model')
    train_yolo_parser.add_argument('--data-yaml', required=False, default=None,
                                  help='Path to data YAML file (defaults to config.data.processed_dir/dataset.yaml)')
    train_yolo_parser.add_argument('--epochs', type=int,
                                  help='Number of epochs')
    train_yolo_parser.add_argument('--batch-size', type=int,
                                  help='Batch size')
    train_yolo_parser.add_argument('--learning-rate', type=float,
                                  help='Learning rate')

    # Train MobileNet command
    train_mobilenet_parser = subparsers.add_parser('train-mobilenet', help='Train MobileNet model')
    train_mobilenet_parser.add_argument('--train-dir', required=False, default=None,
                                       help='Training data directory (defaults to config.data.train_dir)')
    train_mobilenet_parser.add_argument('--val-dir', required=False, default=None,
                                       help='Validation data directory (defaults to config.data.val_dir)')
    train_mobilenet_parser.add_argument('--epochs', type=int,
                                       help='Number of epochs')
    train_mobilenet_parser.add_argument('--batch-size', type=int,
                                       help='Batch size')

    # Train ensemble command
    train_ensemble_parser = subparsers.add_parser('train-ensemble', help='Train ensemble model')
    train_ensemble_parser.add_argument('--train-features', required=True,
                                      help='Path to training features')
    train_ensemble_parser.add_argument('--train-labels', required=True,
                                      help='Path to training labels')

    # Predict command
    predict_parser = subparsers.add_parser('predict', help='Make predictions')
    predict_parser.add_argument('--image', help='Path to single image')
    predict_parser.add_argument('--image-dir', help='Directory with images')
    predict_parser.add_argument('--output-dir', help='Output directory for results')

    return parser


def main():
    """Main application entry point"""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize detector
    detector = MicroplasticsDetector()

    # Execute command
    if args.command == 'config':
        detector.show_config()

    elif args.command == 'diagnostics':
        success = detector.run_diagnostics()
        sys.exit(0 if success else 1)

    elif args.command == 'download':
        success = detector.download_dataset(args.dataset)
        sys.exit(0 if success else 1)

    elif args.command == 'prepare':
        print(f"🔄 Preparing data:")
        print(f"   - Source directory: {args.source_dir}")
        print(f"   - Output directory: {args.output_dir}")
        success = detector.prepare_data(args.source_dir, args.output_dir)
        if not success:
            print("❌ Data preparation failed")
        sys.exit(0 if success else 1)

    elif args.command == 'train-yolo':
        kwargs = {}
        if args.epochs:
            kwargs['epochs'] = args.epochs
        if args.batch_size:
            kwargs['batch_size'] = args.batch_size
        if args.learning_rate:
            kwargs['learning_rate'] = args.learning_rate

        # Default data_yaml to processed_dir/dataset.yaml if not provided
        data_yaml = args.data_yaml
        if not data_yaml:
            processed_dir = detector.config.get('data', {}).get('processed_dir')
            data_yaml = str(Path(processed_dir) / 'dataset.yaml') if processed_dir else 'data/dataset.yaml'

        print(f"🔄 Starting YOLO training with:")
        print(f"   - Data YAML: {data_yaml}")
        print(f"   - Epochs: {kwargs.get('epochs', 'default')}")
        print(f"   - Batch size: {kwargs.get('batch_size', 'default')}")
        print(f"   - Learning rate: {kwargs.get('learning_rate', 'default')}")

        success = detector.train_yolo(data_yaml, **kwargs)
        if not success:
            print("❌ YOLO training failed")
        sys.exit(0 if success else 1)

    elif args.command == 'train-mobilenet':
        kwargs = {}
        if args.epochs:
            kwargs['epochs'] = args.epochs
        if args.batch_size:
            kwargs['batch_size'] = args.batch_size

        success = detector.train_mobilenet(args.train_dir, args.val_dir, **kwargs)
        sys.exit(0 if success else 1)

    elif args.command == 'train-ensemble':
        # Load features and labels
        import numpy as np
        train_features = np.load(args.train_features)
        train_labels = np.load(args.train_labels)

        success = detector.train_ensemble(train_features, train_labels)
        sys.exit(0 if success else 1)

    elif args.command == 'predict':
        if args.image:
            result = detector.predict_single(args.image)
            if result is None:
                sys.exit(1)
        elif args.image_dir:
            success = detector.predict_batch(args.image_dir, args.output_dir)
            sys.exit(0 if success else 1)
        else:
            print("❌ Must specify either --image or --image-dir")
            sys.exit(1)

    else:
        print(f"❌ Unknown command: {args.command}")
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
