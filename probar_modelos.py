from ultralytics import YOLO


modelo_torax = YOLO("clasificador/ml_models/modelo_torax.pt")
modelo_neumonia = YOLO("clasificador/ml_models/modelo_neumonia.pt")

print("Modelo tórax:")
print(modelo_torax.names)

print("Modelo neumonía:")
print(modelo_neumonia.names)