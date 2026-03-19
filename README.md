# Briefing Matutino — Gerencia de Personas Oxiquim

Portal de noticias diario generado automáticamente con IA. Se publica cada mañana de lunes a viernes a las 07:00 hora Chile vía GitHub Actions + GitHub Pages.

---

## Setup — paso a paso

### 1. Subir estos archivos al repositorio

Sube el contenido de este ZIP al repositorio `oxiquim-briefing-portal` en GitHub (el mismo donde activaste GitHub Pages).

Estructura esperada:
```
oxiquim-briefing-portal/
├── .github/
│   └── workflows/
│       └── briefing.yml
├── scripts/
│   └── generate_briefing.py
├── index.html              ← se genera automáticamente cada día
└── README.md
```

### 2. Agregar el secret ANTHROPIC_API_KEY

En el repositorio: **Settings → Secrets and variables → Actions → New repository secret**

| Nombre | Valor |
|--------|-------|
| `ANTHROPIC_API_KEY` | Tu API key de Anthropic (empieza con `sk-ant-...`) |

### 3. Probar manualmente

En el repositorio: **Actions → Briefing Matutino Oxiquim → Run workflow → Run workflow**

Espera 2–3 minutos. El workflow:
1. Busca noticias del día vía Anthropic API + web search
2. Genera `index.html` con las noticias encontradas
3. Hace commit + push al repositorio
4. GitHub Pages redespliega automáticamente

### 4. URL pública

```
https://TU_USUARIO.github.io/oxiquim-briefing-portal/
```

---

## Horario automático

Lunes a viernes a las **07:00 hora Chile** (10:00 UTC).

Para cambiar el horario, edita la línea `cron` en `.github/workflows/briefing.yml`.

---

## Notas

- Solo se incluyen noticias con fecha de publicación del día exacto de ejecución.
- Las secciones sin noticias del día no aparecen en el portal.
- En cada sección nacional, la primera noticia es siempre de fuente chilena.
