# Frontend Development Guide

ARL frontend provides a modern web interface for managing research projects and workflows.

## Technology Stack

- **Framework:** React 18 with TypeScript
- **Build Tool:** Vite 6
- **Styling:** Tailwind CSS 4 + shadcn/ui components
- **API Client:** TanStack Query (React Query)
- **Routing:** React Router v7
- **State Management:** Zustand
- **Form Handling:** React Hook Form + Zod validation

## Quick Start

### 1. Setup

```bash
cd arl-frontend

# Install dependencies
npm install

# Configure API endpoint
echo "VITE_API_BASE_URL=http://localhost:8000" > .env

# Start development server
npm run dev
```

### 2. Backend API

```bash
# In separate terminal, start backend
cd arl-backend
uvicorn arl.api.main:app --reload --port 8000
```

### 3. Access

Open [http://localhost:5173](http://localhost:5173)

## Project Structure

```
arl-frontend/
├── src/
│   ├── components/
│   │   ├── ui/              # shadcn/ui components
│   │   ├── layout/          # Layout components
│   │   ├── projects/        # Project management
│   │   ├── sessions/        # Research sessions
│   │   └── papers/          # Paper library
│   ├── pages/
│   │   ├── Dashboard.tsx    # Main dashboard
│   │   ├── ProjectDetail.tsx
│   │   ├── SessionDetail.tsx
│   │   └── PaperLibrary.tsx
│   ├── services/
│   │   ├── api.ts           # API client
│   │   └── queries.ts       # React Query hooks
│   ├── types/
│   │   └── index.ts         # TypeScript types
│   ├── store/
│   │   └── index.ts         # Zustand store
│   └── App.tsx
├── public/
├── index.html
└── package.json
```

## Key Features

### Project Management

**Components:**
- `ProjectList.tsx` - List all projects
- `ProjectCard.tsx` - Project summary card
- `CreateProjectDialog.tsx` - New project form
- `ProjectDetail.tsx` - Full project view

**API Hooks:**
```typescript
import { useProjects, useCreateProject } from '@/services/queries'

// List projects
const { data: projects, isLoading } = useProjects()

// Create project
const createProject = useCreateProject()
await createProject.mutateAsync({
  name: "My Research",
  domain: "cs",
  objectives: "Study ML algorithms"
})
```

### Research Sessions

**Components:**
- `SessionList.tsx` - Session history
- `SessionCard.tsx` - Session summary
- `SessionDetail.tsx` - Full session view
- `StartSessionDialog.tsx` - New session form

**API Hooks:**
```typescript
import { useSessions, useStartSession, useContinueSession } from '@/services/queries'

// List sessions
const { data: sessions } = useSessions(projectId)

// Start research
const startSession = useStartSession()
await startSession.mutateAsync({
  projectId,
  request: "Test hypothesis"
})

// Continue session
const continueSession = useContinueSession()
await continueSession.mutateAsync({ sessionId })
```

### Paper Library

**Components:**
- `PaperList.tsx` - Paper library
- `PaperCard.tsx` - Paper summary
- `IngestPaperDialog.tsx` - Add papers form
- `PaperDetail.tsx` - Full paper view

**API Hooks:**
```typescript
import { usePapers, useIngestPaper } from '@/services/queries'

// List papers
const { data: papers } = usePapers(projectId)

// Ingest paper
const ingestPaper = useIngestPaper()
await ingestPaper.mutateAsync({
  projectId,
  arxivId: "2301.00001"
})
```

## API Integration

### API Client Configuration

```typescript
// src/services/api.ts
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor (add auth token if needed)
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor (handle errors)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data)
    return Promise.reject(error)
  }
)
```

### React Query Setup

```typescript
// src/services/queries.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from './api'

// Query: List projects
export const useProjects = () => {
  return useQuery({
    queryKey: ['projects'],
    queryFn: async () => {
      const response = await apiClient.get('/api/v1/projects/')
      return response.data
    }
  })
}

// Mutation: Create project
export const useCreateProject = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: CreateProjectRequest) => {
      const response = await apiClient.post('/api/v1/projects/', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
    }
  })
}
```

## State Management

### Zustand Store

```typescript
// src/store/index.ts
import { create } from 'zustand'

interface AppState {
  // Current project
  currentProjectId: string | null
  setCurrentProjectId: (id: string | null) => void

  // Current session
  currentSessionId: string | null
  setCurrentSessionId: (id: string | null) => void

  // UI state
  sidebarOpen: boolean
  toggleSidebar: () => void
}

export const useAppStore = create<AppState>((set) => ({
  currentProjectId: null,
  setCurrentProjectId: (id) => set({ currentProjectId: id }),

  currentSessionId: null,
  setCurrentSessionId: (id) => set({ currentSessionId: id }),

  sidebarOpen: true,
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen }))
}))
```

## Component Development

### Using shadcn/ui

```bash
# Add components
npx shadcn@latest add button
npx shadcn@latest add dialog
npx shadcn@latest add card

# Components are added to src/components/ui/
```

### Example Component

```typescript
// src/components/projects/ProjectCard.tsx
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useNavigate } from 'react-router-dom'

interface ProjectCardProps {
  project: Project
}

export function ProjectCard({ project }: ProjectCardProps) {
  const navigate = useNavigate()

  return (
    <Card>
      <CardHeader>
        <CardTitle>{project.name}</CardTitle>
        <CardDescription>
          Domain: {project.domain} • {project.sessions?.length || 0} sessions
        </CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground mb-4">
          {project.objectives}
        </p>
        <Button onClick={() => navigate(`/projects/${project.project_id}`)}>
          View Details
        </Button>
      </CardContent>
    </Card>
  )
}
```

## Styling

### Tailwind CSS

```typescript
// Using Tailwind utility classes
<div className="flex items-center justify-between p-4 bg-gray-100 rounded-lg">
  <h2 className="text-2xl font-bold text-gray-900">Title</h2>
  <Button variant="outline" size="sm">Action</Button>
</div>
```

### Dark Mode

```typescript
// Configured in tailwind.config.js
export default {
  darkMode: 'class',  // Toggle via class on <html>
  // ...
}

// Toggle dark mode
function toggleDarkMode() {
  document.documentElement.classList.toggle('dark')
}
```

## Form Handling

### React Hook Form + Zod

```typescript
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

const createProjectSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  domain: z.enum(['cs', 'biology', 'physics', 'general']),
  objectives: z.string().min(10, 'Objectives must be at least 10 characters')
})

type CreateProjectForm = z.infer<typeof createProjectSchema>

export function CreateProjectForm() {
  const form = useForm<CreateProjectForm>({
    resolver: zodResolver(createProjectSchema),
    defaultValues: {
      name: '',
      domain: 'cs',
      objectives: ''
    }
  })

  const createProject = useCreateProject()

  const onSubmit = async (data: CreateProjectForm) => {
    await createProject.mutateAsync(data)
  }

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      {/* Form fields */}
    </form>
  )
}
```

## Development Workflow

### Running Development Server

```bash
# Start dev server
npm run dev

# Dev server runs on http://localhost:5173
# Hot module replacement (HMR) enabled
```

### Building for Production

```bash
# Build
npm run build

# Preview production build
npm run preview
```

### Linting & Formatting

```bash
# Lint
npm run lint

# Fix lint issues
npm run lint:fix

# Format with Prettier
npm run format
```

## Testing

```bash
# Run tests
npm run test

# Watch mode
npm run test:watch

# Coverage
npm run test:coverage
```

## Environment Variables

```bash
# .env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=ARL Research Lab
VITE_ENABLE_ANALYTICS=false
```

Access in code:
```typescript
const apiUrl = import.meta.env.VITE_API_BASE_URL
```

## Deployment

### Static Build

```bash
# Build
npm run build

# Output in dist/
# Deploy dist/ to static hosting (Vercel, Netlify, etc.)
```

### Docker

```bash
# Build Docker image
docker build -t arl-frontend .

# Run container
docker run -p 80:80 arl-frontend
```

## Troubleshooting

### API Connection Issues

```bash
# Verify backend is running
curl http://localhost:8000/api/v1/health

# Check CORS configuration in backend
# Ensure frontend URL is allowed
```

### Hot Reload Not Working

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Build Errors

```bash
# Type errors
npm run typecheck

# Clear cache
rm -rf node_modules/.vite
npm run dev
```

## Next Steps

- See `ARL_FRONTEND_SPECIFICATION.md` for complete feature specs
- See `ARL_FRONTEND_IMPLEMENTATION_PLAN.md` for implementation phases
- Contribute components via pull requests
