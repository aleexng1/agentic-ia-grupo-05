"""Prueba la conexión a la base Postgres compartida del curso.

    python scripts/probar_db.py

Lee DATABASE_URL desde .env y abre UNA sola conexión corta (se cierra al terminar; el usuario
admite pocas conexiones a la vez). Nunca imprime la URL, la clave ni el servidor completo.
Solo consulta: no modifica ningún dato.
"""

import sys
from pathlib import Path

import psycopg
from dotenv import dotenv_values
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict

RAIZ = Path(__file__).resolve().parent.parent
TABLA = ("catalogo", "productos_unicos")
FILAS_ESPERADAS = 2647


def leer_url() -> str:
    url = (dotenv_values(RAIZ / ".env").get("DATABASE_URL") or "").strip()
    if not url:
        sys.exit("✘ Falta DATABASE_URL en .env.")
    return url


def sin_secretos(texto: str, url: str) -> str:
    """Quita de un mensaje de error la URL, la clave y el servidor."""
    info = conninfo_to_dict(url)
    for secreto in (url, info.get("password"), info.get("host")):
        if secreto:
            texto = texto.replace(secreto, "<oculto>")
    return texto


def titulo(texto: str) -> None:
    print(f"\n── {texto} " + "─" * max(0, 70 - len(texto)))


def servidor_parcial(host: str | None) -> str:
    """Muestra solo el dominio base (sin el nombre completo del servidor)."""
    if not host:
        return "(socket local)"
    partes = host.split(".")
    return "…" + ".".join(partes[-2:]) if len(partes) > 2 else "(oculto)"


def main() -> None:
    url = leer_url()
    try:
        # connect_timeout corto: si el servidor no responde, no se queda colgado.
        conn = psycopg.connect(url, connect_timeout=15)
    except psycopg.Error as e:
        sys.exit(f"✘ No pude conectar: {type(e).__name__}: {sin_secretos(str(e).strip(), url)}")

    with conn:  # cierra la conexión al salir, aunque algo falle
        conn.read_only = True  # esta sesión no puede modificar datos
        cur = conn.cursor()

        # 1 · Usuario y base
        titulo("Conexión")
        cur.execute("SELECT current_user, current_database()")
        usuario, base = cur.fetchone()
        host = conninfo_to_dict(url).get("host")
        print(f"usuario : {usuario}")
        print(f"base    : {base}")
        print(f"servidor: {servidor_parcial(host)}")

        # 2 · Esquema de trabajo y permiso para crear tablas
        titulo("Dónde creo mis tablas")
        cur.execute("SELECT current_schema()")
        esquema = cur.fetchone()[0]
        print(f"current_schema(): {esquema}")
        if esquema is None:
            print("  ✘ no hay esquema de trabajo en el search_path (no podría crear tablas sin indicar uno)")
        else:
            cur.execute("SELECT has_schema_privilege(current_user, %s, 'CREATE')", (esquema,))
            puede = cur.fetchone()[0]
            print(f"  permiso CREATE en '{esquema}': {'✔ sí' if puede else '✘ no'}")
        cur.execute(
            "SELECT nspname FROM pg_namespace "
            "WHERE nspname !~ '^pg_' AND nspname <> 'information_schema' "
            "AND has_schema_privilege(current_user, nspname, 'CREATE') ORDER BY 1"
        )
        print("  esquemas donde puedo crear:", ", ".join(r[0] for r in cur.fetchall()) or "ninguno")

        # 3 · Filas de la tabla
        esquema_t, tabla = TABLA
        nombre = f"{esquema_t}.{tabla}"
        titulo(f"Tabla {nombre}")
        try:
            cur.execute(sql.SQL("SELECT count(*) FROM {}.{}").format(
                sql.Identifier(esquema_t), sql.Identifier(tabla)))
        except psycopg.Error as e:
            sys.exit(f"✘ No pude leer {nombre}: {sin_secretos(str(e).strip(), url)}")
        total = cur.fetchone()[0]
        marca = "✔" if total == FILAS_ESPERADAS else "✘"
        print(f"filas: {total} (esperadas {FILAS_ESPERADAS}) {marca}")

        # 4 · Columnas y tipos
        cur.execute(
            "SELECT column_name, data_type FROM information_schema.columns "
            "WHERE table_schema = %s AND table_name = %s ORDER BY ordinal_position",
            (esquema_t, tabla),
        )
        columnas = cur.fetchall()
        print("\ncolumnas:")
        ancho = max((len(c) for c, _ in columnas), default=0)
        for nombre_col, tipo in columnas:
            print(f"  {nombre_col:<{ancho}}  {tipo}")

        # 3b · 3 productos de ejemplo
        print("\n3 productos de ejemplo:")
        cur.execute(sql.SQL("SELECT * FROM {}.{} LIMIT 3").format(
            sql.Identifier(esquema_t), sql.Identifier(tabla)))
        nombres = [d.name for d in cur.description]
        for i, fila in enumerate(cur.fetchall(), 1):
            print(f"  #{i}")
            for n, valor in zip(nombres, fila):
                texto = str(valor)
                print(f"    {n}: {texto if len(texto) <= 90 else texto[:89] + '…'}")

        # 5 · Privilegios sobre catalogo (solo consulta, sin modificar nada)
        titulo("Privilegios sobre catalogo")
        cur.execute(
            "SELECT has_schema_privilege(current_user, %s, 'USAGE'), "
            "       has_schema_privilege(current_user, %s, 'CREATE')",
            (esquema_t, esquema_t),
        )
        uso, crear = cur.fetchone()
        print(f"esquema {esquema_t}: USAGE={uso}  CREATE={crear}")
        cur.execute(
            "SELECT has_table_privilege(current_user, %s, p) "
            "FROM unnest(ARRAY['SELECT','INSERT','UPDATE','DELETE','TRUNCATE']) AS p",
            (nombre,),
        )
        privilegios = dict(zip(["SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE"], (r[0] for r in cur.fetchall())))
        for p, v in privilegios.items():
            print(f"  {p:<9}: {'sí' if v else 'no'}")
        escritura = [p for p in ("INSERT", "UPDATE", "DELETE", "TRUNCATE") if privilegios[p]]
        if crear or escritura:
            print(f"✘ Ojo: SÍ tengo permisos de escritura sobre catalogo ({', '.join(escritura) or 'CREATE en el esquema'}).")
        else:
            print("✔ Confirmado: NO puedo escribir en catalogo (solo lectura).")

    print("\nConexión cerrada.")


if __name__ == "__main__":
    main()
