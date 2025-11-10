## ORE - Python Integration Application Features:

1. **ORERunner Class** - A wrapper that handles:
   - Configuration file creation
   - Portfolio XML generation
   - Market data setup
   - Running ORE calculations
   - Reading and parsing results

2. **Support for Multiple Trade Types**:
   - Interest Rate Swaps
   - FX Forwards
   - Easy to extend for other instruments

3. **Result Processing**:
   - NPV (Net Present Value) analysis
   - Cashflow extraction
   - CSV output handling

## Setup Guide Covers:

1. **Installation** - Multiple options (build from source, Docker)
2. **Data Sources** - Four different approaches to get market data:
   - ORE sample data
   - Manual creation
   - Live data fetching (yfinance)
   - Enterprise feeds (Bloomberg/Reuters)
3. **File Structure** - Complete directory layout
4. **Trade Portfolio Creation** - XML examples
5. **Running & Analysis** - Step-by-step execution
6. **Advanced Features** - Sensitivities, CVA, stress testing

## Quick Start Steps:

1. Install ORE (easiest via Docker)
2. Install Python dependencies: `pip install pandas numpy lxml`
3. Update the `ore_executable` path in the code
4. Run the sample portfolio
5. Analyze the results

# Docker Setup Guide for ORE Application

## Quick Start

### 1. Project Structure
```
ore-project/
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh
├── requirements.txt
├── ore_app.py
├── ore_input/          (created automatically)
├── ore_output/         (created automatically)
├── data/               (created automatically)
└── notebooks/          (optional, for Jupyter)
```

### 2. Build and Run

#### Basic Usage (Main Application Only)
```bash
# Build the Docker image
docker-compose build

# Run the application
docker-compose up

# Run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f ore-app

# Stop the application
docker-compose down
```

#### With Jupyter Notebook (Interactive Analysis)
```bash
# Start with Jupyter
docker-compose --profile jupyter up

# Access Jupyter at: http://localhost:8888
# Token will be displayed in the logs
```

#### With Database (Store Results)
```bash
# Start with PostgreSQL
docker-compose --profile database up

# Start with all services
docker-compose --profile jupyter --profile database --profile cache up
```

### 3. Running Commands Inside Container

```bash
# Execute Python script
docker-compose exec ore-app python3 ore_app.py

# Run ORE directly
docker-compose exec ore-app ore /app/ore_input/ore.xml

# Open bash shell
docker-compose exec ore-app bash

# Check ORE version
docker-compose exec ore-app ore --version
```

### 4. Development Workflow

#### Run with Auto-reload (Development Mode)
```bash
# The docker-compose.yml mounts ore_app.py as volume
# Any changes to ore_app.py will be immediately available

docker-compose up
# Edit ore_app.py locally
# Restart container to see changes:
docker-compose restart ore-app
```

#### Build Only (No Run)
```bash
docker-compose build --no-cache
```

### 5. Managing Data

#### Add Input Files
```bash
# Create sample portfolio
mkdir -p ore_input
cat > ore_input/portfolio.xml << 'EOF'
<?xml version="1.0"?>
<Portfolio>
  <Trade id="SWAP_001">
    <TradeType>Swap</TradeType>
    <!-- ... trade details ... -->
  </Trade>
</Portfolio>
EOF
```

#### Access Output Files
```bash
# Output files are written to ./ore_output/
ls -la ore_output/
cat ore_output/npv.csv
```

#### Backup Results
```bash
# Create backup of output
tar -czf ore_output_backup_$(date +%Y%m%d).tar.gz ore_output/

# Backup with Docker volumes
docker run --rm -v ore-project_postgres_data:/data -v $(pwd):/backup \
  ubuntu tar czf /backup/postgres_backup.tar.gz /data
```

### 6. Resource Management

#### Check Resource Usage
```bash
# Check container stats
docker stats ore-analytics

# Check disk usage
docker system df
```

#### Adjust Resources
Edit `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      cpus: '8.0'      # Increase CPU limit
      memory: 16G      # Increase memory limit
```

### 7. Troubleshooting

#### Container Won't Start
```bash
# Check logs
docker-compose logs ore-app

# Rebuild without cache
docker-compose build --no-cache

# Remove old containers and rebuild
docker-compose down -v
docker-compose up --build
```

#### ORE Executable Not Found
```bash
# Verify ORE installation
docker-compose exec ore-app which ore
docker-compose exec ore-app ore --version

# Check library dependencies
docker-compose exec ore-app ldd /usr/local/bin/ore
```

#### Python Dependencies Missing
```bash
# Reinstall requirements
docker-compose exec ore-app pip3 install -r requirements.txt

# Or rebuild container
docker-compose up --build
```

#### Out of Memory Errors
```bash
# Increase Docker memory limit
# Docker Desktop: Settings > Resources > Memory

# Or reduce parallelism in ORE calculations
# Edit ore.xml and reduce number of scenarios/paths
```

### 8. Production Deployment

#### Use Production Dockerfile
```dockerfile
# Remove development volume mounts
# Comment out in docker-compose.yml:
# - ./ore_app.py:/app/ore_app.py
```

#### Environment Configuration
```bash
# Create .env file
cat > .env << 'EOF'
ORE_EXECUTABLE=/usr/local/bin/ore
INPUT_DIR=/app/ore_input
OUTPUT_DIR=/app/ore_output
LOG_LEVEL=WARNING
TZ=America/New_York
EOF

# Use with docker-compose
docker-compose --env-file .env up -d
```

#### Health Checks
```bash
# Check if container is healthy
docker-compose ps

# Inspect health check
docker inspect --format='{{.State.Health.Status}}' ore-analytics
```

### 9. Advanced Usage

#### Run Specific ORE Analytics
```bash
# Run NPV calculation only
docker-compose exec ore-app python3 -c "
from ore_app import ORERunner
runner = ORERunner('/usr/local/bin/ore', 'ore_input', 'ore_output')
runner.create_ore_xml_config()
runner.run_ore()
"
```

#### Batch Processing
```bash
# Process multiple portfolios
for portfolio in portfolios/*.xml; do
  docker-compose exec ore-app ore "/app/ore_input/$portfolio"
done
```

#### Export Results to CSV
```bash
# Copy results from container
docker cp ore-analytics:/app/ore_output/npv.csv ./results/

# Or use volume mount (already configured)
cat ore_output/npv.csv
```

### 10. Cleanup

```bash
# Stop and remove containers
docker-compose down

# Remove volumes (WARNING: deletes all data)
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Clean everything (containers, volumes, images)
docker system prune -a --volumes
```

## Common Commands Cheat Sheet

```bash
# Build
docker-compose build

# Start
docker-compose up -d

# Stop
docker-compose down

# Logs
docker-compose logs -f

# Shell access
docker-compose exec ore-app bash

# Run ORE
docker-compose exec ore-app ore /app/ore_input/ore.xml

# Python REPL
docker-compose exec ore-app python3

# Restart
docker-compose restart ore-app

# Rebuild and start
docker-compose up --build
```

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `ORE_EXECUTABLE` | `/usr/local/bin/ore` | Path to ORE binary |
| `INPUT_DIR` | `/app/ore_input` | Input files directory |
| `OUTPUT_DIR` | `/app/ore_output` | Output files directory |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `TZ` | `UTC` | Timezone for timestamps |

## Profiles Reference

| Profile | Services Started | Use Case |
|---------|-----------------|----------|
| (default) | ore-app | Basic ORE calculations |
| `jupyter` | ore-app, jupyter | Interactive analysis |
| `database` | ore-app, postgres | Store results in DB |
| `cache` | ore-app, redis | Cache market data |

## Support

- Check logs: `docker-compose logs -f`
- GitHub Issues: https://github.com/OpenSourceRisk/Engine/issues
- ORE Documentation: https://opensourcerisk.org/docs/

============================================================================

# ORE (Open Source Risk Engine) Setup and Data Guide

...existing code...
See the ore_setup_guide.md -> [Setup guide](./ore_setup_guide.md)
...existing code...
