import pandas as pd
import os
from pathlib import Path

def convert_to_yolo_format(row):
    """Convert a row of annotations to YOLO format"""
    # YOLO format is: class_id center_x center_y width height
    # All normalized between 0 and 1
    width = float(row['width'])
    height = float(row['height'])
    
    # Convert to normalized coordinates
    x_min = float(row['xmin'])
    y_min = float(row['ymin'])
    x_max = float(row['xmax'])
    y_max = float(row['ymax'])
    
    x_center = ((x_min + x_max) / 2) / width
    y_center = ((y_min + y_max) / 2) / height
    box_width = (x_max - x_min) / width
    box_height = (y_max - y_min) / height
    
    # Class id is 0 for Microplastic
    class_id = 0
    
    return f"{class_id} {x_center:.6f} {y_center:.6f} {box_width:.6f} {box_height:.6f}"

def main():
    # Read the annotations
    train_df = pd.read_csv('Resources/Training_annotations.csv')
    val_df = pd.read_csv('Resources/Validation_annotations.csv')

    # Process each dataset split
    for split, df in [('1_Training', train_df), ('2_Validation', val_df)]:
        split_path = Path(f'Resources/{split}')
        
        # Create labels directory
        labels_path = split_path / 'labels'
        labels_path.mkdir(exist_ok=True, parents=True)
        
        print(f"\nProcessing {split}...")
        # Group by filename to create one label file per image
        for filename, group in df.groupby('filename'):
            # Extract base name and create label file path
            base_name = str(filename).replace('.jpg', '')
            label_file = labels_path / f"{base_name}.txt"
            
            # Convert all annotations for this image to YOLO format
            with open(label_file, 'w') as f:
                for _, row in group.iterrows():
                    yolo_format = convert_to_yolo_format(row)
                    f.write(yolo_format + '\n')
            print(f"Created labels for {filename}")

    print("\nAnnotation conversion complete!")
    print("Labels have been created in:")
    print(f"- Resources/1_Training/labels/")
    print(f"- Resources/2_Validation/labels/")

if __name__ == '__main__':
    main()

print("✅ Completed converting annotations to YOLO format")