# CommuteOS - Smart Commuting System Backend

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)
![License](https://img.shields.io/badge/license-MIT-green)

Production-grade backend foundation for an intelligent urban commuting system. Built with clean architecture principles, microservices separation, and low-latency design.

## 🏗️ Architecture Overview

CommuteOS follows a microservices architecture with clear separation of concerns:

```
┌─────────────────┐
│   API Gateway   │ ← Public Entry Point (Port 8000)
│   (FastAPI)     │
└────────┬────────┘
         │
    ┌────┴────────────────┬─────────────┐
    │                     │             │
    ▼                     ▼             ▼
┌────────┐         ┌──────────┐   ┌─────────┐
│ Redis  │         │ Routing  │   │ PostgreSQL
│ Cache  │         │ Service  │   │ Database│
└────────┘         └──────────┘   └─────────┘
```

### Services

- **API Gateway**: Main entry point with caching, request routing, and monitoring
- **Routing Service**: Graph-based route computation using NetworkX and Dijkstra's algorithm
- **Data Ingestion**: Background service for loading and seeding transit data
- **ML Service**: Placeholder for future machine learning models
- **Digital Twin**: Placeholder for simulation capabilities

### Shared Components

- **Config**: Environment-based settings management
- **Database**: Async SQLAlchemy with connection pooling
- **Cache**: Async Redis with connection pooling
- **Utils**: Structured logging and utilities
- **Schemas**: Pydantic models for validation

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)
- PostgreSQL 15+ (if running without Docker)
- Redis 7+ (if running without Docker)

### Running with Docker (Recommended)

1. **Clone and navigate to the project:**
```bash
cd "commute os"
```

2. **Create environment file:**
```bash
copy .env.example .env
```

3. **Start all services:**
```bash
docker-compose up -d
```

4. **Check service health:**
```bash
curl http://localhost:8000/health
```

5. **Test the routing API:**
```bash
curl -X POST http://localhost:8000/api/v1/route \
  -H "Content-Type: application/json" \
  -d "{\"source\": \"Station_A\", \"destination\": \"Station_B\"}"
```

### Running Locally (Development)

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables:**
```bash
# Create .env file with local settings
copy .env.example .env
# Update DB_HOST=localhost, REDIS_HOST=localhost, etc.
```

3. **Start PostgreSQL and Redis:**
```bash
# Using Docker for databases only
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:15-alpine
docker run -d -p 6379:6379 redis:7-alpine
```

4. **Run data ingestion:**
```bash
python -m commuteos.services.data_ingestion.main
```

5. **Start services:**
```bash
# Terminal 1 - Routing Service
python -m uvicorn commuteos.services.routing_service.main:app --port 8001

# Terminal 2 - API Gateway
python -m uvicorn commuteos.services.api_gateway.main:app --port 8000
```

## 📡 API Endpoints

### API Gateway (Port 8000)

#### Health Check
```http
GET /health
```

#### Get Route
```http
POST /api/v1/route
Content-Type: application/json

{
  "source": "Station_A",
  "destination": "Station_B"
}
```

**Response:**
```json
{
  "path": ["Station_A", "Station_C", "Station_B"],
  "estimated_time": 27.0,
  "distance": 5.6,
  "base_score": 0.645,
  "cached": false
}
```

#### Clear Cache
```http
DELETE /api/v1/cache
```

#### Get Statistics
```http
GET /api/v1/stats
```

**Response:**
```json
{
  "total_queries": 150,
  "cache_hits": 95,
  "cache_hit_rate": 63.33,
  "avg_response_time_ms": 12.45
}
```

### Routing Service (Port 8001)

#### Compute Route
```http
POST /compute
Content-Type: application/json

{
  "source": "Station_A",
  "destination": "Station_B"
}
```

#### Get Station Info
```http
GET /station/{station_id}
```

## 🗄️ Database Schema

### Stations Table
- `id`: Primary key
- `station_id`: Unique station identifier
- `name`: Station name
- `latitude`, `longitude`: GPS coordinates
- `station_type`: Type (metro, bus, train)
- `metadata`: JSON metadata
- `created_at`, `updated_at`: Timestamps

### Edges Table
- `id`: Primary key
- `edge_id`: Unique edge identifier
- `source_station`, `target_station`: Station connections
- `distance`: Distance in kilometers
- `travel_time`: Time in minutes
- `transport_type`: Transport mode
- `metadata`: JSON metadata
- `created_at`, `updated_at`: Timestamps

### Routes History Table
- `id`: Primary key
- `source_station`, `target_station`: Query endpoints
- `route_path`: JSON array of station IDs
- `total_time`, `total_distance`: Route metrics
- `score`: Routing score
- `cache_hit`: Boolean indicator
- `response_time_ms`: Request latency
- `timestamp`: Query time

## 🔧 Configuration

All configuration is managed via environment variables. See [.env.example](.env.example) for all available options.

Key configurations:

| Variable | Default | Description |
|----------|---------|-------------|
| `API_PORT` | 8000 | API Gateway port |
| `DB_HOST` | postgres | PostgreSQL host |
| `REDIS_HOST` | redis | Redis host |
| `CACHE_TTL` | 600 | Cache TTL in seconds |
| `LOG_LEVEL` | INFO | Logging level |
| `DB_POOL_SIZE` | 20 | Database connection pool size |

## 📊 Performance Features

### Async-First Design
- All I/O operations are async
- Non-blocking database queries
- Async Redis operations
- Concurrent request handling

### Connection Pooling
- Database connection pooling (20 connections, 10 overflow)
- Redis connection pooling (10 connections)
- Connection lifecycle management

### Caching Strategy
- Redis-based route caching
- Configurable TTL (default 600s)
- Cache-first lookup pattern
- Automatic cache warming

### Monitoring & Logging
- Structured JSON logging
- Request/response timing
- Cache hit/miss tracking
- Error tracking and reporting

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=commuteos --cov-report=html

# Run specific test file
pytest tests/test_routing.py
```

## 📦 Project Structure

```
commuteos/
├── services/
│   ├── api_gateway/          # Main API gateway
│   │   └── main.py
│   ├── routing_service/      # Routing computation
│   │   ├── main.py
│   │   ├── routing_engine.py
│   │   └── data/
│   │       └── mock_city_graph.json
│   ├── data_ingestion/       # Database seeding
│   │   └── main.py
│   ├── ml_service/           # Placeholder for ML
│   └── digital_twin/         # Placeholder for simulation
│
├── shared/
│   ├── config/               # Configuration management
│   │   └── settings.py
│   ├── database/             # Database layer
│   │   ├── connection.py
│   │   └── models.py
│   ├── cache/                # Redis caching
│   │   └── redis_cache.py
│   ├── utils/                # Utilities
│   │   └── logger.py
│   └── schemas/              # Pydantic schemas
│       └── route_schemas.py
│
├── models/                   # Placeholder for ML models
├── tests/                    # Test suite
├── docker/                   # Docker configurations
├── docker-compose.yml        # Service orchestration
├── Dockerfile                # API Gateway image
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🔒 Security Considerations

For production deployment:

1. **Change default credentials** in `.env`
2. **Enable HTTPS** with SSL certificates
3. **Configure CORS** appropriately
4. **Set up authentication** (JWT, OAuth2)
5. **Enable rate limiting**
6. **Use secrets management** (Vault, AWS Secrets Manager)
7. **Configure firewall rules**
8. **Enable audit logging**

## 🚧 Future Enhancements

- [ ] Machine learning-based route scoring
- [ ] Real-time traffic integration
- [ ] Digital twin simulation
- [ ] Multi-modal transport support
- [ ] User preferences and personalization
- [ ] Predictive analytics
- [ ] GraphQL API option
- [ ] Authentication & authorization
- [ ] Rate limiting
- [ ] API versioning

## 📈 Monitoring & Observability

### Health Checks
All services expose `/health` endpoints for monitoring:
- API Gateway: `http://localhost:8000/health`
- Routing Service: `http://localhost:8001/health`

### Metrics
The API Gateway provides statistics endpoint:
```bash
curl http://localhost:8000/api/v1/stats
```

### Logs
Structured JSON logs are written to stdout:
```bash
# View API Gateway logs
docker logs -f commuteos_api

# View Routing Service logs
docker logs -f commuteos_routing
```

## 🛠️ Development

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for all public functions
- Keep functions focused and small

### Adding a New Service
1. Create service directory in `services/`
2. Implement FastAPI app with lifespan events
3. Add health check endpoint
4. Update docker-compose.yml
5. Create Dockerfile if needed
6. Document API endpoints

## 📄 License

MIT License - See LICENSE file for details

## 👥 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Built with ❤️ for smarter urban commuting**
