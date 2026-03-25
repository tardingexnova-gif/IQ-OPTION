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

print("⏳ Esperando cierre de vela...")

while True:
    ahora = datetime.now()
    if ahora.second == 0:
        print(f"\n⏰ Vela cerrada detectada: {ahora.strftime('%H:%M:%S')}")
        break
    time.sleep(0.2)

print("\n📥 Descargando velas...\n")

for activo in ACTIVOS:
    try:
        velas = iq.get_candles(activo, 60, 1000, time.time())
        df = pd.DataFrame(velas)

        if df.empty:
            print(f"⚠️ {activo} sin datos")
            continue

        df = df.sort_values("from")
        df = df[['from', 'open', 'max', 'min', 'close']]

        nombre = f"{activo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(nombre, index=False)

        print(f"💾 {activo} guardado ({len(df)} velas)")

    except Exception as e:
        print(f"⚠️ Error en {activo}: {e}")

print("\n✅ PROCESO TERMINADO")
