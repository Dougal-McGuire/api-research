# Modern Web Application Tech Stack Setup Guide

This guide provides step-by-step instructions for Claude Code to set up a new web application using a modern, production-ready tech stack in an empty folder. The project will use the folder name as the project ID.

## Tech Stack Overview

**Backend:**
- FastAPI (Python web framework)
- Uvicorn (ASGI server)
- Pydantic (Data validation)
- Pytest (Testing)

**Frontend:**
- React 18 with TypeScript
- Vite 6 (Build tool)
- Tailwind CSS (Styling)
- Axios (HTTP client)
- React Router (Routing)
- Lucide React (Icons)

**Infrastructure:**
- Docker & Docker Compose
- Google Cloud Run (Deployment)
- GitHub Actions (CI/CD)
- Google Artifact Registry

## Prerequisites

Before starting, ensure you have:
1. **Docker** and **Docker Compose** installed
2. **Node.js 20+** installed
3. **Python 3.11+** installed
4. **Google Cloud SDK** installed and configured
5. **GitHub CLI** installed
6. **GitHub Personal Access Token** with repo permissions

## Claude Setup Instructions

**User Instructions:** 
1. Navigate to your empty project folder
2. Create a `.env` file with your GitHub token: `GH_TOKEN=your_github_token_here`
3. Ask Claude to execute the setup process using the instructions below

**Claude Instructions:**
Follow these steps in order to set up the complete web application:

### Step 1: Load Environment Variables and Get Project Name

Use the `Bash` tool to load environment variables and get the project name:

```bash
# Load environment variables from .env file if it exists
if [ -f ".env" ]; then
    source .env
fi

# Get project name from current directory
PROJECT_NAME=$(basename "$(pwd)")
echo "Setting up project: $PROJECT_NAME"
```

### Step 2: Create Project Structure

Use the `Bash` tool to create the basic project structure:

```bash
# Create complete project structure
mkdir -p app/{api,core,models,schemas} tests frontend/{src/{components/layout,pages,services,types,utils},public} .github/workflows scripts static/{css,js} templates

# Create Python __init__.py files
touch app/__init__.py app/models/__init__.py app/schemas/__init__.py tests/__init__.py

# Create placeholder files for static assets
touch static/css/.gitkeep static/js/.gitkeep
```

### Step 3: Create Backend Configuration Files

Use the `Write` tool to create each of these files:

#### Create `requirements.txt`:
```
fastapi==0.111.0
uvicorn[standard]==0.30.0
gunicorn==22.0.0
pydantic==2.7.0
python-multipart==0.0.9
```

#### Create `requirements-dev.txt`:
```
pytest==8.2.0
pytest-asyncio==0.23.0
httpx==0.27.0
```

### Step 4: Create Backend Core Files

#### Create `app/main.py`:
```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.api.main import router as main_router

app = FastAPI(title="PROJECT_NAME API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(main_router, prefix="/api")

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": "PROJECT_NAME API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

#### Create `app/api/main.py`:
```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def api_root():
    return {"message": "PROJECT_NAME API is running"}

@router.get("/status")
async def api_status():
    return {"status": "ok", "message": "API is healthy"}
```

### Step 5: Create Docker Configuration

#### Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY static ./static
COPY templates ./templates

EXPOSE 8000

CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

#### Create `Dockerfile.dev`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

#### Create `docker-compose.dev.yml`:
```yaml
services:
  web:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    volumes:
      - ./app:/app/app
      - ./static:/app/static
      - ./templates:/app/templates
      - ./requirements-dev.txt:/app/requirements-dev.txt
    environment:
      - ENV=development
      - PYTHONPATH=/app
      - PYTHONDONTWRITEBYTECODE=1
      - PYTHONUNBUFFERED=1
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir /app/app
    restart: unless-stopped
    depends_on:
      - frontend

  frontend:
    image: node:20-alpine
    working_dir: /app
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - ./static:/app/dist
    command: sh -c "npm install && npm run dev -- --host 0.0.0.0"
    environment:
      - NODE_ENV=development
    restart: unless-stopped
```

### Step 6: Create Frontend Configuration

#### Create `frontend/package.json`:
```json
{
  "name": "PROJECT_NAME-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.28.0",
    "axios": "^1.7.9",
    "lucide-react": "^0.468.0",
    "clsx": "^2.1.1"
  },
  "devDependencies": {
    "@types/react": "^18.3.17",
    "@types/react-dom": "^18.3.5",
    "@typescript-eslint/eslint-plugin": "^8.18.2",
    "@typescript-eslint/parser": "^8.18.2",
    "@vitejs/plugin-react": "^4.3.4",
    "autoprefixer": "^10.4.20",
    "eslint": "^9.17.0",
    "eslint-plugin-react-hooks": "^5.0.0",
    "eslint-plugin-react-refresh": "^0.4.16",
    "postcss": "^8.5.2",
    "tailwindcss": "^3.4.17",
    "typescript": "~5.6.2",
    "vite": "^6.0.7"
  }
}
```

#### Create `frontend/vite.config.ts`:
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: process.env.NODE_ENV === 'production' ? '/static/' : '/',
  build: {
    outDir: '../static',
    emptyOutDir: true,
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://web:8000',
        changeOrigin: true,
      }
    }
  }
})
```

#### Create `frontend/tailwind.config.js`:
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        }
      }
    },
  },
  plugins: [],
}
```

#### Create `frontend/tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

#### Create `frontend/tsconfig.node.json`:
```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
```

#### Create `frontend/postcss.config.js`:
```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

### Step 7: Create Frontend Structure

#### Create `frontend/index.html`:
```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>PROJECT_NAME</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  </head>
  <body class="font-sans antialiased">
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

#### Create `frontend/src/main.tsx`:
```typescript
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

#### Create `frontend/src/App.tsx`:
```typescript
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/layout/Layout'
import HomePage from './pages/HomePage'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
```

#### Create `frontend/src/index.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

html {
  scroll-behavior: smooth;
}

body {
  @apply bg-gray-50 text-gray-900;
}

@layer components {
  .btn-primary {
    @apply bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200;
  }
  
  .input-field {
    @apply w-full px-3 py-2 border border-gray-300 rounded-lg transition-all duration-200 focus:ring-2 focus:ring-primary-500 focus:border-transparent;
  }
  
  .card {
    @apply bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-all duration-200 p-6;
  }
}
```

### Step 8: Create React Components

#### Create `frontend/src/components/layout/Layout.tsx`:
```typescript
import React from 'react'
import Header from './Header'
import Footer from './Footer'

interface LayoutProps {
  children: React.ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        {children}
      </main>
      <Footer />
    </div>
  )
}

export default Layout
```

#### Create `frontend/src/components/layout/Header.tsx`:
```typescript
import React from 'react'
import { Link } from 'react-router-dom'
import { Home } from 'lucide-react'

const Header: React.FC = () => {
  return (
    <header className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-6">
          <Link to="/" className="flex items-center space-x-3">
            <Home className="h-8 w-8 text-primary-600" />
            <span className="text-2xl font-bold text-gray-900">PROJECT_NAME</span>
          </Link>
        </div>
      </div>
    </header>
  )
}

export default Header
```

#### Create `frontend/src/components/layout/Footer.tsx`:
```typescript
import React from 'react'

const Footer: React.FC = () => {
  return (
    <footer className="bg-white border-t border-gray-200 mt-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center text-gray-500">
          <p>&copy; 2024 PROJECT_NAME. All rights reserved.</p>
        </div>
      </div>
    </footer>
  )
}

export default Footer
```

#### Create `frontend/src/pages/HomePage.tsx`:
```typescript
import React from 'react'

const HomePage: React.FC = () => {
  return (
    <div className="py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 sm:text-5xl md:text-6xl">
            Welcome to PROJECT_NAME
          </h1>
          <p className="mt-3 max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
            Modern web application built with FastAPI and React
          </p>
        </div>
        
        <div className="mt-16">
          <div className="max-w-3xl mx-auto">
            <div className="card">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                Ready to Start Building
              </h2>
              <p className="text-gray-600 mb-6">
                Your project is set up with a modern tech stack including FastAPI for the backend and React with TypeScript for the frontend. The development environment is ready to go!
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-900 mb-2">Backend Features</h3>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>• FastAPI with automatic OpenAPI docs</li>
                    <li>• Hot reload development server</li>
                    <li>• Docker containerization</li>
                    <li>• CORS middleware configured</li>
                  </ul>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-900 mb-2">Frontend Features</h3>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>• React 18 with TypeScript</li>
                    <li>• Vite for fast development</li>
                    <li>• Tailwind CSS for styling</li>
                    <li>• React Router for navigation</li>
                  </ul>
                </div>
              </div>
              <div className="mt-6 text-center">
                <a
                  href="/api/docs"
                  className="btn-primary mr-4"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  View API Docs
                </a>
                <a
                  href="https://github.com/your-username/PROJECT_NAME"
                  className="text-primary-600 hover:text-primary-700 font-medium"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  View on GitHub
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default HomePage
```

### Step 9: Create Configuration Files

#### Create `.env.example`:
```
# GitHub Personal Access Token for repository creation
GH_TOKEN=your_github_token_here

# Optional: Other environment variables
# NODE_ENV=development
# PYTHON_ENV=development
```

#### Create `.gitignore`:
```
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

node_modules/
.DS_Store
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

dist/
dist-ssr/
*.local

.vscode
.idea
*.swp
*.swo
*~

.pytest_cache/
.coverage
htmlcov/
.tox/
.nox/

static/css/
static/js/
!static/css/.gitkeep
!static/js/.gitkeep

# Environment files
.env
.env.local
.env.*.local
```

### Step 10: Create GitHub Actions Workflow

#### Create `.github/workflows/deploy.yml`:
```yaml
name: Build and Deploy to Google Cloud Run

on:
  push:
    branches: [ main ]
    tags: [ "v*" ]

env:
  PROJECT_ID: PROJECT_NAME
  SERVICE_NAME: PROJECT_NAME
  REGION: europe-west1

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    permissions:
      contents: read
      id-token: write

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Authenticate to Google Cloud
      uses: google-github-actions/auth@v2
      with:
        credentials_json: ${{ secrets.GCP_SA_KEY }}

    - name: Configure Docker to use Artifact Registry
      run: gcloud auth configure-docker $REGION-docker.pkg.dev

    - name: Build Docker image
      run: |
        docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/$SERVICE_NAME/$SERVICE_NAME:$GITHUB_SHA .

    - name: Push Docker image
      run: |
        docker push $REGION-docker.pkg.dev/$PROJECT_ID/$SERVICE_NAME/$SERVICE_NAME:$GITHUB_SHA

    - name: Deploy to Cloud Run
      run: |
        gcloud run deploy $SERVICE_NAME \
          --image $REGION-docker.pkg.dev/$PROJECT_ID/$SERVICE_NAME/$SERVICE_NAME:$GITHUB_SHA \
          --platform managed \
          --region $REGION \
          --allow-unauthenticated \
          --port 8000 \
          --memory 512Mi \
          --cpu 1 \
          --max-instances 10 \
          --quiet

    - name: Show service URL
      run: |
        gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)'
```

### Step 11: Replace PROJECT_NAME Placeholders

Use the `Bash` tool to replace all PROJECT_NAME placeholders with the actual project name:

```bash
# Get project name and replace placeholders
PROJECT_NAME=$(basename "$(pwd)")
find . -type f \( -name "*.py" -o -name "*.tsx" -o -name "*.ts" -o -name "*.json" -o -name "*.html" -o -name "*.yml" \) -exec sed -i "s/PROJECT_NAME/$PROJECT_NAME/g" {} \;
```

### Step 12: Initialize Git and Create Repository

```bash
# Initialize git repository
git init
git add .
git commit -m "Initial commit: Setup $PROJECT_NAME with modern web app tech stack"

# Create GitHub repository if GH_TOKEN is available
if [ -n "$GH_TOKEN" ]; then
    gh repo create "$PROJECT_NAME" --public --source=. --remote=origin --push
fi
```

### Step 13: Setup Google Cloud (Optional)

If Google Cloud CLI is available, use the `Bash` tool to set up the Google Cloud project:

```bash
# Create and configure Google Cloud project
gcloud projects create "$PROJECT_NAME" --name="$PROJECT_NAME"
gcloud config set project "$PROJECT_NAME"

# Enable required APIs
gcloud services enable artifactregistry.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Create Artifact Registry repository
gcloud artifacts repositories create "$PROJECT_NAME" --repository-format=docker --location=europe-west1

# Create service account and permissions
gcloud iam service-accounts create "$PROJECT_NAME-deploy" --display-name="$PROJECT_NAME Deploy Service Account"
gcloud projects add-iam-policy-binding "$PROJECT_NAME" \
    --member="serviceAccount:$PROJECT_NAME-deploy@$PROJECT_NAME.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.writer"
gcloud projects add-iam-policy-binding "$PROJECT_NAME" \
    --member="serviceAccount:$PROJECT_NAME-deploy@$PROJECT_NAME.iam.gserviceaccount.com" \
    --role="roles/run.admin"
gcloud projects add-iam-policy-binding "$PROJECT_NAME" \
    --member="serviceAccount:$PROJECT_NAME-deploy@$PROJECT_NAME.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

# Create service account key and set up GitHub secret
gcloud iam service-accounts keys create "gcp-key.json" \
    --iam-account="$PROJECT_NAME-deploy@$PROJECT_NAME.iam.gserviceaccount.com"
gh secret set GCP_SA_KEY < gcp-key.json
rm gcp-key.json
```

### Step 14: Install Dependencies and Start Development

```bash
# Install frontend dependencies
cd frontend && npm install && cd ..

# Install backend dependencies
pip install -r requirements-dev.txt

# Start development environment
docker-compose -f docker-compose.dev.yml up
```

## Usage Summary

**User Instructions:**
1. Create a `.env` file with `GH_TOKEN=your_token_here`
2. Ask Claude to execute the setup process step by step
3. Claude will create the complete project structure and configuration
4. Start development with `docker-compose -f docker-compose.dev.yml up`

**Access URLs:**
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Project Structure

```
project-name/
├── app/                    # FastAPI backend
│   ├── api/               # API routes
│   ├── core/              # Core utilities
│   ├── models/            # Database models
│   ├── schemas/           # Pydantic schemas
│   └── main.py           # FastAPI app
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   └── services/      # API services
│   └── package.json
├── tests/                 # Test files
├── .github/workflows/     # GitHub Actions
├── docker-compose.dev.yml # Development environment
└── Dockerfile            # Production container
```

This setup provides a complete, production-ready web application with modern development practices, automated deployment, and scalable architecture.