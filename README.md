# API Research

Modern web application with FastAPI backend and React frontend, designed for rapid development and production deployment.

## 🚀 Quick Start

### Development Environment
```bash
# Start development servers
./start-dev.sh

# Load development aliases
source dev-aliases.sh

# Access URLs (WSL2)
./get-windows-urls.sh
```

**Development URLs:**
- Frontend: http://localhost:5173 (or WSL2 IP)
- Backend: http://localhost:8000 (or WSL2 IP)
- API Docs: http://localhost:8000/docs

### Production Deployment
```bash
# Setup Google Cloud and deploy
./setup-gcloud.sh

# Deploy to production
git push origin main
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server for development
- **Gunicorn** - WSGI server for production
- **Pydantic** - Data validation and settings
- **Pytest** - Testing framework

### Frontend
- **React 18** - UI library with hooks
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Lucide React** - Icon library

### Infrastructure
- **Docker** - Containerization
- **Google Cloud Run** - Serverless container platform
- **Google Artifact Registry** - Container image storage
- **GitHub Actions** - CI/CD pipeline
- **WSL2** - Windows development environment

## 📁 Project Structure

```
api-research/
├── app/                     # FastAPI backend
│   ├── api/                # API routes
│   ├── core/               # Core utilities
│   ├── models/             # Database models
│   ├── schemas/            # Pydantic schemas
│   └── main.py            # FastAPI application
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   ├── types/          # TypeScript types
│   │   └── utils/          # Utility functions
│   ├── public/             # Static assets
│   └── package.json        # Node.js dependencies
├── tests/                  # Test files
├── static/                 # Built frontend assets
├── .github/workflows/      # GitHub Actions
├── docker-compose.dev.yml  # Development environment
├── Dockerfile             # Production container
└── scripts/               # Utility scripts
```

## 🔧 Development

### Prerequisites
- **Docker** and **Docker Compose**
- **Node.js 20+**
- **Python 3.11+**
- **WSL2** (for Windows development)

### Setup
1. Clone the repository
2. Run development environment:
   ```bash
   ./start-dev.sh
   ```
3. Load development aliases:
   ```bash
   source dev-aliases.sh
   ```

### Development Commands
```bash
# Start development environment
dev-start

# Stop development environment
dev-stop

# View logs
dev-logs

# Check container status
dev-status

# Get access URLs
dev-urls

# Restart environment
dev-restart

# Rebuild containers
dev-build

# Open shell in containers
dev-shell-web
dev-shell-frontend
```

### Making Changes
- **Frontend**: Edit files in `frontend/src/` - hot reload enabled
- **Backend**: Edit files in `app/` - auto-reload enabled
- **Styling**: Uses Tailwind CSS classes
- **API**: FastAPI with automatic OpenAPI docs

## 🚀 Deployment

### Automated Deployment
1. **Setup**: Run `./setup-gcloud.sh`
2. **Deploy**: Push to `main` branch
3. **Monitor**: Check GitHub Actions for deployment status

### Manual Deployment
See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

### Production URLs
After deployment:
- **Application**: `https://your-service-url.run.app`
- **API**: `https://your-service-url.run.app/api`
- **API Docs**: `https://your-service-url.run.app/docs`

## 🧪 Testing

### Backend Tests
```bash
# Run Python tests
pytest tests/

# Run with coverage
pytest --cov=app tests/
```

### Frontend Tests
```bash
# Run React tests
cd frontend && npm test
```

## 📚 Documentation

- **[Development Environment](DEV_ENVIRONMENT.md)** - Local development setup
- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment
- **[Tech Stack Setup](TECH_STACK_SETUP.md)** - Complete setup guide

## 🔐 Security

### Development
- Environment variables in `.env` (not committed)
- Docker containers run with non-root users
- Hot reload only in development mode

### Production
- HTTPS enforced by Cloud Run
- Service account with minimal permissions
- Container image vulnerability scanning
- Secrets managed through GitHub Actions

## 🌟 Features

### Current Features
- ✅ Modern React frontend with TypeScript
- ✅ FastAPI backend with automatic docs
- ✅ Docker containerization
- ✅ WSL2 development environment
- ✅ Automated CI/CD pipeline
- ✅ Production-ready deployment
- ✅ Hot reload for development
- ✅ Port conflict resolution

### Planned Features
- 🔄 Database integration
- 🔄 User authentication
- 🔄 API rate limiting
- 🔄 Logging and monitoring
- 🔄 Unit and integration tests

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Test** thoroughly
5. **Submit** a pull request

### Development Workflow
```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "feat: add new feature"

# Push and create PR
git push origin feature/new-feature
```

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Dougal-McGuire/api-research/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Dougal-McGuire/api-research/discussions)
- **Documentation**: Check the docs/ directory

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 Acknowledgments

- Built with modern web development best practices
- Optimized for rapid development and deployment
- Designed for scalability and maintainability
- WSL2 compatible for Windows developers

---

**Made with ❤️ for modern web development**