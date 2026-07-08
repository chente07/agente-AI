"""
Sistema de Clasificación Médica en Dos Etapas (YOLOv8)
1. Filtro de Validación: Verifica si la imagen es una radiografía de tórax válida.
2. Diagnóstico Médico con Filtro de Confianza: Identifica Neumonía vs Normal, 
   asegurando un umbral mínimo de certeza diagnóstica.
"""

from ultralytics import YOLO
import os

def analizar_radiografia(ruta_imagen, ruta_modelo_filtro, ruta_modelo_diagnostico, umbral_filtro=0.80, umbral_diagnostico=0.80):
    # Verificación de que la imagen de entrada exista
    if not os.path.exists(ruta_imagen):
        return {"error": f"La ruta de la imagen no existe: {ruta_imagen}"}
        
    # -------------------------------------------------------------------------
    # ETAPA 1: FILTRO DE TAREAS INVÁLIDAS (Modelo de Validación de Tórax)
    # -------------------------------------------------------------------------
    modelo_filtro = YOLO(ruta_modelo_filtro)
    resultado_filtro = modelo_filtro.predict(source=ruta_imagen, verbose=False, device="cpu")[0]
    
    # Extraemos la probabilidad de la clase 'TORAX' (Índice 1 en nuestro modelo)
    prob_torax = resultado_filtro.probs.data[1].item()
    
    print(f"[FILTRO] Confianza de estructura torácica: {prob_torax:.2%}")
    
    # Condicional matemática para evaluar el umbral de validez de la imagen
    if prob_torax < umbral_filtro:
        return {
            "valido": False,
            "conclusive": False,
            "mensaje": "❌ Filtro activado: La imagen no corresponde a una radiografía de tórax válida.",
            "probabilidad_torax": prob_torax
        }
        
    # -------------------------------------------------------------------------
    # ETAPA 2: DIAGNÓSTICO MÉDICO (Modelo de Clasificación de Neumonía)
    # -------------------------------------------------------------------------
    print("[PROCESO] Estructura válida detectada. Procediendo al análisis de patología...")
    
    modelo_diagnostico = YOLO(ruta_modelo_diagnostico)
    resultado_medico = modelo_diagnostico.predict(source=ruta_imagen, verbose=False, device="cpu")[0]
    
    # Extraer etiquetas y predicción con mayor confianza (categoría ganadora)
    clases = resultado_medico.names
    idx_predilecto = resultado_medico.probs.top1
    clase_predicha = clases[idx_predilecto]
    confianza_diagnostico = resultado_medico.probs.top1conf.item()
    
    print(f"[DIAGNÓSTICO] Categoría ganadora: {clase_predicha} ({confianza_diagnostico:.2%})")
    
    # NUEVA CONDICIONAL: Si la confianza de la categoría ganadora es menor al 80%
    if confianza_diagnostico < umbral_diagnostico:
        return {
            "valido": True,
            "conclusive": False,  # 🚩 Bandera solicitada para el Backend
            "mensaje": "⚠️ Predicción rechazada por falta de confianza técnica (< 80%).",
            "resultado": clase_predicha,
            "confianza": confianza_diagnostico,
            "probabilidad_torax": prob_torax
        }
    
    # Diagnóstico exitoso y concluyente
    return {
        "valido": True,
        "conclusive": True,   # Diagnóstico firme
        "resultado": clase_predicha,
        "confianza": confianza_diagnostico,
        "probabilidad_torax": prob_torax
    }

# =============================================================================
# BLOQUE DE EJECUCIÓN (Configuración de rutas ajustadas a tus archivos reales)
# =============================================================================
if __name__ == "__main__":
    # 1. Ajustamos los nombres exactos con los que aparecen en tu barra izquierda
    RUTA_FILTRO = "Modelo1_best.pt"         
    RUTA_DIAGNOSTICO = "Modelo2_best.pt" 
    
    # 2. Ajustamos la extensión de tu imagen que es .jpeg
    IMAGEN_TEST = "prueba2.jpeg"
    
    # Ejecución del análisis
    print("--- INICIANDO PIPELINE DE ANÁLISIS MÉDICO ---")
    diagnostico = analizar_radiografia(IMAGEN_TEST, RUTA_FILTRO, RUTA_DIAGNOSTICO)
    
    print("\n--- INFORME DEL SISTEMA ---")
    if diagnostico.get("error"):
        print(diagnostico["error"])
    elif not diagnostico["valido"]:
        print(diagnostico["mensaje"])
        print(f"Bandera 'conclusive': {diagnostico['conclusive']}")
        print("Operación abortada por seguridad de estructura.")
    elif not diagnostico["conclusive"]:
        print(diagnostico["mensaje"])
        print(f"Resultado tentativo: {diagnostico['resultado']} con {diagnostico['confianza']:.2%}")
        print(f"Bandera 'conclusive': {diagnostico['conclusive']} 🚩 (Imagen rechazada para Backend)")
    else:
        print(f"Estatus de la imagen: VÁLIDA (Confianza: {diagnostico['probabilidad_torax']:.2%})")
        print(f"Diagnóstico Final: {diagnostico['resultado']}")
        print(f"Confianza Médica: {diagnostico['confianza']:.2%}")
        print(f"Bandera 'conclusive': {diagnostico['conclusive']}")