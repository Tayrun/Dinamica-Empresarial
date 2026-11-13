"""Las cuatro vistas del Análisis multidimensional y sus conocimientos documentados."""
from math import sqrt

import multidim as m
from multidim import n0, n2, pct, pp

MIN_BASE = 10  # no se grafican celdas con menos registros que esto


def _ctrl_pivot(piv):
    return m.control("pivot", "Pivotar matriz (intercambiar filas y columnas)",
                     [("0", "No"), ("1", "Sí")], "1" if piv else "0", "pivot")


# ---------------------------------------------------------------------------
# Vista 1: Tiempo x Tamaño -> % de patrimonio negativo
# ---------------------------------------------------------------------------
def vista1(con, a):
    fil, ctr_f = m.parse_filters(con, a, ["periodo", "segmento"])
    nt = m.choice(a, "nivel_tiempo", ["periodo", "bloque", "ano"], "periodo")
    ns = m.choice(a, "nivel_tamano", ["segmento", "tamano"], "segmento")
    med = m.choice(a, "medida", ["pct_neg", "insolventes", "base_pat"], "pct_neg")
    piv = m.choice(a, "pivot", ["0", "1"], "0") == "1"
    ms = ["pct_neg", "insolventes", "base_pat"]

    tot = m.uno(con, ms + ["registros"], fil)
    fil_eq = {k: v for k, v in fil.items() if k != "periodo"}
    eq = {r[0]: r[1:] for r in m.group(con, ["bloque"], ms, fil_eq)}
    pre, pan = eq.get("2018–2019"), eq.get("2020–2021")
    dif = (pan[0] - pre[0]) if pre and pan and pre[0] is not None and pan[0] is not None else None
    det2 = (f"{pct(pre[0], 2)} (n={n0(pre[2])}) → {pct(pan[0], 2)} (n={n0(pan[2])}); ignora el filtro de periodo"
            if pre and pan else "Sin datos para esta selección")
    indicadores = [
        m.indicador("% con patrimonio negativo", pct(tot[0], 2),
                    f"{n0(tot[1])} de {n0(tot[2])} registros con patrimonio conocido (el denominador excluye los vacíos)", "bi-percent"),
        m.indicador("Variación entre periodos equivalentes", pp(dif), "2018–2019 → 2020–2021: " + det2, "bi-arrow-left-right"),
        m.indicador("Cobertura del patrimonio", pct(tot[2] / tot[3] * 100 if tot[3] else None),
                    f"{n0(tot[2])} de {n0(tot[3])} registros tienen patrimonio; el resto no se sabe", "bi-clipboard-data"),
    ]

    cel = {(r[0], r[1]): r[2:] for r in m.group(con, [nt, ns], ["pct_neg", "base_pat"], fil)}
    cats = m.sort_labels(nt, {k[0] for k in cel})
    segs = m.sort_labels(ns, {k[1] for k in cel})
    series = [{"name": s, "values": [(cel[(c, s)][0] if (c, s) in cel and cel[(c, s)][1] >= MIN_BASE else None) for c in cats]}
              for s in segs]
    g1 = m.line_chart(f"% con patrimonio negativo por {m.DIMS[nt][1].lower()} y {m.DIMS[ns][1].lower()}",
                      "Una línea por nivel de tamaño", cats, series, lambda v: pct(v), m.DIMS[nt][1], "% con patrimonio negativo",
                      f"No se grafican celdas con menos de {MIN_BASE} registros con patrimonio conocido; la matriz las muestra todas con su base (n).")
    bt = {r[0]: r[1] for r in m.group(con, [nt], ["base_pat"], fil)}
    cats2 = m.sort_labels(nt, bt.keys())
    g2 = m.bar_chart(f"Registros con patrimonio conocido por {m.DIMS[nt][1].lower()}", "Es la base (denominador) de cada porcentaje",
                     cats2, [{"name": "Registros con patrimonio conocido", "values": [bt[c] for c in cats2]}],
                     n0, m.DIMS[nt][1], "Registros", 0)

    raw = m.matriz_raw(con, ns, nt, ms, fil) if piv else m.matriz_raw(con, nt, ns, ms, fil)
    idx = ms.index(med)
    es_pct = med == "pct_neg"
    mat = m.matriz_html(raw, lambda v, r, c: v[idx], pct if es_pct else n0,
                        (lambda v: f"n={n0(v[2])}") if es_pct else None)
    titulo_mat = {"pct_neg": "% con patrimonio negativo (denominador: registros con patrimonio conocido de cada celda)",
                  "insolventes": "Registros con patrimonio negativo (conteo)",
                  "base_pat": "Registros con patrimonio conocido (base)"}[med]

    cand = [(r[0], r[1], r[2]) for r in m.group(con, [nt], ["pct_neg", "base_pat"], fil)
            if r[1] is not None and r[2] >= 30]
    if cand:
        hi, lo = max(cand, key=lambda x: x[1]), min(cand, key=lambda x: x[1])
        interp = (f"En la selección, {pct(tot[0], 2)} de los registros con patrimonio conocido tiene patrimonio negativo. "
                  f"Entre los niveles de {m.DIMS[nt][1].lower()} con al menos 30 registros de base, el valor más alto es {hi[0]} "
                  f"({pct(hi[1], 2)}, n={n0(hi[2])}) y el más bajo es {lo[0]} ({pct(lo[1], 2)}, n={n0(lo[2])}). "
                  "Las diferencias deben leerse junto con la base: una celda con pocos casos cambia mucho con un solo registro.")
    else:
        interp = "La selección no tiene niveles con base suficiente (30 registros) para comparar."
    partes, ops = m.seleccion(fil, [("Nivel de tiempo", nt, "periodo"), ("Nivel de tamaño", ns, "segmento")], piv)
    return {
        "n": 1, "titulo": "Insolvencia patrimonial en el tiempo y por tamaño",
        "pregunta": "¿Cambió el porcentaje de empresas con patrimonio negativo entre periodos equivalentes y entre segmentos de tamaño?",
        "profundiza": ("La etapa 4 reportó 323 empresas insolventes sobre 18.651 NIT (1,73 %), contando como «no insolventes» a las empresas "
                       "sin patrimonio reportado. Aquí el denominador son solo los registros con patrimonio conocido, se comparan "
                       "bloques equivalentes de dos años (2018–2019 frente a 2020–2021) y se sube y baja por las jerarquías de tiempo y tamaño."),
        "dimensiones": ["Tiempo", "Tamaño"],
        "medidas": ["% con patrimonio negativo = registros con patrimonio negativo / registros con patrimonio conocido"],
        "jerarquias": ["Tiempo: Año → Bloque de 2 años → Periodo", "Tamaño: Tamaño → Segmento"],
        "filtros": ctr_f,
        "controles": [m.control("nivel_tiempo", "Nivel de tiempo (Año → Bloque → Periodo)", m.NIVEL_TIEMPO, nt),
                      m.control("nivel_tamano", "Nivel de tamaño (Tamaño → Segmento)", m.NIVEL_TAMANO, ns),
                      m.control("medida", "Medida de la matriz",
                                [("pct_neg", "% con patrimonio negativo"), ("insolventes", "Registros con patrimonio negativo"),
                                 ("base_pat", "Base: registros con patrimonio conocido")], med, "medida"),
                      _ctrl_pivot(piv)],
        "seleccion": partes, "operaciones": ops, "indicadores": indicadores, "graficos": [g1, g2],
        "matriz": mat, "matriz_titulo": titulo_mat,
        "matriz_nota": "Cada celda se recalcula con su propio denominador al cambiar de nivel; los totales no son sumas de porcentajes.",
        "interpretacion": interp,
        "limitacion": ("El patrimonio está vacío en cerca del 63 % de los registros y el tamaño se asigna solo cuando hay activo, "
                       "por lo que el grupo «Sin clasificar» domina la base. Las celdas de Micro, Gran empresa y de los años "
                       "2017 y 2022–2025 tienen muy pocos casos. Los registros de una misma empresa no son independientes."),
        "decision": ("Completar el patrimonio y el activo de las empresas sin clasificar antes de afirmar un efecto de la pandemia, "
                     "y hacer seguimiento al segmento Gran empresa, donde los casos pasaron de 1 a 4."),
    }


# ---------------------------------------------------------------------------
# Vista 2: Tamaño x Condición financiera -> endeudamiento
# ---------------------------------------------------------------------------
def vista2(con, a):
    fil, ctr_f = m.parse_filters(con, a, ["periodo", "estado"])
    ns = m.choice(a, "nivel_tamano", ["segmento", "tamano"], "segmento")
    med = m.choice(a, "medida", ["registros", "pct_fila"], "registros")
    piv = m.choice(a, "pivot", ["0", "1"], "0") == "1"

    tot = m.uno(con, ["razon_agr", "con_razon", "registros", "alto"], fil)
    indicadores = [
        m.indicador("Razón de endeudamiento agregada", n2(tot[0]),
                    f"Σ pasivos / Σ activos de {n0(tot[1])} registros con razón conocida", "bi-bank"),
        m.indicador("Registros con razón conocida", n0(tot[1]),
                    f"{pct(tot[1] / tot[2] * 100 if tot[2] else None)} de {n0(tot[2])} registros de la selección", "bi-clipboard-check"),
        m.indicador("Endeudamiento alto (> 0,60)", pct(tot[3] / tot[1] * 100 if tot[1] else None),
                    f"{n0(tot[3])} de {n0(tot[1])} registros con razón conocida (denominador: registros con razón)", "bi-exclamation-diamond"),
    ]

    por = {(r[0], r[1]): r[2] for r in m.group(con, [ns, "banda"], ["registros"], fil)}
    cats = m.sort_labels(ns, {k[0] for k in por})
    bandas = m.BANDAS[:4]
    cats_ok = [c for c in cats if sum(por.get((c, b), 0) for b in bandas) > 0]
    partes = [{"name": b, "values": [por.get((c, b), 0) for c in cats_ok]} for b in bandas]
    sin = [c for c in cats if c not in cats_ok]
    g1 = m.stacked100(f"Distribución del endeudamiento por {m.DIMS[ns][1].lower()}",
                      "Solo registros con razón de endeudamiento conocida", cats_ok, partes, m.DIMS[ns][1],
                      ("Sin razón conocida (no se grafican): " + ", ".join(sin) + ".") if sin else "")
    rz = {r[0]: r[1:] for r in m.group(con, [ns], ["razon_agr", "razon_prom", "con_razon"], fil)}
    cats2 = [c for c in m.sort_labels(ns, rz.keys()) if rz[c][2] > 0]
    g2 = m.bar_chart(f"Razón de endeudamiento por {m.DIMS[ns][1].lower()}: agregada frente a promedio simple",
                     "Agregada = Σ pasivos / Σ activos; simple = promedio de las razones de cada registro", cats2,
                     [{"name": "Agregada (Σ pasivos / Σ activos)", "values": [rz[c][0] for c in cats2]},
                      {"name": "Promedio simple de razones", "values": [rz[c][1] for c in cats2]}],
                     n2, m.DIMS[ns][1], "Razón (pasivo / activo)", 0)

    raw = m.matriz_raw(con, "banda", ns, ["registros"], fil) if piv else m.matriz_raw(con, ns, "banda", ["registros"], fil)
    if med == "registros":
        mat = m.matriz_html(raw, lambda v, r, c: v[0], n0)
        titulo_mat = "Registros por " + m.DIMS[raw["rdim"]][1].lower() + " y " + m.DIMS[raw["cdim"]][1].lower()
    else:
        def pf(v, r, c):
            base = raw["rtot"].get(r) if r is not None else raw["grand"]
            return (v[0] / base[0] * 100) if base and base[0] else None
        mat = m.matriz_html(raw, pf, pct, lambda v: f"n={n0(v[0])}", vmax=100)
        titulo_mat = "% de registros de cada fila (denominador: total de registros de la fila, incluida «Sin información»)"

    interp_p = []
    for c in cats_ok:
        mod, alt = por_g(con, ns, c, fil)
        if mod + alt:
            interp_p.append(f"{c}: {pct(alt / (mod + alt) * 100)} de los registros con razón tiene endeudamiento alto")
    interp = ("Entre los registros con razón conocida, " + "; ".join(interp_p) + ". " if interp_p else "") + \
        ("Los niveles sin razón conocida no pueden compararse. " if sin else "") + \
        "La razón agregada pesa más a las empresas con más activos; el promedio simple trata igual a todas."
    partes_s, ops = m.seleccion(fil, [("Nivel de tamaño", ns, "segmento")], piv)
    return {
        "n": 2, "titulo": "Perfil de endeudamiento por tamaño",
        "pregunta": "¿En qué bandas de endeudamiento se concentra cada tamaño de empresa y cuánta información falta para saberlo?",
        "profundiza": ("La etapa 4 comparó promedio, mediana y desviación del endeudamiento por tamaño. Aquí se pasa a bandas de endeudamiento "
                       "(distribución, no solo promedios), se contrasta la razón agregada con el promedio simple y se mide la información faltante."),
        "dimensiones": ["Tamaño", "Condición financiera"],
        "medidas": ["Razón de endeudamiento agregada = Σ pasivos / Σ activos", "Registros por banda de endeudamiento"],
        "jerarquias": ["Tamaño: Tamaño → Segmento", "Condición financiera: Banda (Baja, Media, Alta, Crítica) → Grupo (Moderado, Alto)"],
        "filtros": ctr_f,
        "controles": [m.control("nivel_tamano", "Nivel de tamaño (Tamaño → Segmento)", m.NIVEL_TAMANO, ns),
                      m.control("medida", "Medida de la matriz",
                                [("registros", "Registros (conteo)"), ("pct_fila", "% de la fila")], med, "medida"),
                      _ctrl_pivot(piv)],
        "seleccion": partes_s, "operaciones": ops, "indicadores": indicadores, "graficos": [g1, g2],
        "matriz": mat, "matriz_titulo": titulo_mat,
        "matriz_nota": "Las bandas se definieron por el equipo sobre la razón pasivo/activo: Baja ≤ 0,30; Media hasta 0,60; Alta hasta 1,00; Crítica > 1,00.",
        "interpretacion": interp,
        "limitacion": ("La razón de endeudamiento existe en pocos registros (alrededor del 3 %) porque exige activo y pasivo a la vez, "
                       "y el tamaño depende del activo. Las bandas son una definición del equipo. «Micro» tiene muy pocos registros."),
        "decision": ("Antes de fijar umbrales de endeudamiento por tamaño, completar el pasivo de las empresas. Mientras tanto, usar la razón "
                     "agregada para medir la exposición del conjunto y las bandas para clasificar empresas individuales."),
    }


def por_g(con, ns, c, fil):
    f2 = dict(fil)
    rows = {r[1]: r[2] for r in m.group(con, [ns, "grupo"], ["registros"], f2) if r[0] == c}
    return rows.get("Moderado", 0), rows.get("Alto", 0)


# ---------------------------------------------------------------------------
# Vista 3: Empresa x Condición financiera -> años observados y solvencia
# ---------------------------------------------------------------------------
def vista3(con, a):
    fil, ctr_f = m.parse_filters(con, a, ["cohorte", "periodo", "segmento"], {"cohorte": "ventana"})
    ne = m.choice(a, "nivel_empresa", ["anos_obs_grupo", "anos_obs"], "anos_obs_grupo")
    med = m.choice(a, "medida", ["registros", "pct_fila"], "registros")
    piv = m.choice(a, "pivot", ["0", "1"], "0") == "1"

    g3 = {r[0]: r[1:] for r in m.group(con, ["anos_obs_grupo"], ["pct_neg", "insolventes", "base_pat"], fil)}
    indicadores = []
    for k, ico in (("1", "bi-1-circle"), ("2", "bi-2-circle"), ("3 o más", "bi-3-circle")):
        v = g3.get(k)
        etq = "% con patrimonio negativo: " + ("1 año observado" if k == "1" else f"{k} años observados" if k == "2" else "3 o más años observados")
        indicadores.append(m.indicador(etq, pct(v[0], 2) if v else "—",
                                       f"{n0(v[1])} de {n0(v[2])} registros con patrimonio conocido" if v else "Sin datos", ico))

    pn = {(r[0]): r[1:] for r in m.group(con, [ne], ["pct_neg", "base_pat"], fil)}
    cats = m.sort_labels(ne, pn.keys())
    g1 = m.bar_chart(f"% con patrimonio negativo según años observados",
                     "Años observados = años en que la empresa aparece en el modelo (no es su edad)", cats,
                     [{"name": "% con patrimonio negativo", "values": [pn[c][0] if pn[c][1] >= MIN_BASE else None for c in cats]}],
                     lambda v: pct(v, 1), "Años observados", "% con patrimonio negativo", 0,
                     f"Se omiten niveles con menos de {MIN_BASE} registros con patrimonio conocido.")
    md = m.media_activo(con, ne, fil)
    cats2 = [c for c in m.sort_labels(ne, md.keys()) if md[c][1] >= MIN_BASE]
    g2 = m.bar_chart("Activo mediano según años observados", "Mediana del activo total, en las unidades de la fuente (solo registros con activo)",
                     cats2, [{"name": "Activo mediano", "values": [md[c][0] for c in cats2]}], n0, "Años observados", "Activo total", 0,
                     "Se usa la mediana porque unos pocos activos enormes distorsionan el promedio.")

    raw = m.matriz_raw(con, "estado", ne, ["registros"], fil) if piv else m.matriz_raw(con, ne, "estado", ["registros"], fil)

    def pneg(r):
        if piv:
            return None
        pos = raw["cells"].get((r, "Positivo"), (0,))[0]
        neg = raw["cells"].get((r, "Negativo"), (0,))[0]
        return pct(neg / (pos + neg) * 100, 2) if pos + neg else "—"
    if med == "registros":
        mat = m.matriz_html(raw, lambda v, r, c: v[0], n0)
        titulo_mat = "Registros por " + m.DIMS[raw["rdim"]][1].lower() + " y " + m.DIMS[raw["cdim"]][1].lower()
    else:
        def pf(v, r, c):
            base = raw["rtot"].get(r) if r is not None else raw["grand"]
            return (v[0] / base[0] * 100) if base and base[0] else None
        mat = m.matriz_html(raw, pf, pct, lambda v: f"n={n0(v[0])}", vmax=100)
        titulo_mat = "% de registros de cada fila (denominador: total de registros de la fila)"
    if not piv:
        pos = raw["ctot"].get("Positivo", (0,))[0]
        neg = raw["ctot"].get("Negativo", (0,))[0]
        mat["extra_label"] = "% negativo (sobre conocidos)"
        mat["extra_total"] = pct(neg / (pos + neg) * 100, 2) if pos + neg else "—"
        for f in mat["rows"]:
            f["extra"] = pneg(f["label"])

    v1, v3 = g3.get("1"), g3.get("3 o más")
    if v1 and v3 and v1[0] is not None and v3[0] is not None:
        interp = (f"En la selección, las empresas observadas un solo año tienen {pct(v1[0], 2)} de registros con patrimonio negativo "
                  f"(n={n0(v1[2])}) frente a {pct(v3[0], 2)} de las observadas tres o más años (n={n0(v3[2])}). "
                  "Es una asociación observada dentro de la muestra; no indica que observarse más años haga más solvente a una empresa, "
                  "y una empresa en dificultades puede dejar de aparecer.")
    else:
        interp = "La selección no tiene datos suficientes en los niveles de años observados."
    partes, ops = m.seleccion(fil, [("Nivel de años observados", ne, "anos_obs_grupo")], piv)
    return {
        "n": 3, "titulo": "Años observados y solvencia de las empresas",
        "pregunta": "¿Las empresas que aparecen más años en el modelo se diferencian en solvencia y en tamaño de las que aparecen un solo año?",
        "profundiza": ("La etapa 4 trabajó empresa-año sin una dimensión de empresa. Aquí se incorpora la dimensión Empresa (años observados y "
                       "cohorte de ingreso), que permite comparar empresas según cuánto aparecen en el modelo, con una ventana de ingreso comparable."),
        "dimensiones": ["Empresa", "Condición financiera"],
        "medidas": ["% con patrimonio negativo", "Activo mediano", "Registros"],
        "jerarquias": ["Empresa: Años observados (1, 2, 3, 4, 5) → Grupo (1, 2, 3 o más); NIT → Cohorte de ingreso"],
        "filtros": ctr_f,
        "controles": [m.control("nivel_empresa", "Nivel de años observados (detalle → grupo)",
                                [("anos_obs_grupo", "Grupo: 1, 2, 3 o más (nivel alto)"), ("anos_obs", "Detalle: 1, 2, 3, 4, 5 (nivel detallado)")], ne),
                      m.control("medida", "Medida de la matriz", [("registros", "Registros (conteo)"), ("pct_fila", "% de la fila")], med, "medida"),
                      _ctrl_pivot(piv)],
        "seleccion": partes, "operaciones": ops, "indicadores": indicadores, "graficos": [g1, g2],
        "matriz": mat, "matriz_titulo": titulo_mat,
        "matriz_nota": ("La ventana comparable 2016–2018 incluye solo empresas que ingresaron a esos años, con la misma oportunidad de aparecer "
                        "en años posteriores. Las cohortes recientes no pueden acumular tantos años."),
        "interpretacion": interp,
        "limitacion": ("«Años observados» cuenta apariciones en una muestra, no la vida de la empresa: no aparecer no equivale a cerrar. "
                       "El activo solo se conoce en cerca del 38 % de los registros. Es una asociación, no una relación causal."),
        "decision": ("Incluir «años observados» y el tamaño como variables de seguimiento en el modelo predictivo de la siguiente etapa, "
                     "sin tratarlos como causa de solvencia."),
    }


# ---------------------------------------------------------------------------
# Vista 4: Empresa x Tiempo -> cohortes de ingreso
# ---------------------------------------------------------------------------
def vista4(con, a):
    fil, ctr_f = m.parse_filters(con, a, ["segmento", "estado"])
    nt = m.choice(a, "nivel_tiempo", ["periodo", "bloque", "ano"], "ano")
    nc = m.choice(a, "nivel_cohorte", ["cohorte_periodo", "cohorte"], "cohorte")
    med = m.choice(a, "medida", ["empresas", "reaparicion"], "empresas")
    piv = m.choice(a, "pivot", ["0", "1"], "0") == "1"

    tot = m.uno(con, ["empresas", "e_multi", "e_tres"], fil)
    indicadores = [
        m.indicador("Empresas distintas", n0(tot[0]), "Conteo de NIT distintos en la selección (no de registros)", "bi-buildings"),
        m.indicador("Con más de un año observado", pct(tot[1] / tot[0] * 100 if tot[0] else None),
                    f"{n0(tot[1])} de {n0(tot[0])} empresas (denominador: empresas de la selección)", "bi-arrow-repeat"),
        m.indicador("Con 3 o más años observados", pct(tot[2] / tot[0] * 100 if tot[0] else None),
                    f"{n0(tot[2])} de {n0(tot[0])} empresas", "bi-collection"),
    ]

    raw = m.matriz_raw(con, nt, nc, ["empresas"], fil) if piv else m.matriz_raw(con, nc, nt, ["empresas"], fil)
    tam = {r[0]: r[1] for r in m.group(con, [nc], ["empresas"], fil)}
    if med == "empresas":
        mat = m.matriz_html(raw, lambda v, r, c: v[0], n0)
        titulo_mat = "Empresas distintas por " + m.DIMS[raw["rdim"]][1].lower() + " y " + m.DIMS[raw["cdim"]][1].lower()
    else:
        def tamano_coh(r, c):
            return tam.get(c if piv else r)
        def pf(v, r, c):
            d = tamano_coh(r, c) if (r is not None and c is not None) else None
            if d is None:
                return None
            return v[0] / d * 100
        mat = m.matriz_html(raw, pf, pct, lambda v: f"n={n0(v[0])}", vmax=100)
        titulo_mat = "% de las empresas de cada cohorte presentes (denominador: empresas distintas de la cohorte)"
        for f in mat["rows"]:
            f["total"] = {"t": "—", "sub": "", "bg": "", "fg": "", "v": None}
        mat["col_totals"] = [{"t": "—", "sub": "", "bg": "", "fg": "", "v": None} for _ in mat["cols"]]
        mat["grand"] = {"t": "—", "sub": "", "bg": "", "fg": "", "v": None}

    cel = {(r[0], r[1]): r[2] for r in m.group(con, [nc, nt], ["empresas"], fil,
                                                [m.SOLO_BLOQUES] if nt == "bloque" else None)}
    top = sorted(tam, key=lambda c: -tam[c])[:5]
    top = m.sort_labels(nc, top)
    cats = m.sort_labels(nt, {k[1] for k in cel})
    series = [{"name": ("Cohorte " + c) if nc == "cohorte" else c, "values": [cel.get((c, x)) for x in cats]} for c in top]
    g1 = m.line_chart(f"Empresas distintas por {m.DIMS[nt][1].lower()} y cohorte de ingreso",
                      "Una línea por cohorte (las 5 más grandes de la selección)", cats, series, n0, m.DIMS[nt][1], "Empresas distintas",
                      "La cohorte 2016 es la primera observada: no significa que las empresas se crearan en 2016.")

    if nc == "cohorte":
        cy = {(int(r[0]), int(r[1])): r[2] for r in m.group(con, ["cohorte", "ano"], ["empresas"], fil)}
        coh = [c for c in range(2016, 2021) if tam.get(str(c), 0) >= 100]
        vals = [(cy.get((c, c + 1), 0) / tam[str(c)] * 100) for c in coh]
        g2 = m.bar_chart("Reaparición al año siguiente por cohorte", "% de empresas de la cohorte que aparecen en el año de ingreso + 1",
                         [str(c) for c in coh], [{"name": "% que reaparece al año siguiente", "values": vals}], lambda v: pct(v, 1),
                         "Cohorte", "% de la cohorte", 0,
                         f"La cohorte 2016 casi no reaparece en 2017 porque 2017 solo tiene {n0(m.cobertura_2017(con))} registros en todo el modelo: es un hueco de datos, no cierres.")
    else:
        multi = {r[0]: r[1:] for r in m.group(con, [nc], ["empresas", "e_multi"], fil)}
        cats3 = m.sort_labels(nc, multi.keys())
        g2 = m.bar_chart("Empresas con más de un año observado por periodo de ingreso", "% de las empresas de cada grupo",
                         cats3, [{"name": "% con más de un año observado",
                                  "values": [(multi[c][1] / multi[c][0] * 100) if multi[c][0] else None for c in cats3]}],
                         lambda v: pct(v, 1), "Periodo de ingreso", "% de empresas", 0)
    c17 = m.cobertura_2017(con)
    interp = ("El tamaño de cada cohorte aparece en la columna Total de la matriz (empresas distintas). "
              "Las cohortes más recientes tienen menos tiempo para reaparecer, así que solo son comparables ventanas de la misma duración. "
              f"El año 2017 tiene apenas {n0(c17)} registros en el modelo, lo que distorsiona cualquier lectura que lo incluya.")
    partes, ops = m.seleccion(fil, [("Nivel de tiempo", nt, "periodo"), ("Nivel de cohorte", nc, "cohorte_periodo")], piv)
    return {
        "n": 4, "titulo": "Cohortes de ingreso y reaparición de empresas",
        "pregunta": "¿Cuántas empresas de cada año de ingreso al modelo reaparecen en los años siguientes?",
        "profundiza": ("La etapa 4 describió las empresas año por año. Aquí se sigue a cada cohorte (empresas agrupadas por su primer año observado) "
                       "a lo largo del tiempo, con una matriz cohorte × año que la etapa anterior no tenía."),
        "dimensiones": ["Empresa", "Tiempo"],
        "medidas": ["Empresas distintas = conteo de NIT distintos", "Reaparición = empresas de la cohorte presentes en el año / empresas distintas de la cohorte"],
        "jerarquias": ["Empresa: NIT → Cohorte (primer año observado) → Periodo de ingreso", "Tiempo: Año → Bloque de 2 años → Periodo"],
        "filtros": ctr_f,
        "controles": [m.control("nivel_tiempo", "Nivel de tiempo (Año → Bloque → Periodo)",
                                [("ano", "Año (nivel detallado)"), ("bloque", "Bloque de 2 años (2018–2021)"), ("periodo", "Periodo (nivel alto)")], nt),
                      m.control("nivel_cohorte", "Nivel de cohorte (Cohorte → Periodo de ingreso)",
                                [("cohorte_periodo", "Periodo de ingreso (nivel alto)"), ("cohorte", "Año de ingreso (nivel detallado)")], nc),
                      m.control("medida", "Medida de la matriz", [("empresas", "Empresas distintas"), ("reaparicion", "% de reaparición de la cohorte")], med, "medida"),
                      _ctrl_pivot(piv)],
        "seleccion": partes, "operaciones": ops, "indicadores": indicadores, "graficos": [g1, g2],
        "matriz": mat, "matriz_titulo": titulo_mat,
        "matriz_nota": ("Los totales de empresas son conteos de NIT distintos, no sumas de las celdas: una empresa aparece en varias columnas. "
                        "Con los filtros activos, una empresa cuenta en una celda solo si tiene registros que cumplen el filtro."),
        "interpretacion": interp,
        "limitacion": ("Reaparecer en el modelo no es sobrevivir: los datos son una muestra y no hay una variable de cierre. "
                       "La cohorte 2016 está censurada a la izquierda y el año 2017 casi no tiene registros."),
        "decision": ("Para medir permanencia, usar solo ventanas de un año completamente observadas (de 2018→2019 a 2020→2021), "
                     "excluir 2017 y pedir al origen la serie completa antes de hablar de supervivencia."),
    }


VISTAS = {1: vista1, 2: vista2, 3: vista3, 4: vista4}


# ---------------------------------------------------------------------------
# Conocimientos multidimensionales documentados (2 por vista, 8 en total)
# ---------------------------------------------------------------------------
def _z(p1, n1, p2, n2, x1, x2):
    p = (x1 + x2) / (n1 + n2)
    se = sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    return (p2 - p1) / se if se else 0.0


def _sube(a, b):
    return "subió" if b > a else "bajó" if b < a else "se mantuvo"


def conocimientos(con):
    out = {}

    # --- 1.1 periodos equivalentes
    rows, sql = m.group(con, ["bloque"], ["pct_neg", "insolventes", "base_pat"], None, want_sql=True)
    d = {r[0]: r[1:] for r in rows}
    pre, pan = d["2018–2019"], d["2020–2021"]
    z = _z(pre[0] / 100, pre[2], pan[0] / 100, pan[2], pre[1], pan[1])
    concl = ("la diferencia no es estadísticamente distinguible" if abs(z) < 1.96 else "la diferencia es estadísticamente distinguible")
    k11 = {
        "vista": 1, "titulo": "El cambio entre periodos equivalentes es pequeño",
        "pregunta": "¿Cambió el porcentaje de registros con patrimonio negativo entre 2018–2019 y 2020–2021?",
        "dimensiones": "Tiempo (Año → Bloque de 2 años) · medida: % con patrimonio negativo (registros con patrimonio negativo / registros con patrimonio conocido).",
        "procedimiento": "Vista 1 con nivel de tiempo = Bloque de 2 años, sin filtros de periodo ni segmento; la columna Total de la matriz da el resultado del bloque, calculado con su propio denominador.",
        "evidencia": "Indicador «Variación entre periodos equivalentes» y matriz de la vista 1; consulta SQL abajo.",
        "hallazgo": (f"{pct(pre[0], 2)} ({n0(pre[1])} de {n0(pre[2])} registros) en 2018–2019 y {pct(pan[0], 2)} ({n0(pan[1])} de {n0(pan[2])}) en 2020–2021: "
                     f"{pp(pan[0] - pre[0])} Con una prueba de dos proporciones, z = {n2(abs(z))}: {concl} (cifra orientativa)."),
        "interpretacion": ("La etapa 4 no separaba periodos equivalentes. Con bloques de la misma duración y el denominador correcto, el cambio es menor a un punto porcentual: "
                           "no hay evidencia sólida de que la pandemia haya aumentado ni reducido el patrimonio negativo en esta muestra."),
        "utilidad": "Evita presentar como deterioro o mejoría un cambio que los datos no sostienen y orienta el esfuerzo a completar el patrimonio vacío.",
        "limitacion": "Solo dos años por bloque, cerca del 63 % del patrimonio vacío, datos de una muestra y registros de una misma empresa que se repiten (la prueba supone independencia).",
        "sql": sql, "params": {"nivel_tiempo": "bloque", "nivel_tamano": "segmento"},
    }

    # --- 1.2 por segmento
    rows, sql = m.group(con, ["segmento", "bloque"], ["pct_neg", "insolventes", "base_pat"], None, want_sql=True)
    ds = {(r[0], r[1]): r[2:] for r in rows}
    partes = []
    for s in ("Sin clasificar", "Mipyme", "Gran empresa"):
        a_, b_ = ds[(s, "2018–2019")], ds[(s, "2020–2021")]
        partes.append((s, a_, b_))
    sc = partes[0]
    base_sc = (sc[1][2] + sc[2][2]) / (pre[2] + pan[2]) * 100
    txt = "; ".join(f"{s}: {pct(a_[0], 2)} ({n0(a_[1])}/{n0(a_[2])}) → {pct(b_[0], 2)} ({n0(b_[1])}/{n0(b_[2])})" for s, a_, b_ in partes)
    bajo_sc = sc[2][0] < sc[1][0]
    suben = [s for s, a_, b_ in partes[1:] if b_[0] > a_[0]]
    k12 = {
        "vista": 1, "titulo": "El resultado global esconde movimientos distintos por segmento",
        "pregunta": "¿El cambio entre periodos equivalentes es igual en todos los segmentos de tamaño?",
        "dimensiones": "Tiempo (Bloque de 2 años) × Tamaño (Segmento) · medida: % con patrimonio negativo, con la base (n) de cada celda.",
        "procedimiento": "Vista 1 con nivel de tiempo = Bloque de 2 años y nivel de tamaño = Segmento (drill-down desde Periodo y Tamaño→Segmento), sin filtros; medida de la matriz alternada entre % y conteos.",
        "evidencia": "Matriz de la vista 1 en las tres medidas (porcentaje, conteo de insolventes y base); consulta SQL abajo.",
        "hallazgo": f"Insolventes / base por bloque (2018–2019 → 2020–2021). {txt}. El grupo «Sin clasificar» aporta el {pct(base_sc)} de la base de los dos bloques.",
        "interpretacion": (("El descenso del total viene de «Sin clasificar», que pesa casi toda la base; " if bajo_sc else "")
                           + (f"en {', '.join(suben)} el porcentaje subió" if suben else "en los segmentos clasificados no subió")
                           + ", pero con muy pocos casos (de 1 a 9 empresas-año). Se trata de una hipótesis para validar, no de un hallazgo firme."),
        "utilidad": "Indica dónde conviene completar información (clasificar el tamaño) y qué segmentos vigilar antes de decidir.",
        "limitacion": "Celdas con 56 a 321 registros de base y 1 a 9 casos: un solo registro cambia el porcentaje de forma visible. No se puede afirmar una diferencia entre segmentos.",
        "sql": sql, "params": {"nivel_tiempo": "bloque", "nivel_tamano": "segmento"},
    }
    out[1] = [k11, k12]

    # --- 2.1 agregada vs promedio simple
    rows, sql = m.group(con, ["tamano"], ["razon_agr", "razon_prom", "con_razon"], None, want_sql=True)
    dz = {r[0]: r[1:] for r in rows}
    lista = "; ".join(f"{t}: {n2(dz[t][0])} / {n2(dz[t][1])} (n={n0(dz[t][2])})" for t in m.TAMANOS if t in dz and dz[t][2])
    cand = [(t, dz[t][0] - dz[t][1]) for t in dz if dz[t][2] >= 100]
    tmax = max(cand, key=lambda x: abs(x[1]))
    mayor = tmax[1] > 0
    k21 = {
        "vista": 2, "titulo": "Agregar o promediar la razón cambia la lectura del endeudamiento",
        "pregunta": "¿Cambia la conclusión sobre el endeudamiento si se usa la razón agregada o el promedio simple de razones?",
        "dimensiones": "Tamaño (nivel Tamaño) · medidas: razón agregada (Σ pasivos / Σ activos) y promedio simple de la razón de cada registro.",
        "procedimiento": "Vista 2 con nivel de tamaño = Tamaño (drill-down desde Segmento), sin filtros; se compara en la gráfica «agregada frente a promedio simple».",
        "evidencia": "Segunda gráfica de la vista 2 y su tabla de datos; consulta SQL abajo.",
        "hallazgo": f"Razón agregada / promedio simple por tamaño: {lista}.",
        "interpretacion": (f"En {tmax[0]} la razón agregada ({n2(dz[tmax[0]][0])}) queda {'por encima' if mayor else 'por debajo'} del promedio simple ({n2(dz[tmax[0]][1])}): "
                           f"las empresas con más activos tienden a tener {'mayor' if mayor else 'menor'} endeudamiento que la empresa típica de ese grupo. "
                           "La etapa 4 usaba promedios, que no capturan este efecto de escala."),
        "utilidad": "Usar la razón agregada para medir la exposición total de un grupo y el promedio simple (o la mediana) para describir a la empresa típica.",
        "limitacion": "La razón existe solo en los registros con activo y pasivo (n pequeño, y muy pequeño en Micro); los valores extremos pesan en el promedio simple.",
        "sql": sql, "params": {"nivel_tamano": "tamano"},
    }

    # --- 2.2 bandas por segmento e información faltante
    rows, sql = m.group(con, ["segmento", "grupo"], ["registros"], None, want_sql=True)
    dg = {(r[0], r[1]): r[2] for r in rows}

    def alto(s):
        mo, al = dg.get((s, "Moderado"), 0), dg.get((s, "Alto"), 0)
        return al / (mo + al) * 100 if mo + al else None, mo + al

    def sin(s):
        tot_s = sum(v for (a_, _), v in dg.items() if a_ == s)
        return dg.get((s, "Sin información"), 0) / tot_s * 100, tot_s
    am, ag = alto("Mipyme"), alto("Gran empresa")
    similar = abs(am[0] - ag[0]) < 3
    k22 = {
        "vista": 2, "titulo": "El perfil de deuda es parecido entre segmentos; lo que falta es información",
        "pregunta": "¿En qué bandas de endeudamiento se concentran Mipyme y Gran empresa, y qué parte de los registros no permite saberlo?",
        "dimensiones": "Tamaño (Segmento) × Condición financiera (Grupo de endeudamiento) · medida: registros (conteo y % de la fila).",
        "procedimiento": "Vista 2 con nivel de tamaño = Segmento, sin filtros; matriz con medida «% de la fila» (denominador: registros de cada segmento) y la columna «Sin información».",
        "evidencia": "Matriz y primera gráfica de la vista 2; consulta SQL abajo.",
        "hallazgo": (f"Endeudamiento alto (razón > 0,60) entre los registros con razón conocida: Mipyme {pct(am[0])} ({n0(am[1])} registros) y Gran empresa {pct(ag[0])} ({n0(ag[1])} registros). "
                     f"Sin razón conocida: Mipyme {pct(sin('Mipyme')[0])}, Gran empresa {pct(sin('Gran empresa')[0])} y Sin clasificar {pct(sin('Sin clasificar')[0])}."),
        "interpretacion": (("La diferencia entre segmentos es menor a tres puntos porcentuales: " if similar else "Los segmentos muestran perfiles de deuda distintos: ")
                           + "en esta muestra, el tamaño clasificado por sí solo separa poco el perfil de deuda, y la limitación principal es que alrededor de nueve de cada diez registros "
                             "(incluso entre empresas con tamaño asignado) no tienen pasivo. La etapa 4 no medía esa información faltante."),
        "utilidad": "Prioriza completar el pasivo antes de diseñar umbrales o políticas de endeudamiento por tamaño.",
        "limitacion": "La clasificación de tamaño depende del activo y es parte del mismo problema de datos faltantes; las bandas son una definición del equipo.",
        "sql": sql, "params": {"nivel_tamano": "segmento", "medida": "pct_fila"},
    }
    out[2] = [k21, k22]

    # --- 3.1 años observados y patrimonio negativo (ventana comparable)
    f3 = {"cohorte": "ventana"}
    rows, sql = m.group(con, ["anos_obs_grupo"], ["pct_neg", "insolventes", "base_pat"], f3, want_sql=True)
    d3 = {r[0]: r[1:] for r in rows}
    seq = [d3[k][0] for k in ("1", "2", "3 o más")]
    dec = seq[0] > seq[1] > seq[2]
    txt3 = "; ".join(f"{k}: {pct(d3[k][0], 2)} ({n0(d3[k][1])} de {n0(d3[k][2])})" for k in ("1", "2", "3 o más"))
    k31 = {
        "vista": 3, "titulo": "Las empresas observadas más años tienen menos patrimonio negativo",
        "pregunta": "Entre empresas que ingresaron en 2016–2018, ¿cambia el % con patrimonio negativo según los años que aparecen en el modelo?",
        "dimensiones": "Empresa (Años observados → Grupo; Cohorte de ingreso) × Condición financiera · medida: % con patrimonio negativo.",
        "procedimiento": "Vista 3 con filtro de cohorte = Ventana comparable 2016–2018 (slice sobre Empresa) y nivel de años observados = Grupo; denominador: registros con patrimonio conocido.",
        "evidencia": "Indicadores y primera gráfica de la vista 3; consulta SQL abajo.",
        "hallazgo": f"% con patrimonio negativo según años observados (1, 2, 3 o más): {txt3}.",
        "interpretacion": (("El porcentaje disminuye a medida que aumentan los años observados. " if dec else "El porcentaje no disminuye de forma continua con los años observados. ")
                           + "Es una asociación: puede reflejar que las empresas con patrimonio negativo dejan de aparecer (hipótesis sin comprobar) "
                             "y no que observarse más años cause mayor solvencia."),
        "utilidad": "Sugiere usar los años observados como variable de seguimiento para el modelo predictivo, junto con el tamaño.",
        "limitacion": "Aparecer pocos años puede deberse al muestreo y no a un cierre; los datos son una muestra y el patrimonio está vacío en cerca del 60 % de los registros de esta ventana.",
        "sql": sql, "params": {"cohorte": "ventana"},
    }

    # --- 3.2 activo mediano por años observados
    md = m.media_activo(con, "anos_obs_grupo", f3)
    sql32 = ("SELECT " + m.DIMS["anos_obs_grupo"][0] + " AS anos_obs, f.Activo_Total\n" + m.FROM +
             "\nWHERE e.Primer_Ano_Observado BETWEEN 2016 AND 2018 AND f.Activo_Total IS NOT NULL\n"
             "-- la mediana de cada grupo se calcula en Python (SQLite no trae función MEDIAN)")
    txt32 = "; ".join(f"{k}: {n0(md[k][0])} (n={n0(md[k][1])})" for k in ("1", "2", "3 o más"))
    crece = md["1"][0] < md["3 o más"][0]
    k32 = {
        "vista": 3, "titulo": "Las empresas que aparecen más años son, en mediana, más grandes",
        "pregunta": "En la misma ventana de ingreso, ¿las empresas observadas más años tienen mayor activo?",
        "dimensiones": "Empresa (Años observados → Grupo) × medida activo mediano (Tamaño como atributo de contexto).",
        "procedimiento": "Vista 3 con filtro de cohorte = Ventana comparable 2016–2018 y nivel de años observados = Grupo; se usa la mediana del activo total de los registros con activo.",
        "evidencia": "Segunda gráfica de la vista 3 y su tabla de datos; consulta SQL abajo.",
        "hallazgo": f"Activo mediano (unidades de la fuente) según años observados (1, 2, 3 o más): {txt32}.",
        "interpretacion": (("El activo mediano es mayor en las empresas observadas más años. " if crece else "El activo mediano no crece con los años observados. ")
                           + "Por eso parte de la menor insolvencia del conocimiento 3.1 podría deberse al tamaño y no a los años observados; "
                             "es una hipótesis que requiere comparar dentro de cada tamaño."),
        "utilidad": "Obliga a controlar por tamaño cuando se perfile la permanencia de las empresas.",
        "limitacion": "El activo solo se conoce en cerca del 38 % de los registros; la mediana resiste valores extremos, pero no corrige el sesgo de qué empresas reportan activo.",
        "sql": sql32, "params": {"cohorte": "ventana"},
    }
    out[3] = [k31, k32]

    # --- 4.1 reaparición al año siguiente
    rows, sql = m.group(con, ["cohorte", "ano"], ["empresas"], None, want_sql=True)
    cy = {(int(r[0]), int(r[1])): r[2] for r in rows}
    tam = {int(r[0]): r[1] for r in m.group(con, ["cohorte"], ["empresas"])}
    rea = {c: (cy.get((c, c + 1), 0), tam[c]) for c in (2018, 2019, 2020)}
    txt41 = "; ".join(f"{c}→{c + 1}: {pct(v[0] / v[1] * 100)} ({n0(v[0])} de {n0(v[1])})" for c, v in rea.items())
    desc = rea[2018][0] / rea[2018][1] > rea[2019][0] / rea[2019][1] > rea[2020][0] / rea[2020][1]
    k41 = {
        "vista": 4, "titulo": "La reaparición al año siguiente baja en las cohortes más recientes",
        "pregunta": "¿Qué porcentaje de las empresas de cada cohorte reaparece al año siguiente, con la misma ventana de observación?",
        "dimensiones": "Empresa (Cohorte de ingreso) × Tiempo (Año) · medida: empresas distintas y reaparición (empresas del año / empresas de la cohorte).",
        "procedimiento": "Vista 4 con nivel de cohorte = Año de ingreso, nivel de tiempo = Año y medida = % de reaparición; se lee la celda del año de ingreso + 1 de cada cohorte (ventanas de un año completas: 2018→2019 a 2020→2021).",
        "evidencia": "Matriz cohorte × año y segunda gráfica de la vista 4; consulta SQL abajo.",
        "hallazgo": f"Reaparición al año siguiente: {txt41}.",
        "interpretacion": (("El porcentaje desciende de una cohorte a la siguiente. " if desc else "El porcentaje no desciende de forma continua. ")
                           + "Con ventanas iguales, las cohortes recientes reaparecen menos en esta muestra; no puede afirmarse que esas empresas hayan cerrado, "
                             "pues la muestra y la carga de datos también explican ausencias (hipótesis)."),
        "utilidad": "Da una referencia comparable de continuidad en la muestra y muestra qué ventanas son válidas para medir permanencia.",
        "limitacion": "Reaparecer en la muestra no equivale a sobrevivir, y la matriz no distingue entre cierre, no reporte y muestreo.",
        "sql": sql, "params": {"nivel_cohorte": "cohorte", "nivel_tiempo": "ano", "medida": "reaparicion"},
    }

    # --- 4.2 hueco 2017
    r17, r18 = m.cobertura_2017(con), m.uno(con, ["registros"], None, ["t.Ano = 2018"])[0]
    n2016 = tam[2016]
    p17, p18 = cy.get((2016, 2017), 0), cy.get((2016, 2018), 0)
    k42 = {
        "vista": 4, "titulo": "El año 2017 es un hueco de datos que distorsiona la permanencia",
        "pregunta": "¿Por qué la cohorte 2016 casi no reaparece al año siguiente pero sí dos años después?",
        "dimensiones": "Empresa (Cohorte 2016) × Tiempo (Año) · medida: empresas distintas y reaparición.",
        "procedimiento": "Vista 4 con nivel de cohorte = Año de ingreso, nivel de tiempo = Año y medida = % de reaparición; se compara la fila de la cohorte 2016 en 2017 y 2018.",
        "evidencia": "Fila 2016 de la matriz de la vista 4 y nota de la segunda gráfica; consulta SQL abajo.",
        "hallazgo": (f"El modelo tiene {n0(r17)} registros en 2017 frente a {n0(r18)} en 2018. De {n0(n2016)} empresas de la cohorte 2016, "
                     f"{n0(p17)} aparecen en 2017 ({pct(p17 / n2016 * 100)}) y {n0(p18)} en 2018 ({pct(p18 / n2016 * 100)})."),
        "interpretacion": ("La caída a casi cero en 2017 es incompatible con un patrón real de cierres, porque las empresas reaparecen en 2018. "
                           "Apunta a que el año 2017 quedó casi sin datos en la extracción de la muestra (hipótesis a confirmar con el origen). "
                           "Este hallazgo no existía en la etapa 4, que trataba cada año por separado."),
        "utilidad": "Obliga a excluir 2017 o tratar 2016→2018 como un salto de dos años al medir permanencia, y justifica pedir la serie completa al origen.",
        "limitacion": "No se conoce la causa del hueco; solo se observa que el año tiene muy pocos registros.",
        "sql": sql, "params": {"nivel_cohorte": "cohorte", "nivel_tiempo": "ano", "medida": "reaparicion"},
    }
    out[4] = [k41, k42]
    return out


def resumen(con):
    r = m.uno(con, ["registros", "empresas", "base_pat", "con_razon"])
    anos = con.execute("SELECT MIN(Ano), MAX(Ano) FROM Dim_Tiempo").fetchone()
    return {"registros": n0(r[0]), "empresas": n0(r[1]), "pat": pct(r[2] / r[0] * 100), "razon": n0(r[3]),
            "razon_pct": pct(r[3] / r[0] * 100), "ano_min": anos[0], "ano_max": anos[1]}


# ---------------------------------------------------------------------------
# Ejemplos de las cinco operaciones y validaciones del modelo (página general)
# ---------------------------------------------------------------------------
def ejemplos(con):
    ms = ["pct_neg", "insolventes", "base_pat"]
    per = {r[0]: r[1:] for r in m.group(con, ["periodo"], ms)}
    txt_per = "; ".join(f"{p}: {pct(per[p][0], 2)} (n={n0(per[p][2])})" for p in m.PERIODOS if p in per)
    ano = {r[0]: r[1:] for r in m.group(con, ["ano"], ms)}
    txt_ano = "; ".join(f"{a}: {pct(ano[a][0], 2)} (n={n0(ano[a][2])})" for a in ("2018", "2019", "2020", "2021") if a in ano)
    c18 = {r[0]: r[1:] for r in m.group(con, ["anos_obs_grupo"], ms, {"cohorte": "2018"})}
    txt_c18 = "; ".join(f"{k}: {pct(c18[k][0], 2)} (n={n0(c18[k][2])})" for k in ("1", "2", "3 o más") if k in c18)
    dice = m.uno(con, ms, {"periodo": "Pandemia (2020-2021)", "segmento": "Mipyme"})
    cy = {(int(r[0]), int(r[1])): r[2] for r in m.group(con, ["cohorte", "ano"], ["empresas"])}
    tam = {int(r[0]): r[1] for r in m.group(con, ["cohorte"], ["empresas"])}
    txt_piv = "; ".join(f"cohorte {c}: {pct(cy.get((c, 2019), 0) / tam[c] * 100)}" for c in (2016, 2018))
    return [
        {"op": "Roll-up", "vista": 1, "params": {"nivel_tiempo": "periodo"},
         "dims": "Tiempo (Año → Periodo) · medida % con patrimonio negativo",
         "como": "Vista 1, nivel de tiempo = Periodo (nivel alto). Los años se agrupan y el porcentaje se recalcula con la base del periodo, sin promediar porcentajes anuales.",
         "resultado": txt_per + ".",
         "lectura": "Al subir de nivel, el periodo Posterior queda con una base muy pequeña: el porcentaje más alto es también el menos confiable."},
        {"op": "Drill-down", "vista": 1, "params": {"nivel_tiempo": "ano"},
         "dims": "Tiempo (Periodo → Año) · medida % con patrimonio negativo",
         "como": "Vista 1, nivel de tiempo = Año (nivel detallado): cada año recalcula su propio porcentaje y su base.",
         "resultado": txt_ano + ".",
         "lectura": "El detalle por año permite ver que el cambio entre 2018–2019 y 2020–2021 es pequeño y no una tendencia clara."},
        {"op": "Slice", "vista": 3, "params": {"cohorte": "2018"},
         "dims": "Empresa (Cohorte de ingreso = 2018) × Condición financiera · medida % con patrimonio negativo",
         "como": "Vista 3, filtro de cohorte = 2018: se selecciona un único valor de la dimensión Empresa y se estudia ese subconjunto.",
         "resultado": txt_c18 + ".",
         "lectura": "Dentro de una sola cohorte también se observa la asociación entre años observados y patrimonio negativo."},
        {"op": "Dice", "vista": 1, "params": {"periodo": "Pandemia (2020-2021)", "segmento": "Mipyme"},
         "dims": "Tiempo (Periodo = Pandemia) y Tamaño (Segmento = Mipyme) · medida % con patrimonio negativo",
         "como": "Vista 1 con dos filtros a la vez: periodo = Pandemia (2020-2021) y segmento = Mipyme.",
         "resultado": f"{pct(dice[0], 2)} ({n0(dice[1])} de {n0(dice[2])} registros con patrimonio conocido).",
         "lectura": "La combinación de filtros aísla las Mipymes durante la pandemia; con una base de pocos cientos de registros, el porcentaje es orientativo."},
        {"op": "Pivot", "vista": 4, "params": {"pivot": "1", "medida": "reaparicion"},
         "dims": "Empresa (Cohorte) × Tiempo (Año) · medida % de reaparición",
         "como": "Vista 4 con medida = % de reaparición y pivot activado: los años pasan a las filas y las cohortes a las columnas.",
         "resultado": "Presencia en 2019 de cada cohorte: " + txt_piv + ".",
         "lectura": "La misma matriz, leída por años, responde otra pregunta: qué cohortes dominan cada año."},
    ]


def validaciones(con):
    r = m.uno(con, ["registros", "empresas", "insolventes"])
    act = con.execute("SELECT SUM(Activo_Total) FROM Fact_Estado_Financiero").fetchone()[0]
    nemp = con.execute("SELECT COUNT(*) FROM Dim_Empresa").fetchone()[0]
    dup = con.execute("SELECT COUNT(*) FROM (SELECT Empresa_Key, Fecha_Corte FROM Fact_Estado_Financiero "
                      "GROUP BY 1, 2 HAVING COUNT(*) > 1)").fetchone()[0]
    huerf = con.execute("PRAGMA foreign_key_check").fetchall()
    sin_pat = con.execute("SELECT COUNT(*) FROM Fact_Estado_Financiero WHERE Patrimonio_Total IS NULL AND Insolvente IS NOT NULL").fetchone()[0]
    filas = [
        ("Filas de la tabla de hechos = registros de Datos_Tratados", "25.164", n0(r[0]), n0(r[0]) == "25.164"),
        ("Empresas distintas (NIT) = filas de Dim_Empresa", "18.652", n0(nemp), n0(nemp) == "18.652" and r[1] == nemp),
        ("Registros con patrimonio negativo = «Sí» de Insolvencia_Tecnica", "335", n0(r[2]), int(r[2]) == 335),
        ("Suma de Activo_Total", "570.991.663.932,36", _fmt2(act), _fmt2(act) == "570.991.663.932,36"),
    ]
    extra = [
        ("Combinaciones (empresa, fecha de corte) repetidas en la tabla de hechos", "0", n0(dup), dup == 0),
        ("Claves foráneas sin registro relacionado", "0", n0(len(huerf)), len(huerf) == 0),
        ("Insolvente con patrimonio vacío (incoherencias)", "0", n0(sin_pat), sin_pat == 0),
    ]
    return filas, extra


def _fmt2(x):
    return m._fmt(x, 2)
