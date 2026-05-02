"""
Create YOLO label files for clean (non-microplastic) images where labels are missing.
Strategy:
- For any image named `clean_water_train_*.jpg` or `clean_water_val_*.jpg` check for a corresponding .txt label.
- If missing, create a label with class `1` and bbox covering the whole image: "1 0.5 0.5 1.0 1.0"
- Print summary counts and list up to 10 missing labels created.

Note: Full-image bbox (1.0) marks the whole image as a NonMicroplastic object. This is a simple way to provide detection labels for the negative class; you can refine later with tighter boxes if desired.
"""
import os
from pathlib import Path

BASE = Path(__file__).resolve().parent
DS = BASE / 'clean_dataset'

created = []
skipped = []
missing_image_labels = []

for split in ('train', 'val'):
    images_dir = DS / split / 'images'
    labels_dir = DS / split / 'labels'
    labels_dir.mkdir(parents=True, exist_ok=True)

    if not images_dir.exists():
        print(f"Warning: images dir does not exist: {images_dir}")
        continue

    images = sorted(images_dir.glob('*.jpg'))
    for img in images:
        name = img.stem
        # expected label path
        lbl = labels_dir / f"{name}.txt"
        # If image is a clean_water image, ensure it has a label of class 1
        if name.startswith('clean_water_'):
            if not lbl.exists():
                # write a single label: class_id x_center y_center width height (normalized)
                with open(lbl, 'w') as f:
                    f.write('1 0.5 0.5 1.0 1.0\n')
                created.append(str(lbl.relative_to(BASE)))
            else:
                # Optionally check whether label contains class 1; if not, append class 1
                with open(lbl, 'r+') as f:
                    content = f.read().strip()
                    if content == '':
                        f.write('1 0.5 0.5 1.0 1.0\n')
                        created.append(str(lbl.relative_to(BASE)))
                    else:
                        # check if class 1 already present
                        if any(line.split()[0] == '1' for line in content.splitlines() if line):
                            skipped.append(str(lbl.relative_to(BASE)))
                        else:
                            # append the non-microplastic label
                            f.write('\n1 0.5 0.5 1.0 1.0\n')
                            created.append(str(lbl.relative_to(BASE)))
        else:
            # non-clean images: ensure a label exists (we don't change them here)
            if not lbl.exists():
                missing_image_labels.append(str(img.relative_to(BASE)))

# Summary
print('\nSummary:')
print(f'Clean-image labels created: {len(created)}')
if created:
    for p in created[:10]:
        print('  created:', p)
if skipped:
    print(f'Clean-image labels already present (skipped): {len(skipped)}')
if missing_image_labels:
    print(f'WARNING: {len(missing_image_labels)} non-clean images missing labels (listed up to 10):')
    for p in missing_image_labels[:10]:
        print('  missing label for image:', p)

# count images and labels per split
for split in ('train', 'val'):
    images_dir = DS / split / 'images'
    labels_dir = DS / split / 'labels'
    imgs = len(list(images_dir.glob('*.jpg'))) if images_dir.exists() else 0
    lbls = len(list(labels_dir.glob('*.txt'))) if labels_dir.exists() else 0
    print(f"{split}: images={imgs}, labels={lbls}")

print('\nDone.')
