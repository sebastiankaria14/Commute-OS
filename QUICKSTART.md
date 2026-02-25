# CommuteOS - Quick Reference Guide

## 🚀 Quick Start Commands

### Start All Services
```bash
docker-compose up -d
```

### Stop All Services
```bash
docker-compose down
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f routing_service
```

### Restart Services
```bash
docker-compose restart
```

## 📡 API Quick Reference

### Test Route Query
```bash
# Windows (PowerShell)
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/route" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"source":"Station_A","destination":"Station_B"}'

# Windows (curl)
curl -X POST http://localhost:8000/api/v1/route -H "Content-Type: application/json" -d "{\"source\":\"Station_A\",\"destination\":\"Station_B\"}"
```

### Health Checks
```bash
curl http://localhost:8000/health
curl http://localhost:8001/health
```

### Get Statistics
```bash
curl http://localhost:8000/api/v1/stats
```

### Clear Cache
```bash
curl -X DELETE http://localhost:8000/api/v1/cache
```

## 🗺️ Available Stations

- Station_A: Central Station (Metro)
- Station_B: East Terminal (Metro)
- Station_C: North Hub (Bus)
- Station_D: West Plaza (Bus)
- Station_E: South Gateway (Metro)
- Station_F: University Circle (Metro)
- Station_G: Business District (Bus)
- Station_H: Airport Express (Train)

## 🔧 Troubleshooting

### Database Connection Issues
```bash
# Check if PostgreSQL is running
docker ps | findstr postgres

# Connect to database
docker exec -it commuteos_postgres psql -U postgres -d commuteos
```

### Redis Connection Issues
```bash
# Check if Redis is running
docker ps | findstr redis

# Connect to Redis
docker exec -it commuteos_redis redis-cli
```

### View Service Status
```bash
docker-compose ps
```

### Rebuild Services
```bash
docker-compose up -d --build
```

## 📊 Performance Metrics

Expected performance:
- **First request**: ~50-100ms (cache miss)
- **Cached requests**: ~5-15ms (cache hit)
- **Database queries**: ~10-30ms
- **Route computation**: ~20-50ms

## 🔄 Development Workflow

1. Make code changes
2. Rebuild affected service: `docker-compose up -d --build api`
3. Test changes
4. Check logs: `docker-compose logs -f api`

## 📦 Docker Commands

### Remove All Data
```bash
docker-compose down -v
```

### Clean Build
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Access Container Shell
```bash
docker exec -it commuteos_api bash
```

## 🌐 Port Mapping

- **8000**: API Gateway (Main entry point)
- **8001**: Routing Service (Internal)
- **5432**: PostgreSQL Database
- **6379**: Redis Cache

## 📝 Environment Variables

Key variables to customize in `.env`:

```env
# Cache TTL (seconds)
CACHE_TTL=600

# Log level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# Database pool size
DB_POOL_SIZE=20

# Request timeout (seconds)
REQUEST_TIMEOUT=30
```

## 🎯 Next Steps

1. **Add Authentication**: Implement JWT or OAuth2
2. **Add Rate Limiting**: Prevent API abuse
3. **Set up Monitoring**: Integrate Prometheus/Grafana
4. **ML Integration**: Add ML-based route scoring
5. **Real-time Data**: Connect to live transit feeds
