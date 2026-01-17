# Wallapop Scraper V2 🔍

[![Docker Tested](https://img.shields.io/badge/Docker-Tested%20%E2%9C%85-success?style=flat-square&logo=docker)](https://github.com/jogarman/wallascrapping_v2)
[![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)](https://www.python.org/)
[![Selenium](https://img.shields.io/badge/Selenium-Automated-green?style=flat-square&logo=selenium)](https://www.selenium.dev/)
[![Apify](https://img.shields.io/badge/Apify-Ready-orange?style=flat-square&logo=apify)](https://apify.com/)

Scraper automatizado para Wallapop con pipeline completo de procesamiento de datos.

## ✨ Características

- 🤖 **Scraping automatizado** con Selenium
- 🐳 **Docker containerizado** para fácil deployment
- 🔄 **Pipeline de 5 pasos** para procesar y filtrar datos
- 🧠 **Enriquecimiento con IA** usando Google Gemini
- ☁️ **Listo para Apify** - Deploy directo a la nube
- 🔍 **Anti-detección** con User-Agent rotación y medidas anti-bot

## 🚀 Quick Start

### Opción 1: Docker (Recomendado)

```bash
# Construir imagen
docker build -t wallascrap:latest .

# Ejecutar
docker run --rm \
  -e GOOGLE_API_KEY="your_api_key" \
  -e SEARCH_TERM="iphone" \
  -e HEADLESS=true \
  -v "$(pwd)/scrapping_outputs:/usr/src/app/scrapping_outputs" \
  -v "$(pwd)/data:/usr/src/app/data" \
  wallascrap:latest
```

### Opción 2: Local con UV

```bash
# Instalar dependencias
uv sync

# Ejecutar
uv run python -m src.main
```

## 📊 Pipeline

El scraper ejecuta 5 pasos automáticamente:

1. **Scraper** → Extrae items de Wallapop
2. **Filtro Inicial** → Filtra por precio y condiciones
3. **Lógica de Negocio** → Aplica blacklist/whitelist
4. **Enriquecimiento Gemini** → Analiza con IA
5. **Finalización** → Genera output final

## 🔧 Configuración

### Variables de Entorno

| Variable | Descripción | Requerido |
|----------|-------------|-----------|
| `GOOGLE_API_KEY` | API key de Google Gemini | ✅ |
| `SEARCH_TERM` | Término de búsqueda | ❌ |
| `HEADLESS` | Modo headless (`true`/`false`) | ❌ |
| `SCROLLS` | Número de scrolls | ❌ |

### Archivos de Configuración

- `config/general_scrap_config.json` - Configuración del scraper
- `input_schema.json` - Schema de inputs para Apify
- `elements_to_scrap.json` - Selectores CSS

## 📦 Output

El scraper genera:

- `scrapping_outputs/orchestrator_*.log` - Logs de ejecución
- `data/step1/raw_*.csv` - Datos crudos scrapeados
- `data/step2_inc/filtered_*.csv` - Items incluidos
- `data/step2_exc/excluded_*.csv` - Items excluidos
- Screenshots de debug en caso de error

## ✅ Testing

**Última prueba:** 17 Enero 2026

```
✅ Imagen Docker construida: 2.51GB
✅ Items scrapeados: 200
✅ Pipeline completado: 5/5 steps
✅ Exit code: 0 (Success)
```

## 🌐 Deploy a Apify

```bash
# Instalar CLI
npm install -g apify-cli

# Login
apify login

# Push
apify push
```

O conecta tu repositorio de GitHub en [Apify Console](https://console.apify.com) para deploys automáticos.

## 📝 Licencia

MIT

## 👤 Autor

[@jogarman](https://github.com/jogarman)
