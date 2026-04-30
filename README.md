# Multi-Platform Video Downloader Bot

Bot profissional do Telegram para download de vídeos. Arquitetado para suportar múltiplas plataformas via sistema de plugins.

## Arquitetura

- **Plugin system**: `BaseExtractor` + `ExtractorRegistry` permitem adicionar novas plataformas (YouTube, Instagram, X, etc.) sem tocar no restante do código.
- **Async queue**: `DownloadOrchestrator` gerencia fila de downloads com semáforo de concorrência.
- **Typed domain**: `DownloadJob`, `DownloadSuccess`, `DownloadError` garantem contratos claros.
- **Config**: `pydantic-settings` carrega variáveis de ambiente com validação.

## Estrutura

```
src/
├── bot/           # Handlers e aplicação Telegram
├── config/        # Settings (Pydantic)
├── core/          # Domain: job, result, orchestrator
├── downloaders/   # Extractors e registry
└── utils/         # Logging, URL parsing
```

## Setup

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copie `.env.example` para `.env` e preencha `TELEGRAM_BOT_TOKEN`.

## Executar

```powershell
python -m src.main
```

## Adicionar um novo extractor

1. Crie uma classe herdando `BaseExtractor` em `src/downloaders/extractors/`.
2. Defina `DOMAINS = {"site.com"}`.
3. Implemente `async def extract(self, job: DownloadJob) -> DownloadResult`.
4. Registre-o em `src/bot/application.py` com `registry.register(MeuExtractor)`.

## Testes

```powershell
pytest tests/ -v
```
