import os
import cv2
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

# 1. CONFIGURACIÓN DE RUTAS
# Ajusta esta ruta si tu carpeta se llama diferente
DATASET_DIR = r"C:\Users\Gissell\OneDrive\Documents\Universidad\8voCuatrimestre\Proyecto\agente-AI\agente-AI.gi\dataset_torax"
CATEGORIES = ["TORAX", "NO_TORAX"]
IMG_SIZE = 224 # Tamaño estándar para procesar

X = []
y = []

print("Cargando imágenes de TÓRAX vs NO_TÓRAX... Espera un momento.")

# 2. CARGAR Y PROCESAR IMÁGENES
for category in CATEGORIES:
    path = os.path.join(DATASET_DIR, category)
    class_num = CATEGORIES.index(category) # TORAX = 0, NO_TORAX = 1
    
    if not os.path.exists(path):
        print(f"❌ Error: No se encontró la carpeta {path}")
        continue

    for img_name in os.listdir(path):
        try:
            img_path = os.path.join(path, img_name)
            # Leer en escala de grises para que el KNN no tarde una eternidad
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            
            # Redimensionar
            img_resized = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
            
            # Aplanar la imagen (convertirla en un vector de una fila)
            X.append(img_resized.flatten())
            y.append(class_num)
        except Exception as e:
            # Si una imagen está corrupta, se la salta
            pass

X = np.array(X)
y = np.array(y)

print(f"Total imágenes cargadas: {len(X)}")
print(f"Tórax (0): {list(y).count(0)} | No Tórax (1): {list(y).count(1)}")

# 3. DIVISIÓN DE DATOS (80% Train, 10% Val, 10% Test)
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp)

print(f"Entrenamiento: {len(X_train)} | Validación: {len(X_val)} | Prueba: {len(X_test)}")

# 4. ENTRENAR MODELO KNN
K = 5
print(f"\nEntrenando KNN con K = {K}...")
knn = KNeighborsClassifier(n_neighbors=K)
knn.fit(X_train, y_train)

# 5. EVALUACIÓN EN VALIDACIÓN
y_val_pred = knn.predict(X_val)
print(f"Accuracy Validación: {accuracy_score(y_val, y_val_pred):.4f}")

# 6. RESULTADOS FINALES EN PRUEBA
y_test_pred = knn.predict(X_test)
print("\n======================")
print("RESULTADOS FINALES (TEST)")
print("======================")
print(f"Accuracy: {accuracy_score(y_test, y_test_pred) * 100:.2f}%")

print("\nMatriz de confusión:")
print(confusion_matrix(y_test, y_test_pred))

print("\nReporte de Clasificación:")
print(classification_report(y_test, y_test_pred, target_names=CATEGORIES))