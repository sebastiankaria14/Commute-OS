# CommuteOS Architecture

## System Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────┐
│                          Client Layer                              │
│                    (Web/Mobile/API Clients)                        │
└────────────────────────────┬───────────────────────────────────────┘
                             │
                             │ HTTP/HTTPS
                             ▼
┌────────────────────────────────────────────────────────────────────┐
│                        API Gateway (Port 8000)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │   Routing    │  │   Caching    │  │  Monitoring  │            │
│  │   Handler    │  │   Layer      │  │  & Logging   │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
└────────┬───────────────────┬─────────────────┬─────────────────────┘
         │                   │                 │
         │                   │                 │
         ▼                   ▼                 ▼
┌─────────────────┐  ┌──────────────┐  ┌──────────────┐
│ Routing Service │  │    Redis     │  │  PostgreSQL  │
│  (Port 8001)    │  │    Cache     │  │   Database   │
│                 │  │              │  │              │
│ ┌─────────────┐ │  │ • Route     │  │ • Stations   │
│ │  NetworkX   │ │  │   Cache     │  │ • Edges      │
│ │   Graph     │ │  │ • TTL: 600s │  │ • History    │
│ │  Dijkstra   │ │  │ • Pool: 10  │  │ • Pool: 20   │
│ └─────────────┘ │  │             │  │              │
└─────────────────┘  └──────────────┘  └──────────────┘
         │
         │ Loads graph from
         ▼
┌─────────────────────────────┐
│   Data Ingestion Service    │
│                             │
│  • Loads GTFS-like data     │
│  • Seeds database           │
│  • Builds network graph     │
│  • Runs once on startup     │
└─────────────────────────────┘
```

## Request Flow

### Route Query Flow

1. **Client Request** → POST /api/v1/route
   ```json
   {
     "source": "Station_A",
     "destination": "Station_B"
   }
   ```

2. **API Gateway** receives request
   - Generates cache key: `route:Station_A:Station_B`
   - Checks Redis cache

3. **Cache Hit** (Best case: ~5-15ms)
   ```
   Redis → API Gateway → Client
   ```

4. **Cache Miss** (Normal case: ~50-100ms)
   ```
   API Gateway → Routing Service
   Routing Service computes route using Dijkstra
   Result → Redis (cached for 10 min)
   Result → PostgreSQL (for history/analytics)
   Result → Client
   ```

5. **Response**
   ```json
   {
     "path": ["Station_A", "Station_C", "Station_B"],
     "estimated_time": 27.0,
     "distance": 5.6,
     "base_score": 0.645,
     "cached": false
   }
   ```

## Data Flow

```
┌───────────────┐
│  Graph JSON   │
│     File      │ (mock_city_graph.json)
└───────┬───────┘
        │
        │ Load at startup
        ▼
┌────────────────────┐
│ Data Ingestion     │
│    Service         │
└───────┬────────────┘
        │
        │ Seed
        ▼
┌────────────────────┐     ┌──────────────────┐
│   PostgreSQL DB    │◄────│  Routing Service │
│                    │     │  (Loads graph)   │
│  • stations        │     └──────────────────┘
│  • edges           │
│  • routes_history  │
└────────────────────┘
```

## Component Responsibilities

### API Gateway
- **Primary Entry Point**: All client requests
- **Caching Logic**: Cache-first lookup pattern
- **Service Orchestration**: Calls routing service
- **Persistence**: Saves query history
- **Monitoring**: Tracks metrics and performance

### Routing Service
- **Graph Management**: Loads and maintains transit network
- **Route Computation**: Dijkstra's shortest path algorithm
- **Scoring**: Basic route quality scoring (placeholder for ML)
- **Station Info**: Provides station metadata

### Data Ingestion
- **One-time Execution**: Runs once on startup
- **Database Seeding**: Populates stations and edges
- **Idempotency**: Safe to run multiple times

### Redis Cache
- **Fast Access**: In-memory cache for routes
- **TTL Management**: Auto-expiry after 10 minutes
- **Connection Pool**: 10 pooled connections
- **LRU Policy**: Max 256MB with eviction

### PostgreSQL Database
- **Persistent Storage**: Stations, edges, history
- **Connection Pool**: 20 connections, 10 overflow
- **Async Operations**: Non-blocking queries
- **Indexing**: Optimized for common queries

## Clean Architecture Layers

```
┌─────────────────────────────────────────────────┐
│           Presentation Layer                    │
│        (FastAPI Routes & Schemas)               │
├─────────────────────────────────────────────────┤
│           Application Layer                     │
│     (Business Logic & Use Cases)                │
├─────────────────────────────────────────────────┤
│           Domain Layer                          │
│   (Models, Entities, Business Rules)            │
├─────────────────────────────────────────────────┤
│          Infrastructure Layer                   │
│  (Database, Cache, External Services)           │
└─────────────────────────────────────────────────┘
```

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Framework | FastAPI | Async web framework |
| Server | Uvicorn | ASGI server |
| Database | PostgreSQL 15 | Persistent storage |
| ORM | SQLAlchemy (async) | Database abstraction |
| Cache | Redis 7 | In-memory cache |
| Graph | NetworkX | Graph algorithms |
| Container | Docker | Containerization |
| Orchestration | Docker Compose | Multi-container apps |
| Config | Pydantic Settings | Environment management |
| Logging | Python logging | Structured logs |

## Scalability Considerations

### Horizontal Scaling
- **API Gateway**: Can scale to N instances behind load balancer
- **Routing Service**: Stateless, can scale horizontally
- **Database**: Read replicas for read-heavy workloads
- **Redis**: Redis Cluster for distributed cache

### Performance Optimization
- **Async I/O**: Non-blocking operations throughout
- **Connection Pooling**: Reuse database/cache connections
- **Caching Strategy**: Reduces backend load by 60%+
- **Indexing**: Database queries optimized with indexes

### Future Enhancements
- **Load Balancer**: Nginx/HAProxy for traffic distribution
- **API Gateway**: Kong/KrakenD for advanced routing
- **Message Queue**: RabbitMQ/Kafka for async processing
- **Service Mesh**: Istio for microservices management

## Security Architecture

```
┌─────────────────────────────────────┐
│      Security Layers (Future)       │
├─────────────────────────────────────┤
│  • API Authentication (JWT/OAuth2)  │
│  • Rate Limiting                    │
│  • Input Validation (Pydantic)      │
│  • SQL Injection Protection (ORM)   │
│  • CORS Configuration               │
│  • HTTPS/TLS                        │
│  • Secrets Management               │
└─────────────────────────────────────┘
```

## Monitoring & Observability

### Current Implementation
- Structured JSON logging
- Health check endpoints
- Request/response timing
- Cache hit/miss tracking
- Query history persistence

### Recommended Additions
- Prometheus metrics export
- Grafana dashboards
- Distributed tracing (Jaeger)
- Error tracking (Sentry)
- APM (Application Performance Monitoring)
