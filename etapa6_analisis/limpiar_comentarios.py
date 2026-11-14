"""
Limpieza de comentarios de YouTube - Etapa 6 (Conocimiento Oculto)
Proyecto: Dinamica Empresarial

Uso:
    python limpiar_comentarios.py comentarios_crudos.csv videos_consultados.csv carpeta_salida

Entradas  (las genera colab_youtube.py):
    comentarios_crudos.csv  -> video_id, comment_id, texto, fecha, likes
    videos_consultados.csv  -> metadatos de los videos

Salidas (en carpeta_salida):
    comentarios_limpios.csv -> corpus final para Orange (sin comment_id, sin autores)
    log_limpieza.csv        -> cuantos comentarios se quitan en cada paso y por que
    videos_resumen.csv      -> tabla de videos con enlaces y conteos antes/despues
    comentarios_descartados.csv -> SOLO para auditoria interna (no publicar)

El script no usa ninguna credencial ni contacta ningun servicio.
"""
import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------- parametros
MIN_PALABRAS = 3

# Relevancia del VIDEO respecto al tema del proyecto (creacion, permanencia,
# crecimiento y cierre de empresas). Es un criterio editorial, documentado:
#   directa    -> el video trata cierre, crisis o rescate de negocios
#   contexto   -> trata el entorno macro (deuda publica, reforma tributaria)
#   tangencial -> trata rentabilidad / emprendimiento en general
RELEVANCIA_VIDEO = {
    "rW-6hpC8izw": "directa",     # cierre de restaurantes en Medellin
    "zm3KYUBUYnE": "directa",     # salir de una crisis economica (negocios)
    "nd0dNQrazxo": "directa",     # rescatar un negocio en quiebra
    "pVfj46LrXGA": "contexto",    # deuda publica de Colombia
    "T_Vc1YfDSwQ": "contexto",    # "quiebra" del Estado y reforma tributaria
    "QvaC0FIaANk": "tangencial",  # negocios que ya no son rentables
    "N-WKlSrkdeQ": "tangencial",  # caso de exito de un empresario
    "H97hH_kvyzU": "tangencial",  # consejo para emprendedores
}

# Lexico del dominio: raices de palabras economico-empresariales.
LEXICO = [
    "empres", "negoci", "pyme", "emprend", "quiebr", "bancarrot", "insolv",
    "cierr", "cerr", "crisis", "deuda", "deud", "endeud", "impuest", "tribut",
    "fiscal", "iva", "venta", "vend", "precio", "arrend", "arriend", "alquil",
    "renta", "costo", "gasto", "inflaci", "econom", "plata", "dinero", "salari",
    "sueldo", "empleo", "desempleo", "trabaj", "cliente", "ingreso", "ganan",
    "ganar", "inversi", "invert", "capital", "comercio", "mercado", "restaurante",
    "producto", "proveedor", "prestam", "credito", "banco", "factura", "nomina",
    "utilidad", "perdid", "perdida", "ahorr", "informal", "turis", "consum",
    "finanza", "presupuesto", "pobre", "riqueza", "rico", "quebrar", "fracas",
    "gast", "billete", "financ", "pagar", "pagan", "pago", "cobr", "recort",
    "interes", "emple", "recurso", "pobreza", "obrero", "tasa",
]

# Palabras funcionales para estimar idioma (heuristica, sin librerias externas)
ES = set("el la los las de del que y en un una es por con para no se su al lo como mas pero sus le ya o este si porque esta son entre cuando muy sin sobre tambien me hasta hay donde quien desde todo nos durante todos uno les ni contra otros ese eso ante ellos e esto mi antes algunos que unos yo otro otras otra el tanto esa estos mucho quienes nada muchos cual poco ella estar estas algunas algo nosotros".split())
EN = set("the and of to in is you that it he was for on are as with his they at be this have from or one had by word but not what all were we when your can said there use an each which she do how their if will up other about out many then them these so some her would make like him into time has look two more write go see number no way could people my than first water been call who oil its now find long down day did get come made may part".split())

URL_RE = re.compile(r"(https?://\S+|www\.\S+|\b\w+\.(?:com|net|org|ly|me)/\S*|\bbit\.ly/\S+)", re.I)
MENCION_RE = re.compile(r"@\w+")
SPAM_RE = re.compile(r"(whatsapp|wa\.me|telegram|t\.me|escr[ií]beme al|contacta(?:me|r)? al|\+?\d{2}[\s-]?\d{3}[\s-]?\d{3}[\s-]?\d{3,4})", re.I)
META_RE = re.compile(
    r"(y el (3|tercer\w*|numero 3|número 3)\b|falt[oó] (el )?(3|tercer\w*|numero 3|número 3|uno)\b|"
    r"(solo|sólo|nada m[aá]s|nom[aá]s)\s+(dij\w+|dice|diste|mencion\w+|escuch\w+|nombr\w+)\s*(el\s*)?(2|dos)\b|"
    r"\bfueron (2|dos)\b|\b2 de 3\b|dices 3|dijo 3|dijiste 3|eran tres o dos|"
    r"cual es el (3|tercero)|cu[aá]l es el (3|tercero)|el (3|tercer\w*) negocio|n[uú]mero 3|el 3ro|el 3er)",
    re.I,
)


def quitar_acentos(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def clave(texto: str) -> str:
    """Forma normalizada para comparar: sin URL/menciones/emoji/puntuacion/acentos."""
    t = URL_RE.sub(" ", texto)
    t = MENCION_RE.sub(" ", t)
    t = quitar_acentos(t.casefold())
    t = re.sub(r"[^a-z0-9ñ\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def palabras(k: str):
    return [w for w in k.split() if re.search(r"[a-zñ]", w)]


def idioma(k: str) -> str:
    toks = palabras(k)
    if len(toks) < 4:
        return "indeterminado"
    es = sum(w in ES for w in toks)
    en = sum(w in EN for w in toks)
    if en >= 2 and en > es:
        return "en"
    return "es"


def enmascarar(texto: str) -> str:
    """Quita datos personales evidentes del texto que se conserva."""
    t = URL_RE.sub("[URL]", texto)
    t = MENCION_RE.sub("[@usuario]", t)
    t = re.sub(r"\+?\d[\d\s-]{7,}\d", "[NUM]", t)
    return re.sub(r"\s+", " ", t).strip()


def main(ruta_com, ruta_vid, salida):
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(ruta_com)
    vid = pd.read_csv(ruta_vid)
    df["clave"] = df["texto"].astype(str).map(clave)
    df["motivo"] = ""
    log = [("0. Comentarios extraidos (crudos)", "Salida de la API, comentarios de primer nivel", 0, len(df))]

    def descartar(mask, motivo, paso, criterio):
        mask = mask & (df["motivo"] == "")
        df.loc[mask, "motivo"] = motivo
        vivos = int((df["motivo"] == "").sum())
        log.append((paso, criterio, int(mask.sum()), vivos))

    # 1. Duplicados por identificador
    descartar(df.duplicated("comment_id", keep="first"), "duplicado_id",
              "1. Duplicados por comment_id", "Mismo comentario descargado dos veces")

    # 2. Vacios / sin contenido textual
    sin_letras = df["clave"].map(lambda k: len(palabras(k)) == 0)
    descartar(sin_letras, "vacio",
              "2. Vacios o sin texto", "Solo emojis, numeros, signos o menciones")

    # 3. Duplicados de texto (copias exactas tras normalizar); se conserva el de mas likes
    orden = df.sort_values(["likes", "fecha"], ascending=[False, True]).index
    vistos = set()
    dup = pd.Series(False, index=df.index)
    for i in orden:
        if df.at[i, "motivo"] != "":
            continue
        k = df.at[i, "clave"]
        if k in vistos:
            dup[i] = True
        else:
            vistos.add(k)
    descartar(dup, "duplicado_texto",
              "3. Duplicados de texto", "Mismo texto normalizado (copias, spam repetido, consignas); se conserva el de mas likes")

    # 4. Idioma
    df["idioma"] = df["clave"].map(idioma)
    descartar(df["idioma"] == "en", "idioma",
              "4. Idioma distinto del espanol", "Heuristica de palabras funcionales (>=2 ingles y mas que espanol)")

    # 5. Irrelevantes (cuatro criterios, en orden)
    spam = df["texto"].astype(str).map(lambda t: bool(URL_RE.search(t) or SPAM_RE.search(t)))
    descartar(spam, "spam", "5a. Irrelevante: publicidad o enlaces", "Contiene URL, WhatsApp/Telegram o telefono")

    corto = df["clave"].map(lambda k: len(palabras(k)) < MIN_PALABRAS)
    descartar(corto, "muy_corto", "5b. Irrelevante: demasiado corto", f"Menos de {MIN_PALABRAS} palabras (saludos, aplausos, 'gracias')")

    meta = df["clave"].map(lambda k: bool(META_RE.search(k)))
    descartar(meta, "meta_video", "5c. Irrelevante: comentarios sobre el formato del video",
              "Quejas del tipo 'y el tercero?' sin contenido sobre el tema")

    def tiene_lexico(k):
        return any(re.search(r"\b" + raiz, k) for raiz in LEXICO)

    sin_tema = ~df["clave"].map(tiene_lexico)
    descartar(sin_tema, "fuera_de_tema", "5d. Irrelevante: sin vocabulario del dominio",
              "No contiene ninguna raiz del lexico economico-empresarial")

    limpio = df[df["motivo"] == ""].copy()
    limpio["texto"] = limpio["texto"].map(enmascarar)
    limpio["fecha"] = limpio["fecha"].astype(str).str[:10]
    limpio["relevancia_video"] = limpio["video_id"].map(RELEVANCIA_VIDEO)
    limpio = limpio.sort_values(["video_id", "fecha"]).reset_index(drop=True)
    limpio.insert(0, "id", [f"c{i + 1:04d}" for i in range(len(limpio))])
    limpio[["id", "video_id", "texto", "fecha", "likes", "idioma", "relevancia_video"]].to_csv(
        salida / "comentarios_limpios.csv", index=False, encoding="utf-8")

    pd.DataFrame(log, columns=["paso", "criterio", "descartados", "quedan"]).to_csv(
        salida / "log_limpieza.csv", index=False, encoding="utf-8")

    df[df["motivo"] != ""][["video_id", "texto", "likes", "motivo"]].to_csv(
        salida / "comentarios_descartados.csv", index=False, encoding="utf-8")

    cuenta = df.groupby("video_id").agg(extraidos=("comment_id", "size"),
                                         descartados=("motivo", lambda s: int((s != "").sum())))
    cuenta["limpios"] = cuenta["extraidos"] - cuenta["descartados"]
    res = vid.merge(cuenta[["limpios"]], left_on="video_id", right_index=True, how="left")
    res["relevancia_video"] = res["video_id"].map(RELEVANCIA_VIDEO)
    res.to_csv(salida / "videos_resumen.csv", index=False, encoding="utf-8")

    print(pd.DataFrame(log, columns=["paso", "criterio", "descartados", "quedan"]).to_string(index=False))
    print()
    print(res[["video_id", "relevancia_video", "comentarios_extraidos", "limpios"]].to_string(index=False))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
