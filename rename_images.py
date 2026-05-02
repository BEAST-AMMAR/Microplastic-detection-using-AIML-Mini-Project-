import os
from pathlib import Path
import shutil

def rename_images(base_path):
    resources_path = Path(base_path) / "Resources"
    
    # Counter for each type of image
    counters = {
        'clean_water': 1,
        'microplastic': 1
    }
    
    # Function to rename files in a directory
    def process_directory(dir_path, is_training=True):
        dataset_type = "train" if is_training else "val"
        
        # Process Clean Water images
        clean_water_dir = dir_path / "1_Clean_Water"
        if clean_water_dir.exists():
            for img_file in clean_water_dir.glob("*.jpg"):
                new_name = f"clean_water_{dataset_type}_{counters['clean_water']:04d}.jpg"
                print(f"Renaming {img_file.name} to {new_name}")
                img_file.rename(clean_water_dir / new_name)
                counters['clean_water'] += 1
        
        # Process Microplastic images
        microplastic_dir = dir_path / "2_Microplastics"
        if microplastic_dir.exists():
            for img_file in microplastic_dir.glob("*.jpg"):
                new_name = f"microplastic_{dataset_type}_{counters['microplastic']:04d}.jpg"
                print(f"Renaming {img_file.name} to {new_name}")
                img_file.rename(microplastic_dir / new_name)
                counters['microplastic'] += 1
                
                # Rename corresponding label file if it exists
                label_file = dir_path / "labels" / f"{img_file.stem}.txt"
                if label_file.exists():
                    new_label_name = f"{new_name[:-4]}.txt"
                    label_file.rename(dir_path / "labels" / new_label_name)
    
    # Process Training directory
    training_dir = resources_path / "1_Training"
    if training_dir.exists():
        print("\nProcessing Training Directory...")
        process_directory(training_dir, True)
    
    # Reset counters for validation set
    counters = {
        'clean_water': 1,
        'microplastic': 1
    }
    
    # Process Validation directory
    validation_dir = resources_path / "2_Validation"
    if validation_dir.exists():
        print("\nProcessing Validation Directory...")
        process_directory(validation_dir, False)
    
    print("\nImage renaming completed successfully!")

if __name__ == "__main__":
    base_path = os.path.dirname(os.path.abspath(__file__))
    rename_images(base_path)