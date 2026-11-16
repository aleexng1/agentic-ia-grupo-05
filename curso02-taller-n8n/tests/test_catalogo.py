"""Pruebas del acceso al catálogo y de sus herramientas. Sin base de datos ni modelo: la conexión es falsa."""

from decimal import Decimal

import psycopg
import pytest

from src.router import catalogo, tools
from src.router.catalogo import CatalogoNoDisponible, SqlNoPermitido, consultar, validar_select

URL_FALSA = "postgresql://usuario:claveSecreta99@servidor-privado.example.com:5432/base"
SELECT_OK = "SELECT sku_id, nombre FROM catalogo.productos_unicos WHERE sku_id = %s LIMIT %s"


# ── Una conexión falsa, para ver cómo se usa ─────────────────────────────────

class CursorFalso:
    def __init__(self, conn):
        self.conn = conn

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, params=None):
        self.conn.ejecutado.append({"read_only": self.conn.read_only, "sql": sql, "params": params})

    def fetchmany(self, n):
        return [{"sku_id": "abc", "nombre": "Producto"}]


class ConexionFalsa:
    def __init__(self):
        self.read_only = None
        self.ejecutado = []
        self.cerrada = False

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.cerrada = True
        return False

    def cursor(self):
        return CursorFalso(self)


@pytest.fixture
def conexion(monkeypatch):
    """DATABASE_URL falsa y psycopg.connect reemplazado por una conexión falsa."""
    monkeypatch.setenv("DATABASE_URL", URL_FALSA)
    conn = ConexionFalsa()
    llamadas = []

    def conectar(url, **kwargs):
        llamadas.append(kwargs)
        return conn

    monkeypatch.setattr(catalogo.psycopg, "connect", conectar)
    conn.llamadas = llamadas
    return conn


@pytest.fixture
def sin_red(monkeypatch):
    """Si algo intenta conectarse, la prueba falla."""
    monkeypatch.setenv("DATABASE_URL", URL_FALSA)

    def prohibido(*a, **k):
        raise AssertionError("no debía conectarse a la base")

    monkeypatch.setattr(catalogo.psycopg, "connect", prohibido)


# ── Solo SELECT ──────────────────────────────────────────────────────────────

def test_acepta_un_select_simple():
    assert validar_select(SELECT_OK) == SELECT_OK
    assert validar_select(SELECT_OK + " ;  ") == SELECT_OK  # el ; final se quita


@pytest.mark.parametrize(
    "sql",
    [
        "INSERT INTO catalogo.productos_unicos (sku_id) VALUES (%s)",
        "UPDATE catalogo.productos_unicos SET precio_internet = 0",
        "DELETE FROM catalogo.productos_unicos",
        "DROP TABLE catalogo.productos_unicos",
        "TRUNCATE catalogo.productos_unicos",
        "ALTER TABLE catalogo.productos_unicos ADD COLUMN x int",
        "CREATE TABLE catalogo.otra (x int)",
        "GRANT ALL ON catalogo.productos_unicos TO public",
        "COPY catalogo.productos_unicos TO STDOUT",
        "CALL algo()",
        "SET search_path = public",
        "BEGIN",
        "  insert into catalogo.productos_unicos values (1)",  # minúsculas y espacios
    ],
)
def test_rechaza_lo_que_no_es_select(sql):
    with pytest.raises(SqlNoPermitido):
        validar_select(sql)


@pytest.mark.parametrize(
    "sql",
    [
        "",
        "   ",
        None,
        123,
        "SELECT 1",  # no lee el catálogo
        "SELECT * FROM catalogo.productos_unicos; DROP TABLE catalogo.productos_unicos",  # dos sentencias
        "SELECT * FROM catalogo.productos_unicos; SELECT 1",
        "SELECT * FROM catalogo.productos_unicos -- ; DELETE",  # comentario
        "SELECT * FROM catalogo.productos_unicos /* x */",
        "WITH x AS (DELETE FROM catalogo.productos_unicos RETURNING *) SELECT * FROM x",  # CTE que escribe
        "SELECT * INTO catalogo.copia FROM catalogo.productos_unicos",  # SELECT INTO crea una tabla
        "SELECT * FROM catalogo.productos_unicos FOR UPDATE",  # bloquea filas
        "SELECT * FROM catalogo.productos_unicos FOR SHARE",
        "SELECT * FROM catalogo.productos_unicos WHERE nombre = 'tele'",  # literal de texto: va en parámetros
        "SELECT * FROM catalogo.productos_unicos WHERE nombre = $$tele$$",
        'SELECT "sku_id" FROM catalogo.productos_unicos',
        "SELECT * FROM productos_unicos",  # sin el nombre completo
        "SELECT * FROM public.checkpoints",  # otra tabla
        "SELECT * FROM catalogo.productos_unicos JOIN alex_nail.checkpoints ON TRUE",
        "SELECT pg_terminate_backend(1) FROM catalogo.productos_unicos",  # función no permitida
        "SELECT pg_read_file(%s) FROM catalogo.productos_unicos",
        "SELECT dblink_exec(%s, %s) FROM catalogo.productos_unicos",
    ],
)
def test_rechaza_sql_peligroso_o_ajeno(sql):
    with pytest.raises(SqlNoPermitido):
        validar_select(sql)


def test_consultar_rechaza_antes_de_conectar(sin_red):
    for sql in ("DELETE FROM catalogo.productos_unicos", "SELECT 1; DROP TABLE x", "UPDATE x SET y = 1"):
        with pytest.raises(SqlNoPermitido):
            consultar(sql)


# ── La consulta: solo lectura, con parámetros, conexión corta ────────────────

def test_consultar_va_en_solo_lectura_con_parametros_y_cierra(conexion):
    filas = consultar(SELECT_OK, ["abc", 1])

    assert filas == [{"sku_id": "abc", "nombre": "Producto"}]
    (ejecucion,) = conexion.ejecutado
    assert ejecucion["read_only"] is True  # BEGIN READ ONLY antes de ejecutar
    assert ejecucion["sql"] == SELECT_OK
    assert ejecucion["params"] == ["abc", 1]  # los valores van aparte del SQL
    assert conexion.cerrada is True  # no queda abierta entre consultas
    opciones = conexion.llamadas[0]["options"]
    assert "default_transaction_read_only=on" in opciones and "statement_timeout" in opciones
    assert "search_path" not in opciones  # el catálogo se pide con nombre completo


def test_consultar_sin_database_url_no_disponible(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(CatalogoNoDisponible):
        consultar(SELECT_OK, ["a", 1])


def test_consultar_si_la_base_falla_no_expone_secretos(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", URL_FALSA)

    def falla(*a, **k):
        raise psycopg.OperationalError(
            'connection failed: connection to server at "servidor-privado.example.com", port 5432 failed: '
            "FATAL: remaining connection slots are reserved for roles with the SUPERUSER attribute"
        )

    monkeypatch.setattr(catalogo.psycopg, "connect", falla)
    with pytest.raises(CatalogoNoDisponible) as e:
        consultar(SELECT_OK, ["a", 1])
    assert "remaining connection slots" in str(e.value)  # el motivo sí se ve
    for secreto in ("servidor-privado", "claveSecreta99", "postgresql://"):
        assert secreto not in str(e.value)
    assert e.value.__cause__ is None and e.value.__suppress_context__  # sin el error original encadenado
    assert not catalogo._TURNO.locked()  # el turno se libera aunque falle


def test_solo_una_conexion_a_la_vez(conexion, monkeypatch):
    """Si el turno está ocupado, la segunda consulta espera y, pasado el tope, queda 'no disponible'."""
    monkeypatch.setattr(catalogo, "SEGUNDOS_ESPERA", 0.05)
    assert catalogo._TURNO.acquire(timeout=1)
    try:
        with pytest.raises(CatalogoNoDisponible):
            consultar(SELECT_OK, ["a", 1])
        assert conexion.ejecutado == []  # ni siquiera se conectó
    finally:
        catalogo._TURNO.release()
    assert consultar(SELECT_OK, ["a", 1])  # liberado el turno, vuelve a funcionar


# ── Las herramientas: su SQL es válido y el texto del usuario solo va en parámetros ──

@pytest.fixture
def capturado(monkeypatch):
    llamadas = []

    def falso(sql, params=()):
        llamadas.append((sql, list(params)))
        return [{"sku_id": "s1", "nombre": "TV 55", "marca": None, "precio_internet": 299990,
                 "descuento_pct": None, "rating": Decimal("4.5")}]

    monkeypatch.setattr(tools.catalogo, "consultar", falso)
    return llamadas


def test_buscar_productos_arma_sql_valido_y_con_parametros(capturado):
    resultado = tools.buscar_productos.invoke({
        "consulta": "smart tv 55", "categoria": "Televisores", "marca": "Samsung", "precio_max": 400000})

    (sql, params), = capturado
    validar_select(sql)  # el SQL que arma la herramienta pasa la validación
    assert params == ["smart", "tv", "55", "Samsung", "Samsung", "Televisores", 400000, 5]
    assert sql.count("strpos(lower(nombre), lower(%s))") == 3 + 1  # una por palabra + la marca dentro del nombre
    assert "strpos(lower(marca), lower(%s))" in sql  # la marca también en su columna
    assert "ORDER BY rating DESC NULLS LAST" in sql and "LIMIT %s" in sql
    assert "catalogo.productos_unicos" in sql
    assert resultado == [{"sku_id": "s1", "nombre": "TV 55", "marca": None, "precio_internet": 299990,
                          "descuento_pct": None, "rating": 4.5}]  # Decimal -> float; lo vacío queda en None
    assert isinstance(resultado[0]["rating"], float)


@pytest.mark.parametrize("texto", ["x'; DROP TABLE catalogo.productos_unicos; --", "a\" OR 1=1 --", "$$x$$", "50%_"])
def test_el_texto_del_usuario_nunca_entra_al_sql(capturado, texto):
    tools.buscar_productos.invoke({"consulta": texto, "marca": texto})
    tools.ver_producto.invoke({"sku_id": texto})
    for sql, params in capturado:
        validar_select(sql)
        assert texto.split()[0] not in sql
        assert not set("'\"$") & set(sql)
    assert any(texto.split()[0] in p for p in capturado[0][1] if isinstance(p, str))  # viaja como parámetro


def test_buscar_productos_sin_criterios_no_consulta(capturado):
    assert "Indica qué producto" in tools.buscar_productos.invoke({"consulta": "   "})
    assert capturado == []


def test_ver_producto_devuelve_el_detalle_con_link(monkeypatch):
    fila = {"sku_id": "s1", "nombre": "TV", "link": "https://tienda.example/p/s1", "rating": Decimal("4.0")}
    monkeypatch.setattr(tools.catalogo, "consultar", lambda sql, params=(): [fila])
    detalle = tools.ver_producto.invoke({"sku_id": "s1"})
    assert detalle["link"] == "https://tienda.example/p/s1" and detalle["rating"] == 4.0


def test_ver_producto_inexistente(monkeypatch):
    monkeypatch.setattr(tools.catalogo, "consultar", lambda sql, params=(): [])
    assert "No encontré" in tools.ver_producto.invoke({"sku_id": "zzz"})


def test_mejores_ofertas_ordena_por_descuento_y_limita(capturado):
    tools.mejores_ofertas.invoke({"categoria": "Smartphones", "limite": 99})
    tools.mejores_ofertas.invoke({})
    (sql1, p1), (sql2, p2) = capturado
    for sql in (sql1, sql2):
        validar_select(sql)
        assert "ORDER BY descuento_pct DESC" in sql and "descuento_pct IS NOT NULL" in sql
    assert p1 == ["Smartphones", 10]  # el límite se recorta a 10
    assert p2 == [5]  # por defecto 5, sin categoría


def test_si_el_catalogo_no_responde_la_herramienta_lo_dice(monkeypatch):
    def cae(sql, params=()):
        raise CatalogoNoDisponible("sin cupo de conexiones")

    monkeypatch.setattr(tools.catalogo, "consultar", cae)
    for resultado in (
        tools.buscar_productos.invoke({"consulta": "tv"}),
        tools.ver_producto.invoke({"sku_id": "s1"}),
        tools.mejores_ofertas.invoke({}),
    ):
        assert resultado == "catálogo no disponible"


def test_las_tres_herramientas_estan_registradas():
    assert [t.name for t in tools.TOOLS_PREVENTA] == ["buscar_productos", "ver_producto", "mejores_ofertas"]
    assert set(tools.buscar_productos.args) == {"consulta", "categoria", "marca", "precio_max"}


# ── scripts/ver_catalogo.py (con consultas falsas) ───────────────────────────

def test_ver_catalogo_cuenta_por_categoria_y_busca(monkeypatch, capsys):
    from scripts import ver_catalogo

    consultas = []

    def falso(sql, params=()):
        consultas.append((sql, list(params)))
        if "GROUP BY" in sql:
            return [{"categoria": "Smartphones", "productos": 1500}, {"categoria": "Televisores", "productos": 1147}]
        return [{"sku_id": "s1", "nombre": "Samsung Galaxy S25", "marca": "Samsung", "categoria": "Smartphones",
                 "precio_internet": 1299990, "descuento_pct": None, "rating": Decimal("4.8")}]

    monkeypatch.setattr(ver_catalogo.catalogo, "consultar", falso)

    ver_catalogo.contar_por_categoria()
    salida = capsys.readouterr().out
    assert "2647" in salida and "Smartphones" in salida and "Televisores" in salida

    ver_catalogo.buscar("samsung'; DROP TABLE x")
    salida = capsys.readouterr().out
    assert "$1.299.990" in salida and "4.8" in salida and "Samsung Galaxy S25" in salida

    for sql, params in consultas:
        validar_select(sql)  # ambas consultas son SELECT válidos
    assert consultas[1][1] == ["samsung'; DROP TABLE x", 10]  # el texto viaja como parámetro; hasta 10


def test_ver_catalogo_sin_base_avisa(monkeypatch):
    from scripts import ver_catalogo

    def cae(sql, params=()):
        raise CatalogoNoDisponible("sin red")

    monkeypatch.setattr(ver_catalogo.catalogo, "consultar", cae)
    monkeypatch.setattr("sys.argv", ["ver_catalogo.py"])
    with pytest.raises(SystemExit) as e:
        ver_catalogo.main()
    assert "catálogo no disponible" in str(e.value)
