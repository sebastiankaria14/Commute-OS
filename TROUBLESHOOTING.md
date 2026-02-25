# CommuteOS Troubleshooting Guide

## Common Issues and Solutions

### 1. Docker Desktop Not Running Error

**Error Message:**
```
unable to get image 'commuteos-routing_service': error during connect: 
Get "http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/...": 
open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
```

**Cause:** Docker Desktop is not started on Windows.

**Solution:**
1. Open Docker Desktop from Start menu
2. Wait for it to fully initialize (30-60 seconds)
3. Check system tray - Docker whale icon should be steady, not animated
4. Run: `docker --version` to verify
5. Then retry: `docker-compose up -d`

---

### 2. Port Already in Use

**Error Message:**
```
Bind for 0.0.0.0:8000 failed: port is already allocated
```

**Solution:**
```powershell
# Find what's using the port
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or change the port in docker-compose.yml
```

---

### 3. Database Connection Failed

**Error Message:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution:**
```powershell
# Check if PostgreSQL container is running
docker ps | findstr postgres

# View PostgreSQL logs
docker logs commuteos_postgres

# Restart PostgreSQL
docker-compose restart postgres

# If still failing, remove and recreate
docker-compose down -v
docker-compose up -d
```

---

### 4. Redis Connection Failed

**Error Message:**
```
redis.exceptions.ConnectionError: Error connecting to Redis
```

**Solution:**
```powershell
# Check if Redis container is running
docker ps | findstr redis

# View Redis logs
docker logs commuteos_redis

# Test Redis connection
docker exec -it commuteos_redis redis-cli ping
# Should return: PONG

# Restart Redis
docker-compose restart redis
```

---

### 5. Module Not Found Errors

**Error Message:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```powershell
# Install dependencies
pip install -r requirements.txt

# Or rebuild Docker images
docker-compose build --no-cache
docker-compose up -d
```

---

### 6. Image Build Failed

**Error Message:**
```
ERROR: failed to solve: failed to compute cache key
```

**Solution:**
```powershell
# Clean Docker build cache
docker builder prune -af

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

---

### 7. Services Not Starting

**Check service status:**
```powershell
docker-compose ps
```

**View logs for specific service:**
```powershell
# API Gateway logs
docker-compose logs api

# Routing Service logs
docker-compose logs routing_service

# All logs
docker-compose logs
```

---

### 8. WSL 2 Issues (Windows)

**Error Message:**
```
The WSL 2 distro could not be found
```

**Solution:**
1. Open Docker Desktop Settings
2. Go to "General"
3. Ensure "Use the WSL 2 based engine" is checked
4. Go to "Resources" → "WSL Integration"
5. Enable integration with your WSL distro
6. Restart Docker Desktop

---

### 9. Disk Space Issues

**Error Message:**
```
no space left on device
```

**Solution:**
```powershell
# Check Docker disk usage
docker system df

# Clean up unused resources
docker system prune -a --volumes

# Remove specific unused items
docker image prune -a
docker volume prune
docker network prune
```

---

### 10. Permission Denied (Windows)

**Error Message:**
```
Error response from daemon: open \\.\pipe\docker_engine: Access is denied
```

**Solution:**
1. Run PowerShell as Administrator
2. Or add your user to "docker-users" group:
   - Open "Computer Management"
   - Go to "Local Users and Groups" → "Groups"
   - Double-click "docker-users"
   - Add your user account
   - Log out and log back in

---

## Quick Diagnostics

### Check Everything
```powershell
# Run setup verification
python setup.py

# Check Docker
docker --version
docker-compose --version
docker ps

# Check services
docker-compose ps

# Check logs
docker-compose logs --tail=50
```

### Complete Reset
```powershell
# Stop everything
docker-compose down -v

# Remove all CommuteOS containers and images
docker rm -f $(docker ps -a -q --filter "name=commuteos")
docker rmi $(docker images --filter "reference=commuteos*" -q)

# Clean build
docker-compose build --no-cache
docker-compose up -d
```

---

## Getting Help

1. **Check logs first:**
   ```powershell
   docker-compose logs --tail=100
   ```

2. **Verify configuration:**
   ```powershell
   # Check .env file exists
   if (Test-Path .env) { Write-Host "✅ .env exists" } else { Write-Host "❌ .env missing" }
   
   # Validate docker-compose.yml
   docker-compose config
   ```

3. **Test individual components:**
   ```powershell
   # Test PostgreSQL
   docker run --rm postgres:15-alpine pg_isready
   
   # Test Redis
   docker run --rm redis:7-alpine redis-cli --version
   ```

4. **Network issues:**
   ```powershell
   # Check network
   docker network ls | findstr commuteos
   
   # Inspect network
   docker network inspect commuteos_network
   ```

---

## Performance Tuning

### If services are slow:

1. **Increase Docker resources:**
   - Docker Desktop Settings → Resources
   - Increase CPU and Memory allocation
   - Recommended: 4 CPUs, 8GB RAM

2. **Optimize database pool:**
   - Edit `.env`
   - Increase `DB_POOL_SIZE` if needed
   - Default is 20 connections

3. **Adjust cache settings:**
   - Edit `.env`
   - Modify `CACHE_TTL` for longer/shorter cache
   - Increase Redis memory in docker-compose.yml

---

## Health Check Endpoints

Test if services are responding:

```powershell
# API Gateway
curl http://localhost:8000/health

# Routing Service
curl http://localhost:8001/health

# PostgreSQL (from container)
docker exec commuteos_postgres pg_isready -U postgres

# Redis (from container)
docker exec commuteos_redis redis-cli ping
```

Expected responses:
- API Gateway: `{"status": "healthy", ...}`
- Routing Service: `{"status": "healthy", ...}`
- PostgreSQL: `accepting connections`
- Redis: `PONG`
