import os
import random
import shutil

# ========= RUTAS =========

origen = r"C:\Users\Gissell\OneDrive\Documents\Universidad\8voCuatrimestre\Proyecto\agente-AI\agente-AI.gi\dataset_torax"

destino = r"C:\Users\Gissell\OneDrive\Documents\Universidad\8voCuatrimestre\Proyecto\agente-AI\agente-AI.gi\dataset_torax_yolo"

# =========================

random.seed(42)

clases = ["TORAX", "NO_TORAX"]

for clase in clases:

    carpeta_origen = os.path.join(origen, clase)

    imagenes = os.listdir(carpeta_origen)

    random.shuffle(imagenes)

    total = len(imagenes)

    train = int(total * 0.80)
    val = int(total * 0.10)

    train_imgs = imagenes[:train]
    val_imgs = imagenes[train:train+val]
    test_imgs = imagenes[train+val:]

    for carpeta in ["train", "val", "test"]:
        os.makedirs(
            os.path.join(destino, carpeta, clase),
            exist_ok=True
        )

    for img in train_imgs:
        shutil.copy2(
            os.path.join(carpeta_origen, img),
            os.path.join(destino, "train", clase, img)
        )

    for img in val_imgs:
        shutil.copy2(
            os.path.join(carpeta_origen, img),
            os.path.join(destino, "val", clase, img)
        )

    for img in test_imgs:
        shutil.copy2(
            os.path.join(carpeta_origen, img),
            os.path.join(destino, "test", clase, img)
        )

    print(f"\n{clase}")
    print(f"Train: {len(train_imgs)}")
    print(f"Val: {len(val_imgs)}")
    print(f"Test: {len(test_imgs)}")

print("\nDataset dividido correctamente.")