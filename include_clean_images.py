import shutil
from pathlib import Path

BASE = Path(__file__).resolve().parent
RES = BASE / 'Resources'
DS = BASE / 'clean_dataset'

pairs = [
    (RES / '1_Training' / '1_Clean_Water', DS / 'train' / 'images', DS / 'train' / 'labels'),
    (RES / '2_Validation' / '1_Clean_Water', DS / 'val' / 'images', DS / 'val' / 'labels'),
]

created = 0
updated = 0
for src_dir, dst_img_dir, dst_lbl_dir in pairs:
    if not src_dir.exists():
        print(f"Source folder not found: {src_dir}")
        continue
    dst_img_dir.mkdir(parents=True, exist_ok=True)
    dst_lbl_dir.mkdir(parents=True, exist_ok=True)

    for img in sorted(src_dir.glob('*.jpg')):
        dst_img = dst_img_dir / img.name
        # copy image if not exists
        if not dst_img.exists():
            shutil.copy2(img, dst_img)
            created += 1
        else:
            updated += 1
        # check for existing label in Resources (labels may be in Resources/1_Training/labels)
        # original labels may have been renamed earlier to match images; try in Resources/1_Training/labels and Resources/2_Validation/labels
        src_label_candidates = [
            src_dir.parent / 'labels' / f"{img.stem}.txt",
            RES / '1_Training' / 'labels' / f"{img.stem}.txt",
            RES / '2_Validation' / 'labels' / f"{img.stem}.txt",
            RES / '1_Training' / '1_Clean_Water' / f"{img.stem}.txt",
            RES / '2_Validation' / '1_Clean_Water' / f"{img.stem}.txt",
        ]
        dst_label = dst_lbl_dir / f"{img.stem}.txt"
        found = False
        for cand in src_label_candidates:
            if cand.exists():
                shutil.copy2(cand, dst_label)
                found = True
                break
        if not found:
            # create a full-image label marking NonMicroplastic class 1
            with open(dst_label, 'w') as f:
                f.write('1 0.5 0.5 1.0 1.0\n')

print(f"Images copied: {created}, already existed: {updated}")
# print counts
for split in ('train','val'):
    imgs = len(list((DS / split / 'images').glob('*.jpg'))) if (DS / split / 'images').exists() else 0
    lbls = len(list((DS / split / 'labels').glob('*.txt'))) if (DS / split / 'labels').exists() else 0
    print(f"{split}: images={imgs}, labels={lbls}")
print('Done.')
