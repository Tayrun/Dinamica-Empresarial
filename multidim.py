"""Análisis multidimensional (Etapa 5) - Dinámica Empresarial.

Lee el modelo estrella almacenado en data/dw.sqlite (copia del esquema dw de
SQL Server) y construye las cuatro vistas de análisis. Todos los indicadores,
gráficas y matrices salen de consultas SQL al modelo; ningún valor está escrito
a mano. Solo usa la biblioteca estándar y markupsafe (que ya trae Flask).
"""
import sqlite3
import statistics
from math import ceil, floor, log10, sqrt
from pathlib import Path

from markupsafe import Markup, escape

DB_PATH = Path(__file__).resolve().parent / "data" / "dw.sqlite"


def connect():
    """Conexión de solo lectura al modelo estrella."""
    con = sqlite3.connect(DB_PATH.as_uri() + "?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


# ---------------------------------------------------------------------------
# Formato numérico (es-CO: punto de miles, coma decimal)
# ---------------------------------------------------------------------------
def _fmt(x, d):
    s = f"{x:,.{d}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def n0(x):
    return "—" if x is None else _fmt(x, 0)


def n2(x):
    return "—" if x is None else _fmt(x, 2)


def pct(x, d=1):
    return "—" if x is None else _fmt(x, d) + " %"


def pp(x):
    return "—" if x is None else ("+" if x > 0 else "") + _fmt(x, 2).replace("-", "−") + " p. p."


# ---------------------------------------------------------------------------
# Definición del cubo: dimensiones, niveles, medidas y filtros
# ---------------------------------------------------------------------------
FROM = """FROM Fact_Estado_Financiero f
JOIN Dim_Tiempo t ON t.Tiempo_Key = f.Tiempo_Key
JOIN Dim_Tamano tm ON tm.Tamano_Key = f.Tamano_Key
JOIN Dim_Empresa e ON e.Empresa_Key = f.Empresa_Key
JOIN Dim_Condicion_Financiera c ON c.Condicion_Key = f.Condicion_Key
JOIN Dim_Tiempo tc ON tc.Ano = e.Primer_Ano_Observado"""

PERIODOS = ["Prepandemia (2016-2019)", "Pandemia (2020-2021)", "Posterior (2022-2025)"]
BLOQUES = ["2018–2019", "2020–2021"]
TAMANOS = ["Micro", "Pequeña", "Mediana", "Grande", "Sin clasificar"]
SEGMENTOS = ["Mipyme", "Gran empresa", "Sin clasificar"]
ESTADOS = ["Positivo", "Negativo", "Sin información"]
BANDAS = ["Baja (<=0.30)", "Media (0.30-0.60]", "Alta (0.60-1.00]", "Crítica (>1.00)", "Sin información"]
GRUPOS = ["Moderado", "Alto", "Sin información"]
BLOQUE_SQL = "CASE WHEN t.Ano IN (2018,2019) THEN '2018–2019' WHEN t.Ano IN (2020,2021) THEN '2020–2021' END"
SOLO_BLOQUES = "t.Ano BETWEEN 2018 AND 2021"

# clave -> (expresión SQL, etiqueta, orden fijo o None)
DIMS = {
    "ano": ("t.Ano", "Año", None),
    "bloque": (BLOQUE_SQL, "Bloque de 2 años", BLOQUES),
    "periodo": ("t.Periodo", "Periodo", PERIODOS),
    "tamano": ("tm.Tamano", "Tamaño", TAMANOS),
    "segmento": ("tm.Segmento", "Segmento", SEGMENTOS),
    "estado": ("c.Estado_Patrimonio", "Estado del patrimonio", ESTADOS),
    "banda": ("c.Banda_Endeudamiento", "Banda de endeudamiento", BANDAS),
    "grupo": ("c.Grupo_Endeudamiento", "Grupo de endeudamiento", GRUPOS),
    "anos_obs": ("CAST(e.Anos_Observados AS TEXT)", "Años observados", None),
    "anos_obs_grupo": (
        "CASE WHEN e.Anos_Observados >= 3 THEN '3 o más' ELSE CAST(e.Anos_Observados AS TEXT) END",
        "Años observados", ["1", "2", "3 o más"]),
    "cohorte": ("CAST(e.Primer_Ano_Observado AS TEXT)", "Cohorte (primer año observado)", None),
    "cohorte_periodo": ("tc.Periodo", "Periodo de ingreso", PERIODOS),
}

MEAS = {
    "registros": "COUNT(*)",
    "empresas": "COUNT(DISTINCT f.Empresa_Key)",
    "insolventes": "COALESCE(SUM(f.Insolvente), 0)",
    "base_pat": "COUNT(f.Insolvente)",
    "pct_neg": "100.0 * SUM(f.Insolvente) / NULLIF(COUNT(f.Insolvente), 0)",
    "con_razon": "COUNT(f.Razon_Endeudamiento)",
    "razon_agr": ("SUM(CASE WHEN f.Razon_Endeudamiento IS NOT NULL THEN f.Pasivo_Total END) / "
                  "NULLIF(SUM(CASE WHEN f.Razon_Endeudamiento IS NOT NULL THEN f.Activo_Total END), 0)"),
    "razon_prom": "AVG(f.Razon_Endeudamiento)",
    "alto": "COALESCE(SUM(CASE WHEN c.Grupo_Endeudamiento = 'Alto' THEN 1 ELSE 0 END), 0)",
    "e_multi": "COUNT(DISTINCT CASE WHEN e.Anos_Observados > 1 THEN f.Empresa_Key END)",
    "e_tres": "COUNT(DISTINCT CASE WHEN e.Anos_Observados >= 3 THEN f.Empresa_Key END)",
}

# Filtros: clave -> (etiqueta, dimensión del modelo)
FILTROS = {
    "periodo": ("Periodo", "Tiempo", "t.Periodo"),
    "segmento": ("Segmento", "Tamaño", "tm.Segmento"),
    "estado": ("Estado del patrimonio", "Condición financiera", "c.Estado_Patrimonio"),
    "cohorte": ("Cohorte de ingreso", "Empresa", None),
}


def sort_labels(dim, labels):
    orden = DIMS[dim][2]
    labels = list(labels)
    if orden:
        return sorted(labels, key=lambda x: orden.index(x) if x in orden else 99)
    try:
        return sorted(labels, key=lambda x: int(x))
    except ValueError:
        return sorted(labels)


def filter_options(con, key):
    if key == "periodo":
        vals = PERIODOS
    elif key == "segmento":
        vals = SEGMENTOS
    elif key == "estado":
        vals = ESTADOS
    else:
        anos = [str(r[0]) for r in con.execute(
            "SELECT DISTINCT Primer_Ano_Observado FROM Dim_Empresa ORDER BY 1")]
        return ([("todas", "Todas las cohortes"), ("ventana", "Ventana comparable 2016–2018")]
                + [(a, a) for a in anos])
    return [("todos", "Todos")] + [(v, v) for v in vals]


def parse_filters(con, args, keys, defaults=None):
    """Devuelve (filtros activos, lista de controles para la interfaz)."""
    defaults = defaults or {}
    activos, controles = {}, []
    for k in keys:
        opts = filter_options(con, k)
        validos = [o[0] for o in opts]
        neutro = validos[0]
        val = args.get(k, defaults.get(k, neutro))
        if val not in validos:
            val = defaults.get(k, neutro)
        if val != neutro:
            activos[k] = val
        controles.append({"name": k, "label": f"{FILTROS[k][0]} · dimensión {FILTROS[k][1]}",
                          "options": opts, "selected": val, "kind": "filtro"})
    return activos, controles


def choice(args, name, validos, default):
    v = args.get(name, default)
    return v if v in validos else default


def control(name, label, options, selected, kind="nivel"):
    return {"name": name, "label": label, "options": options, "selected": selected, "kind": kind}


def where_sql(filtros, extra=None):
    cond, params = [], []
    for k, v in (filtros or {}).items():
        if k == "cohorte":
            if v == "ventana":
                cond.append("e.Primer_Ano_Observado BETWEEN 2016 AND 2018")
            else:
                cond.append("e.Primer_Ano_Observado = ?")
                params.append(int(v))
        else:
            cond.append(FILTROS[k][2] + " = ?")
            params.append(v)
    cond += extra or []
    return (("WHERE " + " AND ".join(cond)) if cond else ""), params


def group(con, dims, measures, filtros=None, extra=None, want_sql=False):
    """SELECT dims, medidas FROM modelo WHERE filtros GROUP BY dims."""
    extra = list(extra or [])
    if "bloque" in dims:
        extra.append(SOLO_BLOQUES)
    sel = [DIMS[d][0] for d in dims] + [MEAS[m] for m in measures]
    w, params = where_sql(filtros, extra)
    sql = f"SELECT {', '.join(sel)}\n{FROM}\n{w}"
    if dims:
        sql += "\nGROUP BY " + ", ".join(str(i + 1) for i in range(len(dims)))
    rows = []
    for r in con.execute(sql, params).fetchall():
        r = tuple(r)
        d = tuple(str(x) for x in r[:len(dims)])
        rows.append(d + r[len(dims):])
    if want_sql:
        lit = sql
        for p in params:
            lit = lit.replace("?", repr(p), 1)
        return rows, lit
    return rows


def uno(con, measures, filtros=None, extra=None):
    """Una sola fila de medidas (sin agrupar)."""
    return group(con, [], measures, filtros, extra)[0]


# ---------------------------------------------------------------------------
# Matriz de resultados (cruce de dos dimensiones con totales)
# ---------------------------------------------------------------------------
HEAT = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]


def heat(v, vmax):
    if v is None or not vmax:
        return "", ""
    i = min(len(HEAT) - 1, int((v / vmax) * (len(HEAT) - 1) + 0.5))
    return HEAT[i], ("#0b0b0b" if i <= 2 else "#ffffff")


def matriz_raw(con, rdim, cdim, measures, filtros):
    extra = [SOLO_BLOQUES] if "bloque" in (rdim, cdim) else []
    cells = {(r[0], r[1]): r[2:] for r in group(con, [rdim, cdim], measures, filtros, extra)}
    rtot = {r[0]: r[1:] for r in group(con, [rdim], measures, filtros, extra)}
    ctot = {r[0]: r[1:] for r in group(con, [cdim], measures, filtros, extra)}
    grand = uno(con, measures, filtros, extra)
    return {
        "rdim": rdim, "cdim": cdim,
        "rows": sort_labels(rdim, rtot.keys()), "cols": sort_labels(cdim, ctot.keys()),
        "cells": cells, "rtot": rtot, "ctot": ctot, "grand": grand,
    }


def matriz_html(raw, valor, texto, sub=None, extra_col=None, total_label="Total", vmax=None):
    """Convierte la matriz cruda en estructura para la plantilla.

    valor(vals, r, c) -> número para colorear; texto(valor) -> texto visible;
    sub(vals) -> texto pequeño bajo el valor (por ejemplo la base n).
    """
    def mk(vals, r, c):
        if vals is None:
            return {"t": "—", "sub": "", "bg": "", "fg": "", "v": None}
        v = valor(vals, r, c)
        return {"t": texto(v), "sub": sub(vals) if sub else "", "v": v}

    filas = []
    for r in raw["rows"]:
        celdas = [mk(raw["cells"].get((r, c)), r, c) for c in raw["cols"]]
        tot = mk(raw["rtot"].get(r), r, None)
        extra = extra_col["fn"](r) if extra_col else None
        filas.append({"label": r, "cells": celdas, "total": tot, "extra": extra})
    fila_tot = [mk(raw["ctot"].get(c), None, c) for c in raw["cols"]]
    gran = mk(raw["grand"], None, None)
    nums = [c["v"] for f in filas for c in f["cells"] if c["v"] is not None]
    top = vmax if vmax else (max(nums) if nums else 0)
    for f in filas:
        for c in f["cells"]:
            c["bg"], c["fg"] = heat(c["v"], top)
    return {
        "row_label": DIMS[raw["rdim"]][1], "col_label": DIMS[raw["cdim"]][1],
        "cols": raw["cols"], "rows": filas, "col_totals": fila_tot, "grand": gran,
        "total_label": total_label,
        "extra_label": extra_col["label"] if extra_col else None,
        "extra_total": extra_col["total"] if extra_col else None,
    }


# ---------------------------------------------------------------------------
# Gráficas SVG (se generan en el servidor: no dependen de librerías externas)
# ---------------------------------------------------------------------------
COLORES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]
ORDINAL = [("#86b6ef", "#0b0b0b"), ("#3987e5", "#ffffff"), ("#1c5cab", "#ffffff"), ("#0d366b", "#ffffff")]
INK, INK2, GRID, SURF = "#0f172a", "#475569", "#e2e8f0", "#ffffff"
W, H, ML, MR, MT, MB = 680, 320, 58, 16, 14, 62


def _ticks(vmax):
    if not vmax or vmax <= 0:
        return [0, 1]
    raw = vmax / 5
    mag = 10 ** floor(log10(raw))
    step = next(m * mag for m in (1, 2, 2.5, 5, 10) if m * mag >= raw)
    n = int(ceil(vmax / step - 1e-9))
    return [i * step for i in range(n + 1)]


def _wrap(label, n=11):
    palabras, lineas, cur = str(label).split(), [], ""
    for p in palabras:
        if cur and len(cur) + 1 + len(p) > n:
            lineas.append(cur)
            cur = p
        else:
            cur = (cur + " " + p).strip()
    lineas.append(cur)
    return lineas[:3]


def _axes(cats, ticks, fmt_tick, ymax, ytitle):
    ph, pw = H - MT - MB, W - ML - MR
    s = []
    for tk in ticks:
        y = MT + ph - (tk / ymax) * ph if ymax else MT + ph
        s.append(f'<line x1="{ML}" x2="{W - MR}" y1="{y:.1f}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>')
        s.append(f'<text x="{ML - 8}" y="{y + 4:.1f}" text-anchor="end" font-size="11" fill="{INK2}">{escape(fmt_tick(tk))}</text>')
    band = pw / max(len(cats), 1)
    for i, c in enumerate(cats):
        x = ML + band * (i + 0.5)
        for j, ln in enumerate(_wrap(c, 12 if band > 60 else 8)):
            s.append(f'<text x="{x:.1f}" y="{H - MB + 16 + 12 * j}" text-anchor="middle" font-size="11" fill="{INK2}">{escape(ln)}</text>')
    if ytitle:
        s.append(f'<text x="14" y="{MT + ph / 2}" transform="rotate(-90 14 {MT + ph / 2})" text-anchor="middle" font-size="11" fill="{INK2}">{escape(ytitle)}</text>')
    return s


def _legend(items):
    if len(items) < 2:
        return ""
    li = "".join(f'<span class="viz-key"><i style="background:{c}"></i>{escape(n)}</span>' for n, c in items)
    return f'<div class="viz-legend">{li}</div>'


def _tabla(cats, series, fmt, cab):
    th = "".join(f"<th>{escape(s['name'])}</th>" for s in series)
    filas = ""
    for i, c in enumerate(cats):
        tds = "".join(f"<td>{escape(fmt(s['values'][i]) if s['values'][i] is not None else '—')}</td>" for s in series)
        filas += f"<tr><th scope='row'>{escape(c)}</th>{tds}</tr>"
    return Markup(f'<details class="viz-table"><summary>Ver tabla de datos</summary><table class="table table-sm mb-0">'
                  f'<thead><tr><th>{escape(cab)}</th>{th}</tr></thead><tbody>{filas}</tbody></table></details>')


def _figure(titulo, subt, legend, svg, tabla, nota=""):
    nota_html = f'<p class="viz-note">{escape(nota)}</p>' if nota else ""
    return Markup(
        f'<figure class="viz"><figcaption><strong>{escape(titulo)}</strong>'
        f'<span>{escape(subt)}</span></figcaption>{legend}'
        f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{escape(titulo)}">{svg}</svg>{nota_html}{tabla}</figure>')


def bar_chart(titulo, subt, cats, series, fmt, cab, ytitle="", etiquetar=0, nota=""):
    """Columnas agrupadas. series = [{'name','values'}]; etiqueta el valor en la punta de una serie."""
    vals = [v for s in series for v in s["values"] if v is not None]
    ticks = _ticks(max(vals) if vals else 1)
    ymax = ticks[-1] or 1
    ph, pw = H - MT - MB, W - ML - MR
    band = pw / max(len(cats), 1)
    ns = len(series)
    bw = min(24, band * 0.7 / ns)
    out = _axes(cats, ticks, lambda x: fmt(x) if x != int(x) or x < 1000 else n0(x), ymax, ytitle)
    base = MT + ph
    for i, c in enumerate(cats):
        x0 = ML + band * (i + 0.5) - (bw * ns + 2 * (ns - 1)) / 2
        for j, s in enumerate(series):
            v = s["values"][i]
            if v is None:
                continue
            h = max((v / ymax) * ph, 0)
            x, y = x0 + j * (bw + 2), base - h
            col = COLORES[j % len(COLORES)]
            tip = f"{c} · {s['name']}: {fmt(v)}"
            if h > 4:
                d = f"M{x:.1f},{base:.1f} V{y + 4:.1f} Q{x:.1f},{y:.1f} {x + 4:.1f},{y:.1f} H{x + bw - 4:.1f} Q{x + bw:.1f},{y:.1f} {x + bw:.1f},{y + 4:.1f} V{base:.1f} Z"
                out.append(f'<path class="mark" d="{d}" fill="{col}"><title>{escape(tip)}</title></path>')
            else:
                out.append(f'<rect class="mark" x="{x:.1f}" y="{base - max(h, 1):.1f}" width="{bw:.1f}" height="{max(h, 1):.1f}" fill="{col}"><title>{escape(tip)}</title></rect>')
            if etiquetar is not None and j == etiquetar:
                out.append(f'<text x="{x + bw / 2:.1f}" y="{y - 5:.1f}" text-anchor="middle" font-size="11" font-weight="600" fill="{INK}">{escape(fmt(v))}</text>')
    out.append(f'<line x1="{ML}" x2="{W - MR}" y1="{base}" y2="{base}" stroke="#94a3b8" stroke-width="1"/>')
    leg = _legend([(s["name"], COLORES[j % len(COLORES)]) for j, s in enumerate(series)])
    return _figure(titulo, subt, leg, "".join(out), _tabla(cats, series, fmt, cab), nota)


def line_chart(titulo, subt, cats, series, fmt, cab, ytitle="", nota=""):
    vals = [v for s in series for v in s["values"] if v is not None]
    ticks = _ticks(max(vals) if vals else 1)
    ymax = ticks[-1] or 1
    ph, pw = H - MT - MB, W - ML - MR
    band = pw / max(len(cats), 1)
    out = _axes(cats, ticks, fmt, ymax, ytitle)
    base = MT + ph
    for j, s in enumerate(series):
        col = s.get("color") or COLORES[j % len(COLORES)]
        pts = [(ML + band * (i + 0.5), base - (v / ymax) * ph if v is not None else None, v, cats[i])
               for i, v in enumerate(s["values"])]
        seg = []
        for x, y, v, c in pts + [(0, None, None, "")]:
            if y is None:
                if len(seg) > 1:
                    out.append(f'<polyline points="{" ".join(seg)}" fill="none" stroke="{col}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>')
                seg = []
            else:
                seg.append(f"{x:.1f},{y:.1f}")
        for x, y, v, c in pts:
            if y is not None:
                tip = f"{c} · {s['name']}: {fmt(v)}"
                out.append(f'<circle class="mark" cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{col}" stroke="{SURF}" stroke-width="2"><title>{escape(tip)}</title></circle>')
    out.append(f'<line x1="{ML}" x2="{W - MR}" y1="{base}" y2="{base}" stroke="#94a3b8" stroke-width="1"/>')
    series = [{"name": s["name"], "values": s["values"]} for s in series]
    leg = _legend([(s["name"], COLORES[j % len(COLORES)]) for j, s in enumerate(series)])
    return _figure(titulo, subt, leg, "".join(out), _tabla(cats, series, fmt, cab), nota)


def stacked100(titulo, subt, cats, partes, cab, nota=""):
    """Columnas apiladas al 100 %. partes = [{'name','values'(cantidades)}]; las cantidades se pasan a porcentaje."""
    ph, pw = H - MT - MB, W - ML - MR
    band = pw / max(len(cats), 1)
    bw = min(48, band * 0.6)
    out = _axes(cats, [0, 25, 50, 75, 100], lambda x: f"{int(x)} %", 100, "% de registros")
    base = MT + ph
    tot = [sum(p["values"][i] or 0 for p in partes) for i in range(len(cats))]
    ser_pct = [{"name": p["name"], "values": [(p["values"][i] / tot[i] * 100) if tot[i] else None
                                              for i in range(len(cats))]} for p in partes]
    for i, c in enumerate(cats):
        x = ML + band * (i + 0.5) - bw / 2
        acum = 0
        for j, p in enumerate(partes):
            n = p["values"][i] or 0
            if not tot[i] or not n:
                continue
            h = n / tot[i] * ph
            y = base - acum - h
            col, tc = ORDINAL[j % len(ORDINAL)]
            tip = f"{c} · {p['name']}: {pct(n / tot[i] * 100)} ({n0(n)} de {n0(tot[i])} registros)"
            out.append(f'<rect class="mark" x="{x:.1f}" y="{y + 1:.1f}" width="{bw:.1f}" height="{max(h - 2, 1):.1f}" rx="3" fill="{col}"><title>{escape(tip)}</title></rect>')
            if h >= 18 and bw >= 40:
                out.append(f'<text x="{x + bw / 2:.1f}" y="{y + h / 2 + 4:.1f}" text-anchor="middle" font-size="11" fill="{tc}">{escape(pct(n / tot[i] * 100, 0))}</text>')
            acum += h
        out.append(f'<text x="{x + bw / 2:.1f}" y="{MT - 2}" text-anchor="middle" font-size="10" fill="{INK2}">n={n0(tot[i])}</text>')
    leg = _legend([(p["name"], ORDINAL[j % len(ORDINAL)][0]) for j, p in enumerate(partes)])
    return _figure(titulo, subt, leg, "".join(out), _tabla(cats, ser_pct, lambda v: pct(v), cab), nota)


# ---------------------------------------------------------------------------
# Utilidades comunes de las vistas
# ---------------------------------------------------------------------------
def indicador(titulo, valor, detalle, icono="bi-graph-up"):
    return {"titulo": titulo, "valor": valor, "detalle": detalle, "icono": icono}


def seleccion(filtros, niveles, pivot):
    """Texto de la selección activa y etiquetas de las operaciones OLAP.

    niveles: lista de (etiqueta, nivel_actual, nivel_mas_alto).
    Roll-up = se está en el nivel más agregado de la jerarquía; Drill-down = en uno más detallado.
    """
    ops, partes = [], []
    for k, v in filtros.items():
        txt = "Ventana comparable 2016–2018" if v == "ventana" else v
        partes.append(f"{FILTROS[k][0]} = {txt}")
    if len(filtros) == 1:
        ops.append(("Slice", "un valor de la dimensión " + FILTROS[list(filtros)[0]][1]))
    elif len(filtros) >= 2:
        ops.append(("Dice", "filtros combinados sobre " + " y ".join(FILTROS[k][1] for k in filtros)))
    for etq, actual, alto in niveles:
        partes.append(f"{etq} = {DIMS[actual][1]}")
        ops.append(("Roll-up" if actual == alto else "Drill-down", f"{etq}: {DIMS[actual][1]}"))
    if pivot:
        ops.append(("Pivot", "filas y columnas de la matriz intercambiadas"))
    return (partes or ["Sin filtros"]), ops


def media_activo(con, dimkey, filtros):
    """Mediana del activo por nivel (se calcula en Python: SQLite no trae MEDIAN)."""
    w, params = where_sql(filtros, ["f.Activo_Total IS NOT NULL"] + ([SOLO_BLOQUES] if dimkey == "bloque" else []))
    sql = f"SELECT {DIMS[dimkey][0]}, f.Activo_Total {FROM} {w}"
    por = {}
    for r in con.execute(sql, params):
        por.setdefault(str(r[0]), []).append(r[1])
    return {k: (statistics.median(v), len(v)) for k, v in por.items()}


def cobertura_2017(con):
    return uno(con, ["registros"], None, ["t.Ano = 2017"])[0]


NIVEL_TIEMPO = [("periodo", "Periodo (nivel alto)"), ("bloque", "Bloque de 2 años (2018–2021)"), ("ano", "Año (nivel detallado)")]
NIVEL_TAMANO = [("segmento", "Segmento (nivel alto)"), ("tamano", "Tamaño (nivel detallado)")]
