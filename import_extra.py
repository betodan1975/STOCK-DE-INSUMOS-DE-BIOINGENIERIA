"""Carga los insumos extra que tenias en el HTML original.

Hace UPSERT por nombre directo via SQLAlchemy (no usa la API, asi que
no hace falta login). Es seguro de correr varias veces: si el insumo
ya existe, solo actualiza los campos faltantes (no pisa lo que ya
cargaste a mano). Si no existe, lo crea desde cero.

Uso (parado en api/):
    python import_extra.py
"""
from database import SessionLocal, engine
from models import Base, Insumo

# (nombre, equipo, marca, ubicacion, stock, moneda, precio)
INSUMOS = [
    # ========== SIN STOCK (stock=0) ==========
    ("Bateria 12V 1.3 Ah Camas", None, None, None, 0, "USD", 0),
    ("Bioimedic - Ergometro", None, None, None, 0, "USD", 0),
    ("cable de ergonometria Schiller Sana Bike 1000 ERG 911 PLUS", "ERGONOMETRIA", "SCHILLER", None, 0, "ARS", 762000),
    ("Cable ECG 3 derivaciones Desfibrilador de onda Bifasica Efficia DFM100", "ECG", "PHILIPS", None, 0, "USD", 177.76),
    ("Cable ECG 3 derivaciones Ecografo", "ECG", "PHILIPS", None, 0, "USD", 177.76),
    ("Cable paciente para cicloergometro Schiller Sana Bike 1000 ERG 911 PLUS", "ERGONOMETRIA", "SCHILLER", None, 0, "ARS", 1457445),
    ("Dameca - Sensor de flujo Adultos (usado)", "MESA DE ANESTESIA", None, None, 0, None, None),
    ("ECG Cable Paciente", None, None, None, 0, None, None),
    ("ECG peritas", "ECG", None, None, 0, None, None),
    ("ECG Pinzas", "ECG", None, None, 0, None, None),
    ("Ecosur - Consola ECG", None, None, None, 0, None, None),
    ("Electrodos precordiales", "ECG", "Zusuken kentz Cardico 306", None, 0, None, None),
    ("Haag Streit - Tonometro de Perkins", "OFTALMOLOGIA", None, None, 0, None, None),
    ("HUNTLEIGH - Doppler Vascular", None, None, None, 0, None, None),
    ("Kenz - Cable paciente ECG", None, None, None, 0, None, None),
    ("Lampara de Xenon", None, None, None, 0, None, None),
    ("Lampara Laringoscopios", None, None, None, 0, None, None),
    ("Livetec - Marcapaso externo", "MARCAPASOS", None, None, 0, None, None),
    ("Maquet - Cassettes servo Air", "RESPIRADOR", None, None, 0, None, None),
    ("Maquet - Cassettes servo i", "RESPIRADOR", None, None, 0, None, None),
    ("Maquet - Cassettes servo u", "RESPIRADOR", None, None, 0, None, None),
    ("Maquet - Filtros Servo Duo Guard", "RESPIRADOR", None, None, 0, None, None),
    ("Maquet - Membrana cassete espiratorio", "RESPIRADOR", None, None, 0, None, None),
    ("Maquet - Servo i Celda de O2", "RESPIRADOR", None, None, 0, None, None),
    ("Masimo - Sensor de CO2 (reutilizable)", None, None, None, 0, None, None),
    ("Memoria SD - 32GB", "MEMORIA", None, None, 0, None, None),
    ("Memoria SD - 4GB", "MEMORIA", None, None, 0, None, None),
    ("Memoria SD - 8 GB", "MEMORIA", None, None, 0, None, None),
    ("MIR - Turbina descartable (Espirometria)", "ESPIROMETRO", None, None, 0, None, None),
    ("NEITZ - Cargador Retinoscopio", None, None, None, 0, None, None),
    ("NEITZ - Lampara Oftalmoscopio", None, None, None, 0, None, None),
    ("NEITZ - Lampara Retinoscopio", None, None, None, 0, None, None),
    ("NEITZ - Oftalmoscopio", None, None, None, 0, None, None),
    ("NEITZ - Retinoscopio", None, None, None, 0, None, None),
    ("Nellcor - Oximetro portatil", "OXIMETRO", None, None, 0, None, None),
    ("Nellcor - Sensor de SPO2", "OXIMETRO", None, None, 0, None, None),
    ("OCULAR - Lente de 20 D", None, None, None, 0, None, None),
    ("OCULAR - Lente de 3 espejos", None, None, None, 0, None, None),
    ("Philips - Adaptador Dual PI", None, "PHILIPS", None, 0, None, None),
    ("Philips - Bateria Desfibrilador", None, "PHILIPS", None, 0, None, None),
    ("Philips - Cable ECG 3 derivaciones", None, "PHILIPS", None, 0, None, None),
    ("Philips - Cable ECG 5 derivaciones", None, "PHILIPS", None, 0, None, None),
    ("Philips - Cable ECG 5 derivaciones (3+2)ECG", None, "PHILIPS", None, 0, None, None),
    ("Philips - Cable ECG 5 derivaciones (poligrafo)", None, "PHILIPS", None, 0, None, None),
    ("Philips - Cable ECG 5 derivaciones Recup.", None, "PHILIPS", None, 0, None, None),
    ("Philips - Cable ECG troncal", None, "PHILIPS", None, 0, None, None),
    ("Philips - Cable ECG troncal (5+5) (poligrafo)", None, "PHILIPS", None, 0, None, None),
    ("Philips - Cable ECG troncal 3 derivaciones", None, "PHILIPS", None, 0, None, None),
    ("Philips - Cable ECG troncal recuperado", None, "PHILIPS", None, 0, None, None),
    ("Philips - Cable paciente Telemetro", None, "PHILIPS", None, 0, None, None),
    ("Philips - Intermediario (DB9) SpO2", None, "PHILIPS", None, 0, None, None),
    ("Philips - Intermediario (Gasto cardiaco I)", None, "PHILIPS", None, 0, None, None),
    ("Philips - Intermediario (Gasto cardiaco MI)", None, "PHILIPS", None, 0, None, None),
    ("Philips - Intermediario BIS", None, "PHILIPS", None, 0, None, None),
    ("Philips - Intermediario PI", None, "PHILIPS", None, 0, None, None),
    ("Philips - Intermediario PI Edwars", "Monitor Multiparametrico MX800 / MX450 (Philips)", "PHILIPS", None, 0, None, None),
    ("Philips - Intermediaro P (Gasto cardiaco MI)", None, "PHILIPS", None, 0, None, None),
    ("Philips - Latiguillos EEG", None, "PHILIPS", None, 0, None, None),
    ("Philips - Lineas Microstream EtCO2", None, "PHILIPS", None, 0, None, None),
    ("Philips - Manguito PNI pediatrico", "Monitor Multiparametrico MX800 / MX450 (Philips)", "PHILIPS", None, 0, None, None),
    ("Philips - Medidor de pico Flujo", None, "PHILIPS", None, 0, None, None),
    ("Philips - PICCO Sensor T (Gasto cardiaco MI)", None, "PHILIPS", None, 0, None, None),
    ("Philips - Prolongador SpO2", None, "PHILIPS", None, 0, None, None),
    ("Philips - Sensor de temperatura - 21078A", "Monitor Multiparametrico MX800 / MX450 (Philips)", "PHILIPS", None, 0, None, None),
    ("Philips - Sensor SpO2 Telemetro", None, "PHILIPS", None, 0, None, None),
    ("Philips - Sensor T (Gasto cardiaco I)", None, "PHILIPS", None, 0, None, None),
    ("Philips - Sensor T bano (Gasto cardiaco I)", None, "PHILIPS", None, 0, None, None),
    ("Philips - Telemetro", None, "PHILIPS", None, 0, None, None),
    ("Philips - Transductor C6-2 (convexo)", None, "PHILIPS", None, 0, None, None),
    ("Philips - Troncal EEG", None, "PHILIPS", None, 0, None, None),
    ("Pila CR 1220 (3 volt)", "PILA", None, None, 0, None, None),
    ("Pila CR 2025 (3 volt)", "PILA", None, None, 0, None, None),
    ("Pila CR2032", "PILA", None, None, 0, None, None),
    ("Pila de Litio CR2 (3 volt) - (Navegador)", "PILA", None, None, 0, None, None),
    ("Pilas AAA", "PILA", None, None, 0, None, None),
    ("Pilas CR123", "MARCAPASOS", None, None, 0, None, None),
    ("Piston elevador de camilla Striker", "CAMILLA", None, None, 0, None, None),
    ("Sensor SPO2 Mindray PM-60", "OXIMETRO", "mindray", None, 0, None, None),
    ("Silfab - Filtro aspirador", None, None, None, 0, None, None),
    ("SounTech - MAPA Oscar 2", "MAPA", None, None, 0, None, None),
    ("SounTech M - MAPA Oscar 2 Manguito 32-44cm", "MAPA", None, None, 0, None, None),
    ("Tarjeta Stockey RFID GRIFOLS", None, None, None, 0, None, None),
    ("Triac para autoclave Sturd", None, None, None, 0, None, None),
    ("Tubuladura para bomba de irrigacion de endoscopio", None, None, None, 0, None, None),
    ("Welch Allyn - Iluminador Laringeo", None, None, None, 0, None, None),
    ("YKDMED - Sensor de SP02 MINDRAY - NELLCOR", "OXIMETRO", None, None, 0, None, None),
    # ========== Con stock > 0 ==========
    ("Agente Secante", None, "STAT DRI PLUS", None, 11, None, None),
    ("Brake", "CAMA INTOUCH", "Stryker", None, 8, None, None),
    ("Cable Adaptador de Salida Cardiaca M1643A", None, "PHILIPS", "2K", 15, None, None),
    ("Cable Adaptador IBP 650-206", None, "PHILIPS", "2K", 20, None, None),
    ("Cable de Salida Cardiaca M1642A", None, "PHILIPS", "3K", 4, None, None),
    ("Canister", "MESA DE ANESTESIA", "Dameca", None, 5, None, None),
    ("Latiguillos EEG 120CM", "Estudio del Sueno / EEG", "Insumos Hospitalarios | Cardiosistemas SRL", "3K", 6, "ARS", 9500),
    ("Manguito PNI Adultos", "Monitor Multiparametrico MX800 / MX450 (Philips)", None, "1K", 17, None, None),
    ("Manguito SPACELABS 31-40 CM", "MANGUITO", None, "1K", 1, None, None),
    ("Philips - Sensor SpO2 - M1196A", "Monitor Multiparametrico MX800 / MX450 (Philips)", "PHILIPS", None, 3, None, None),
    ("PICCO Temperature Probe M1646A", None, "PHILIPS", "2K", 19, None, None),
    ("Relay de estado solido para autoclave Sturd", None, None, None, 3, None, None),
    ("Sonda de temperatura Cardiaca", None, "PHILIPS", "3K", 2, None, None),
    ("Sonda de Temperatura para Bano 23002A", None, "PHILIPS", "3K", 2, None, None),
    ("Stryker - Mosfet Repuesto de Fuente Alimentacion", None, None, "AREA 51", 15, None, None),
    ("Welch Allyn - Pocket Led (Oto/Oftalmo)", "OTOSCOPIO / OFTALMOSCOPIO", None, None, 13, None, None),
]


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    creados = actualizados = sin_cambios = 0
    try:
        existentes = {i.nombre.strip().lower(): i for i in db.query(Insumo).all()}
        for nombre, equipo, marca, ubic, stock, moneda, precio in INSUMOS:
            key = nombre.strip().lower()
            existing = existentes.get(key)
            if existing:
                # No pisamos campos no-vacios. Solo completamos si esta vacio.
                changed = False
                if not existing.equipo_medico and equipo:
                    existing.equipo_medico = equipo; changed = True
                if not existing.marca and marca:
                    existing.marca = marca; changed = True
                if not existing.ubicacion and ubic:
                    existing.ubicacion = ubic; changed = True
                if not existing.moneda and moneda:
                    existing.moneda = moneda; changed = True
                if not existing.precio_unit_valor and precio:
                    existing.precio_unit_valor = precio; changed = True
                if changed:
                    actualizados += 1
                else:
                    sin_cambios += 1
            else:
                db.add(Insumo(
                    nombre=nombre,
                    stock=stock or 0,
                    estado="OK" if (stock or 0) > 0 else "SIN STOCK",
                    equipo_medico=equipo,
                    marca=marca,
                    ubicacion=ubic,
                    moneda=moneda,
                    precio_unit_valor=precio,
                ))
                creados += 1
        db.commit()
    finally:
        db.close()
    print(f"Listo -> nuevos: {creados}, completados: {actualizados}, ya estaban: {sin_cambios}")
    print(f"Total enviado: {len(INSUMOS)} insumos")


if __name__ == "__main__":
    main()
