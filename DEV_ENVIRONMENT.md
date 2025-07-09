# Development Environment Guide

This document explains how to run the api-research development environment without port conflicts.

## Quick Start

### Starting Development Environment
```bash
./start-dev.sh
```

### Stopping Development Environment
```bash
./stop-dev.sh
```

### Load Development Aliases
```bash
source dev-aliases.sh
```

## What the Scripts Do

### `start-dev.sh`
- ✅ Checks for port conflicts on 5173 and 8000
- ✅ Stops any conflicting containers automatically
- ✅ Stops other running Docker Compose projects
- ✅ Starts api-research containers with unique project name
- ✅ Performs health checks
- ✅ Displays access URLs for Windows and WSL2

### `stop-dev.sh`
- ✅ Stops api-research containers
- ✅ Cleans up orphaned containers
- ✅ Shows remaining running containers

### `get-windows-urls.sh`
- ✅ Displays current WSL2 IP and access URLs
- ✅ Shows both Windows and WSL2 access methods

## Access URLs

### From Windows Browser
- Frontend: `http://[WSL2-IP]:5173`
- Backend: `http://[WSL2-IP]:8000`
- API Docs: `http://[WSL2-IP]:8000/docs`

### From WSL2 Terminal
- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

## Development Aliases

After running `source dev-aliases.sh`:

| Alias | Command | Description |
|-------|---------|-------------|
| `dev-start` | `./start-dev.sh` | Start development environment |
| `dev-stop` | `./stop-dev.sh` | Stop development environment |
| `dev-logs` | `docker compose -f docker-compose.dev.yml logs -f` | View container logs |
| `dev-status` | `docker compose -f docker-compose.dev.yml ps` | Show container status |
| `dev-urls` | `./get-windows-urls.sh` | Show access URLs |
| `dev-restart` | `./stop-dev.sh && ./start-dev.sh` | Restart development environment |
| `dev-build` | `docker compose -f docker-compose.dev.yml build` | Rebuild containers |
| `dev-shell-web` | `docker compose -f docker-compose.dev.yml exec web bash` | Open shell in web container |
| `dev-shell-frontend` | `docker compose -f docker-compose.dev.yml exec frontend sh` | Open shell in frontend container |

## Docker Compose Configuration

The `docker-compose.dev.yml` file includes:
- ✅ Unique project name: `api-research`
- ✅ Explicit port binding to `0.0.0.0` for WSL2 compatibility
- ✅ Auto-restart policies
- ✅ Volume mounts for hot-reloading
- ✅ Proper service dependencies

## Troubleshooting

### Port Conflicts
If you get port conflicts, run:
```bash
./start-dev.sh
```
The script automatically resolves conflicts.

### WSL2 Access Issues
1. Get current WSL2 IP: `./get-windows-urls.sh`
2. Use the displayed URLs for Windows access
3. WSL2 IP changes when WSL restarts

### Container Issues
- View logs: `dev-logs`
- Check status: `dev-status`
- Restart: `dev-restart`
- Rebuild: `dev-build`

## Project Isolation

Each project uses a unique Docker Compose project name to prevent conflicts:
- `api-research` - This project
- Other projects use their own names

This ensures clean isolation between development environments.