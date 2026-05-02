import os
import shutil
from pathlib import Path
import glob

def clean_dataset(base_path):
    # Create new directories for organized dataset
    train_images = Path(base_path) / "clean_dataset" / "train" / "images"
    train_labels = Path(base_path) / "clean_dataset" / "train" / "labels"
    val_images = Path(base_path) / "clean_dataset" / "val" / "images"
    val_labels = Path(base_path) / "clean_dataset" / "val" / "labels"
    
    # Create directories if they don't exist
    for dir_path in [train_images, train_labels, val_images, val_labels]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Process Training images and labels
    train_path = Path(base_path) / "Resources" / "1_Training"
    val_path = Path(base_path) / "Resources" / "2_Validation"
    
    # Process training set
    for img_file in train_path.glob("**/*.jpg"):
        if img_file.name.startswith("x-Clean"):
            continue  # Skip clean water images
            
        # Get the corresponding label file
        label_file = train_path / "labels" / f"{img_file.stem}.txt"
        
        if not label_file.exists():
            print(f"Warning: No label file for {img_file.name}")
            continue
        
        # Copy files to new location
        shutil.copy2(img_file, train_images / img_file.name)
        shutil.copy2(label_file, train_labels / f"{img_file.stem}.txt")
    
    # Process validation set
    for img_file in val_path.glob("**/*.jpg"):
        if img_file.name.startswith("x-Clean"):
            continue  # Skip clean water images
            
        # Get the corresponding label file
        label_file = val_path / "labels" / f"{img_file.stem}.txt"
        
        if not label_file.exists():
            print(f"Warning: No label file for {img_file.name}")
            continue
        
        # Copy files to new location
        shutil.copy2(img_file, val_images / img_file.name)
        shutil.copy2(label_file, val_labels / f"{img_file.stem}.txt")
    
    # Create new dataset.yaml
    dataset_yaml = f"""
path: {Path(base_path) / 'clean_dataset'}  # dataset root dir
train: train/images  # train images (relative to 'path')
val: val/images  # val images (relative to 'path')

# Classes
names:
  0: Microplastic  # class names
"""
    
    with open(Path(base_path) / "clean_dataset" / "dataset.yaml", "w") as f:
        f.write(dataset_yaml)
    
    print("Dataset cleaned and organized successfully!")

if __name__ == "__main__":
    base_path = os.path.dirname(os.path.abspath(__file__))
    clean_dataset(base_path)