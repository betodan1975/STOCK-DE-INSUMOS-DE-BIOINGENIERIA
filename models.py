"""Modelo de datos: Insumo + Movimiento + Pedido + Config (key/value) + Usuario."""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Insumo(Base):
    __tablename__ = "insumos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    nombre: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    stock_minimo: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    tipo_compra: Mapped[str | None] = mapped_column(String, nullable=True)  # "corta" | "media" | "larga" -> define el lead time usado para calcular stock_minimo
    estado: Mapped[str | None] = mapped_column(String, nullable=True)
    equipo_medico: Mapped[str | None] = mapped_column(String, nullable=True)
    marca: Mapped[str | None] = mapped_column(String, nullable=True)
    referencia: Mapped[str | None] = mapped_column(String, nullable=True)
    ubicacion: Mapped[str | None] = mapped_column(String, nullable=True)
    prom_anual: Mapped[int | None] = mapped_column(Integer, nullable=True)
    solicitud_compra: Mapped[int | None] = mapped_column(Integer, nullable=True)
    moneda: Mapped[str | None] = mapped_column(String, nullable=True)
    precio_original: Mapped[str | None] = mapped_column(String, nullable=True)
    precio_unit_valor: Mapped[float | None] = mapped_column(Float, nullable=True)
    foto_filename: Mapped[str | None] = mapped_column(String, nullable=True)
    foto_phash: Mapped[str | None] = mapped_column(String, nullable=True)  # hash perceptual de la foto, para buscar por imagen
    foto_colorsig: Mapped[str | None] = mapped_column(String, nullable=True)  # firma de color (miniatura 8x8 en hex), complementa el phash

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Movimiento(Base):
    __tablename__ = "movimientos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fecha: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    insumo_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("insumos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    insumo_nombre: Mapped[str | None] = mapped_column(String, nullable=True)
    tipo: Mapped[str] = mapped_column(String, nullable=False)  # "IN" / "OUT" / "AJUSTE"
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    servicio: Mapped[str | None] = mapped_column(String, nullable=True)
    responsable: Mapped[str | None] = mapped_column(String, nullable=True)
    paciente: Mapped[str | None] = mapped_column(String, nullable=True)
    notas: Mapped[str | None] = mapped_column(String, nullable=True)
    comprobante: Mapped[str | None] = mapped_column(String, nullable=True)  # ej: "R-A 0001-00012345" / "F-B ..." / "OC ..."
    comprobante_fecha: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)  # fecha del remito/factura/OC
    proveedor: Mapped[str | None] = mapped_column(String, nullable=True)  # a quien se le compro
    stock_before: Mapped[int | None] = mapped_column(Integer, nullable=True)  # stock del insumo justo antes de este movimiento (permite revertir un AJUSTE al eliminarlo)
    usuario: Mapped[str | None] = mapped_column(String, nullable=True)  # username del operador
    precio_unit_valor: Mapped[float | None] = mapped_column(Float, nullable=True)
    moneda: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Pedido(Base):
    __tablename__ = "pedidos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fecha: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    items_json: Mapped[str] = mapped_column(Text, nullable=False)
    total_usd: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    total_ars: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    notas: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Config(Base):
    """Tabla key/value para guardar config global (fx, threshold, lista de servicios, etc.)."""
    __tablename__ = "config"

    key: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Armario(Base):
    """Armario físico donde se guardan insumos (letra + estantes numerados).

    La ubicación de cada Insumo (campo `ubicacion`, ej. "2K") referencia a un
    Armario por su `letra` + un número de estante. No hay relación de FK
    formal porque `ubicacion` es texto libre en Insumo (para no romper datos
    viejos); el armado se hace en el frontend parseando ese texto.
    """
    __tablename__ = "armarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    letra: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    nombre: Mapped[str | None] = mapped_column(String, nullable=True)
    foto_filename: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Usuario(Base):
    """Usuarios del sistema. Login con username/password (bcrypt). Rol admin/usuario."""
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    nombre: Mapped[str | None] = mapped_column(String, nullable=True)
    rol: Mapped[str] = mapped_column(String, nullable=False, default="usuario")  # 'admin' | 'usuario'
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
