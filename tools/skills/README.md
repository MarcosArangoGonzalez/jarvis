# JarvisOS Skills

Local skills are executable adapters used by Jarvis Kernel.

- `morning_coffee.py`: daily briefing.
- `chat_ingestor.py`: raw file to wiki Markdown.
- `browser_scraper.js`: browser console scraper for large chats.
- `ingest_server.py`: local HTTP receiver for scraper payloads.
- `sync_watcher.py`: automatic ingest queue watcher; URL `.txt` files use `content_analyzer.py`, while plain files use `chat_ingestor.py`.
- `voice_bridge.py`: local STT/TTS using whisper.cpp and Piper.
- `ci_cd_monitor.py`: CI/CD alert collector.
