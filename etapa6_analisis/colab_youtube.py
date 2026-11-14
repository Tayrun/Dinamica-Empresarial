# ============================================================================
# Etapa 6 - Extracción de comentarios de YouTube (para pegar en UNA celda de Google Colab)
#
# Propósito: conocer qué razones mencionan los usuarios sobre por qué las empresas
# colombianas se endeudan, entran en crisis, cierran o sobreviven, y contrastarlo con
# los datos del modelo (SIREM).
#
# La clave NO va escrita aquí: se lee de los Secretos de Colab (icono de llave).
# No se guardan nombres ni identificadores de los autores de los comentarios.
# ============================================================================
import requests
import pandas as pd
from datetime import datetime, timezone
from google.colab import files, userdata

# ---------------------------------------------------------------- configuración
API_KEY = userdata.get("YOUTUBE_API_KEY")   # secreto de Colab; no escribir la clave en el código

CONSULTAS = [
    "por qué cierran las empresas en Colombia",
    "endeudamiento de las pymes en Colombia",
    "quiebra de empresas en Colombia",
    "cómo sobrevive una pyme en Colombia crisis",
    "insolvencia empresarial Colombia",
]
VIDEOS_POR_CONSULTA = 10         # resultados revisados por cada consulta
MIN_COMENTARIOS_VIDEO = 50       # se descartan videos con menos comentarios
VIDEOS_A_ANALIZAR = 8            # videos finalmente usados (los de más comentarios)
MAX_COMENTARIOS_POR_VIDEO = 300  # comentarios principales por video
# -----------------------------------------------------------------------------

BASE = "https://www.googleapis.com/youtube/v3/"


def llamar(recurso, **parametros):
    parametros["key"] = API_KEY
    r = requests.get(BASE + recurso, params=parametros, timeout=30)
    datos = r.json()
    if r.status_code != 200:
        error = datos.get("error", {})
        razon = (error.get("errors") or [{}])[0].get("reason", "")
        raise RuntimeError("%s (%s)" % (razon or r.status_code, error.get("message", "")))
    return datos


# 1) Buscar videos candidatos con cada consulta
candidatos = {}
for q in CONSULTAS:
    r = llamar("search", part="snippet", q=q, type="video", maxResults=VIDEOS_POR_CONSULTA,
               relevanceLanguage="es", regionCode="CO", safeSearch="moderate")
    for it in r.get("items", []):
        candidatos.setdefault(it["id"]["videoId"], q)
    print("Consulta: %-45s -> %d resultados" % (q, len(r.get("items", []))))

# 2) Datos de cada video y selección por número de comentarios
ids = list(candidatos)
info = []
for i in range(0, len(ids), 50):
    r = llamar("videos", part="snippet,statistics", id=",".join(ids[i:i + 50]))
    for v in r.get("items", []):
        n = int(v.get("statistics", {}).get("commentCount", 0))
        if n >= MIN_COMENTARIOS_VIDEO:
            info.append({
                "video_id": v["id"], "titulo": v["snippet"]["title"], "canal": v["snippet"]["channelTitle"],
                "fecha_publicacion": v["snippet"]["publishedAt"][:10],
                "vistas": int(v.get("statistics", {}).get("viewCount", 0)),
                "comentarios_totales": n, "enlace": "https://www.youtube.com/watch?v=" + v["id"],
                "consulta": candidatos[v["id"]]})
info.sort(key=lambda d: d["comentarios_totales"], reverse=True)
info = info[:VIDEOS_A_ANALIZAR]
print("\nVideos seleccionados: %d de %d candidatos" % (len(info), len(candidatos)))

# 3) Extraer comentarios principales de cada video
filas = []
for d in info:
    comentarios, pagina = [], None
    try:
        while len(comentarios) < MAX_COMENTARIOS_POR_VIDEO:
            p = dict(part="snippet", videoId=d["video_id"], maxResults=100,
                     textFormat="plainText", order="relevance")
            if pagina:
                p["pageToken"] = pagina
            r = llamar("commentThreads", **p)
            for it in r.get("items", []):
                s = it["snippet"]["topLevelComment"]["snippet"]
                comentarios.append({"video_id": d["video_id"], "comment_id": it["id"],
                                    "texto": s.get("textDisplay", ""), "fecha": s.get("publishedAt", ""),
                                    "likes": s.get("likeCount", 0)})
            pagina = r.get("nextPageToken")
            if not pagina:
                break
    except RuntimeError as e:
        print("  - %s omitido: %s" % (d["video_id"], e))
    comentarios = comentarios[:MAX_COMENTARIOS_POR_VIDEO]
    d["comentarios_extraidos"] = len(comentarios)
    filas.extend(comentarios)
    print("  - %s | %s | %d comentarios" % (d["video_id"], d["titulo"][:50], len(comentarios)))

# 4) Guardar y descargar
hoy = datetime.now(timezone.utc).strftime("%Y-%m-%d")
df_videos = pd.DataFrame(info)
df_videos["fecha_extraccion"] = hoy
df_comentarios = pd.DataFrame(filas)
df_videos.to_csv("/content/videos_consultados.csv", index=False, encoding="utf-8-sig")
df_comentarios.to_csv("/content/comentarios_crudos.csv", index=False, encoding="utf-8-sig")
print("\nTotal de comentarios: %d | Fecha de extracción: %s" % (len(df_comentarios), hoy))
display(df_videos[["video_id", "titulo", "comentarios_totales", "comentarios_extraidos"]])
files.download("/content/videos_consultados.csv")
files.download("/content/comentarios_crudos.csv")
