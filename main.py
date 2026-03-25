from dotenv import load_dotenv
load_dotenv()

from iqoptionapi.stable_api import IQ_Option
import pandas as pd
import time
from datetime import datetime
import os

EMAIL = os.getenv("IQ_EMAIL")
PASSWORD = os.getenv("IQ_PASSWORD")

ACTIVOS = [
    "AUDCAD-OTC",
    "EURGBP-OTC",
    "EURJPY-OTC",
    "EURUSD-OTC",
    "GBPJPY-OTC",
    "GBPUSD-OTC",
    "NZDUSD-OTC",
    "USDCHF-OTC",
    "USDJPY-OTC"
]

print("🔄 Conectando...")
iq = IQ_Option(EMAIL, PASSWORD)
iq.connect()

if not iq.check_connect():
    print("❌ Error conexión")
    exit()
else:
    print("✅ Conectado")

# ---------------- FUNCION PARA GUARDAR ---------------- #
def guardar_velas(activo, cantidad):
    try:
        velas = iq.get_candles(activo, 60, cantidad, time.time())
        df = pd.DataFrame(velas)

        if df.empty:
            print(f"⚠️ {activo} sin datos")
            return

        df = df.sort_values("from")
        df = df[['from', 'open', 'max', 'min', 'close']]

        nombre_archivo = f"{activo}.csv"

        if os.path.exists(nombre_archivo):
            df.to_csv(nombre_archivo, mode='a', header=False, index=False)
        else:
            df.to_csv(nombre_archivo, index=False)

        print(f"💾 {activo} +{len(df)} velas")

    except Exception as e:
        print(f"⚠️ Error en {activo}: {e}")

# ---------------- DESCARGA INICIAL ---------------- #
print("\n📥 Descargando 100 velas iniciales...\n")

for activo in ACTIVOS:
    guardar_velas(activo, 100)

print("\n🔁 Iniciando ciclo escalonado preciso...\n")

# Tiempo base del sistema
inicio_ciclo = time.time()

while True:
    # ================= BLOQUE 5 MIN ================= #
    objetivo_5min = inicio_ciclo + 300  # 5 minutos

    tiempo_restante = objetivo_5min - time.time()
    if tiempo_restante > 0:
        print(f"⏳ Esperando {round(tiempo_restante, 2)} segundos para bloque de 5 min...")
        time.sleep(tiempo_restante)

    print("\n📥 Descargando 5 velas...\n")
    for activo in ACTIVOS:
        guardar_velas(activo, 5)

    # ================= BLOQUE 15 MIN ================= #
    objetivo_15min = objetivo_5min + 900  # 15 minutos adicionales

    tiempo_restante = objetivo_15min - time.time()
    if tiempo_restante > 0:
        print(f"⏳ Esperando {round(tiempo_restante, 2)} segundos para bloque de 15 min...")
        time.sleep(tiempo_restante)

    print("\n📥 Descargando 10 velas...\n")
    for activo in ACTIVOS:
        guardar_velas(activo, 10)

    # Reiniciar ciclo tomando como referencia el tiempo exacto esperado
    inicio_ciclo = objetivo_15min
