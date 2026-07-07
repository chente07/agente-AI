import os
import cv2
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    classification_report,
    ConfusionMatrixDisplay
)

# ============================================================
# CONFIGURACIÓN
# ============================================================

ruta_dataset ="dataset_teste3"

EXTENSIONES_VALIDAS = (".png", ".jpg", ".jpeg")

# ============================================================
# CARGA DE IMÁGENES
# ============================================================

X = []
y = []

for clase in ["NORMAL", "NEUMONIA"]:

    ruta_clase = os.path.join(ruta_dataset, clase)

    etiqueta = 0 if clase == "NORMAL" else 1

    for archivo in os.listdir(ruta_clase):

        if not archivo.lower().endswith(EXTENSIONES_VALIDAS):
            continue

        ruta_imagen = os.path.join(ruta_clase, archivo)

        imagen = cv2.imread(
            ruta_imagen,
            cv2.IMREAD_GRAYSCALE
        )

        if imagen is None:
            continue

        # Resolución requerida
        imagen = cv2.resize(imagen, (224, 224))

        vector = imagen.flatten()

        X.append(vector)
        y.append(etiqueta)

X = np.array(X)
y = np.array(y)

print("Total imágenes:", len(X))

# ============================================================
# DIVISIÓN
# 80% entrenamiento
# 10% validación
# 10% prueba
# ============================================================

X_train, X_temp, y_train, y_temp = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

X_val, X_test, y_val, y_test = train_test_split(
    X_temp,
    y_temp,
    test_size=0.50,
    random_state=42,
    stratify=y_temp
)

print("Entrenamiento:", len(X_train))
print("Validación:", len(X_val))
print("Prueba:", len(X_test))

# ============================================================
# ENTRENAMIENTO KNN
# ============================================================

K = 5

modelo = KNeighborsClassifier(
    n_neighbors=K
)

modelo.fit(X_train, y_train)

print(f"\nKNN entrenado con K = {K}")

# ============================================================
# VALIDACIÓN
# ============================================================

pred_val = modelo.predict(X_val)

acc_val = accuracy_score(
    y_val,
    pred_val
)

print("\nAccuracy Validación:")
print(acc_val)

# ============================================================
# PRUEBA FINAL
# ============================================================

y_pred = modelo.predict(X_test)

acc_test = accuracy_score(
    y_test,
    y_pred
)

print("\n======================")
print("RESULTADOS FINALES")
print("======================")
print(f"Accuracy: {acc_test*100:.2f}%")

matriz = confusion_matrix(
    y_test,
    y_pred
)

print("\nMatriz de confusión:")
print(matriz)

print("\nReporte:")
print(
    classification_report(
        y_test,
        y_pred,
        target_names=[
            "NORMAL",
            "NEUMONIA"
        ]
    )
)

# ============================================================
# MATRIZ DE CONFUSIÓN
# ============================================================

disp = ConfusionMatrixDisplay(
    confusion_matrix=matriz,
    display_labels=[
        "NORMAL",
        "NEUMONIA"
    ]
)

disp.plot()
plt.title("KNN - Pulmones")
plt.show()