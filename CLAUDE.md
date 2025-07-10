# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a pharmaceutical research web application that uses OpenAI models to search regulatory databases (EMA, FDA) for drug approval documents and bioequivalence guidance. The system consists of a FastAPI backend serving a React frontend, deployed on Google Cloud Run.

## Development Commands

### Quick Start Development
```bash
./start-dev.sh     # Start full development environment
./stop-dev.sh      # Stop development environment
source dev-aliases.sh && dev-urls  # Show access URLs (important for WSL2)
```

### Frontend Development
```bash
cd frontend
npm run dev        # Start Vite dev server (port 5173)
npm run build      # Production build
npm run lint       # Run ESLint
```

### Backend Testing
```bash
pytest tests/                    # Run all tests
pytest tests/test_specific.py    # Run specific test file
pytest -k "test_function_name"   # Run specific test
python test_local.py             # Run basic functionality tests
```

### Docker Operations
```bash
docker compose -f docker-compose.dev.yml logs -f     # View logs
docker compose -f docker-compose.dev.yml ps          # Check status
docker compose -f docker-compose.dev.yml down        # Stop containers
docker compose -f docker-compose.dev.yml up -d       # Start containers
docker compose -f docker-compose.dev.yml exec web bash    # Shell into backend
docker compose -f docker-compose.dev.yml exec frontend sh # Shell into frontend
```

## Architecture & Key Concepts

### Service Architecture
The application follows a service-oriented architecture with clear separation:
- **API Routes** (`app/api/`) - Handle HTTP requests and responses
- **Services** (`app/services/`) - Business logic layer
  - `openai_research_service.py` - Main research orchestrator using OpenAI
  - `research_service.py` - Legacy research implementation
  - `web_service.py` - Web scraping functionality
  - `pdf_service.py` - PDF download and processing
- **Schemas** (`app/schemas/`) - Pydantic models for request/response validation

### Research Flow
1. User enters pharmaceutical substance name in frontend
2. Frontend sends request to `/api/research/search` with substance name and selected AI model
3. Backend loads prompt template from `app/core/research_prompt_template.txt`
4. OpenAI model searches regulatory databases using web search capabilities
5. Results are formatted and returned to frontend
6. Frontend displays research results with clickable links

### Key Files to Understand
- `app/core/research_prompt_template.txt` - The AI prompt template (user-editable)
- `app/services/openai_research_service.py` - Core research logic
- `frontend/src/pages/HomePage.tsx` - Main UI component
- `app/api/research.py` - API endpoints including model selection

### Model Support
The system dynamically fetches available OpenAI models that support web search:
- Default model: `o1` (reasoning + web search)
- Models are filtered to only show web-search capable variants
- User selection is persisted in browser localStorage
- Special handling for o1-pro (falls back to o1 due to API limitations)

### Environment Variables
Required in `.env` file:
```
OPENAI_API_KEY=your_key_here
ENV=development
```

### Frontend-Backend Communication
- Frontend uses Axios for API calls
- All research requests go to `/api/research/search`
- Model selection is passed in request body
- Debug mode shows detailed prompt and response info

### Deployment
- Push to `main` branch triggers automatic deployment via GitHub Actions
- Builds Docker image and deploys to Google Cloud Run
- Static files served from `/static` directory
- Frontend built into backend container for production

## Important Patterns

### Adding New API Endpoints
1. Define Pydantic schemas in `app/schemas/`
2. Add endpoint to appropriate router in `app/api/`
3. Implement business logic in service layer
4. Update frontend API calls in `frontend/src/services/`

### Modifying Research Behavior
- Edit `app/core/research_prompt_template.txt` for prompt changes
- Update `app/services/openai_research_service.py` for logic changes
- Model selection logic is in `app/api/research.py` (get_available_models)

### Frontend State Management
- Component-level state with React hooks
- Model selection stored in localStorage
- No global state management library (intentionally simple)

### Error Handling
- Backend returns HTTPException with status codes
- Frontend displays errors in UI with retry capability
- Detailed error logging in backend services

## Development Tips

### Hot Reload
- Backend: Uvicorn watches `app/` directory
- Frontend: Vite HMR enabled
- Changes to prompt template require no restart

### Testing New Models
- Check available models: `GET /api/research/models`
- Models must support web search to be included
- Test with debug mode enabled to see prompts/responses

### Common Issues
- WSL2: Use `dev-urls` command to get correct IP addresses
- Docker: Ensure Docker Desktop WSL2 integration is enabled
- Ports: 8000 (backend) and 5173 (frontend) must be free

## Custom Claude Commands

### /cp - Create Git Checkpoint
Creates a git commit with all current changes. Usage:
- `/cp` - Creates checkpoint with timestamp
- `/cp feature-complete` - Creates checkpoint with custom message

The commit message format:
- With name: `checkpoint: {name}`
- Without name: `checkpoint: {timestamp}`

Example: `/cp api-refactor` creates commit "checkpoint: api-refactor"