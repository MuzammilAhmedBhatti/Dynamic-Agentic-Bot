# Docker development boundary

Phase 1 uses the root `compose.yaml` only for PostgreSQL. Backend and frontend run directly through `uv` and Node.js for a fast development loop. Pinecone, GCP emulators, Redis, queues, and AI services are intentionally absent until their approved phases.
