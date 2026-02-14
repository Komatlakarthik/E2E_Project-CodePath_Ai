# CodePath AI - An AI-Assisted Beginner Coding Platform

<div align="center">
  <img src="https://img.shields.io/badge/React-18.2.0-61dafb?style=flat-square&logo=react" alt="React" />
  <img src="https://img.shields.io/badge/FastAPI-0.109.0-009688?style=flat-square&logo=fastapi" alt="FastAPI" />
  <img src="https://img.shields.io/badge/MongoDB-7.0-47A248?style=flat-square&logo=mongodb" alt="MongoDB" />
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python" alt="Python" />
</div>

## 🎯 Overview

CodePath AI is a production-ready web application designed to help beginners learn programming through:

- **Micro-Lessons**: Bite-sized lessons covering programming fundamentals
- **Hands-On Coding**: In-browser code editor with real-time execution
- **AI-Guided Hints**: Intelligent mentoring that guides without giving solutions
- **Progress Tracking**: Streaks, badges, and leaderboards to keep you motivated

### ⚠️ Core Philosophy

**The AI Mentor NEVER provides complete solutions.** Instead, it offers:
- Conceptual explanations
- Logical hints and guiding questions
- Error reasoning and debugging guidance
- Optimization suggestions and best practices

This approach ensures learners develop problem-solving skills rather than just copying code.

## 🚀 Learning Tracks

1. **Java with DSA** - Java fundamentals and Data Structures & Algorithms
2. **Data Science** - Python, NumPy, Pandas, and data analysis
3. **AI Engineer** - Machine learning concepts and implementations

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **MongoDB** - NoSQL database with Motor async driver
- **JWT** - Secure authentication with access & refresh tokens
- **Piston API** - Safe code execution in isolated containers

### Frontend
- **React 18** - UI library with hooks
- **Vite** - Lightning-fast build tool
- **Tailwind CSS** - Utility-first styling
- **Monaco Editor** - VS Code's editor in the browser
- **Zustand** - Lightweight state management
- **React Router v6** - Client-side routing

## 📁 Project Structure

## 🧩 Team Module Architecture (4 Modules)

Project ownership is divided into these modules:

1. **User Management & Authentication**
2. **Learning Content & Micro-Lessons**
3. **Coding Practice & AI Guidance**
4. **Progress Tracking & Recommendation**

The backend now registers routes through module entrypoints in `backend/modules/`, and the frontend route wiring imports module entrypoints from `frontend/src/modules/`.

For full file ownership mapping and push order, see [MODULE_SPLIT.md](MODULE_SPLIT.md).

```
codepath-ai/
├── backend/
│   ├── main.py                 # FastAPI application entry
│   ├── config/
│   │   ├── database.py         # MongoDB connection
│   │   └── settings.py         # Environment settings
│   ├── models/
│   │   ├── user.py             # User model
│   │   ├── lesson.py           # Lesson model
│   │   ├── problem.py          # Problem model
│   │   ├── progress.py         # Progress model
│   │   └── ai_hint.py          # AI hint model
│   ├── routes/
│   │   ├── auth.py             # Authentication endpoints
│   │   ├── lessons.py          # Lesson CRUD
│   │   ├── practice.py         # Problem solving
│   │   ├── progress.py         # Progress tracking
│   │   └── ai_mentor.py        # AI hint endpoints
│   ├── services/
│   │   ├── auth_service.py     # Auth business logic
│   │   ├── lesson_service.py   # Lesson operations
│   │   ├── problem_service.py  # Problem operations
│   │   ├── code_execution_service.py  # Piston API
│   │   ├── progress_service.py # Stats & badges
│   │   └── ai_mentor_service.py # AI mentoring
│   ├── ai/
│   │   └── prompts.py          # AI prompt templates
│   └── utils/
│       └── security.py         # JWT & password utils
├── frontend/
│   ├── src/
│   │   ├── main.jsx            # React entry
│   │   ├── App.jsx             # Routes & layouts
│   │   ├── components/
│   │   │   ├── layouts/        # MainLayout, AuthLayout
│   │   │   └── editor/         # CodeEditor, OutputPanel, AIHintPanel
│   │   ├── pages/
│   │   │   ├── HomePage.jsx
│   │   │   ├── DashboardPage.jsx
│   │   │   ├── LessonsPage.jsx
│   │   │   ├── ProblemsPage.jsx
│   │   │   ├── ProblemSolvePage.jsx
│   │   │   ├── ProgressPage.jsx
│   │   │   ├── ProfilePage.jsx
│   │   │   └── auth/
│   │   ├── services/           # API service layer
│   │   └── stores/             # Zustand stores
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md
```

## 🔧 Installation & Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB (local or Atlas)
- OpenAI or Anthropic API key

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/codepath-ai.git
   cd codepath-ai
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run the backend**
   ```bash
   cd backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**
   ```bash
   npm run dev
   ```

3. **Build for production**
   ```bash
   npm run build
   ```

## 🔐 Environment Variables

Create a `.env` file with the following:

```env
# MongoDB
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=codepath_ai

# JWT
JWT_SECRET_KEY=your-super-secret-key-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# AI Provider (choose one)
OPENAI_API_KEY=sk-your-openai-key
# OR
ANTHROPIC_API_KEY=your-anthropic-key

# Piston API
PISTON_API_URL=https://emkc.org/api/v2/piston

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:5173

# Environment
ENVIRONMENT=development
```

## 🌐 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login user |
| POST | `/api/auth/refresh` | Refresh access token |
| POST | `/api/auth/change-password` | Change password |
| GET | `/api/auth/me` | Get current user |
| PUT | `/api/auth/profile` | Update profile |

### Lessons
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/lessons` | List lessons |
| GET | `/api/lessons/{id}` | Get lesson details |
| GET | `/api/lessons/tracks` | Get learning tracks |
| POST | `/api/lessons/{id}/complete` | Mark as complete |

### Practice
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/practice/problems` | List problems |
| GET | `/api/practice/problems/{id}` | Get problem |
| POST | `/api/practice/problems/{id}/run` | Run code |
| POST | `/api/practice/problems/{id}/submit` | Submit solution |

### AI Mentor
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ai/hint` | Get AI hint |
| POST | `/api/ai/analyze-error` | Analyze code error |
| POST | `/api/ai/ask` | Ask AI question |

### Progress
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/progress/stats` | Get user stats |
| GET | `/api/progress/badges` | Get earned badges |
| GET | `/api/progress/leaderboard` | Get leaderboard |

## 🐳 Docker Deployment

```bash
# Build the image
docker build -t codepath-ai .

# Run the container
docker run -d -p 8000:8000 \
  -e MONGODB_URL=your-mongo-url \
  -e JWT_SECRET_KEY=your-secret \
  -e OPENAI_API_KEY=your-key \
  codepath-ai
```

## 🚀 Deployment on Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables in Render dashboard

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 🎨 Features

### For Learners
- 📚 Structured micro-lessons by track
- 💻 In-browser code editor with syntax highlighting
- 🤖 AI mentor for guidance (never gives solutions!)
- 📊 Progress tracking with streaks and badges
- 🏆 Leaderboard to compete with others

### For Admins
- Create and manage lessons
- Add coding problems with test cases
- Configure AI prompt settings
- View user analytics

## 🤖 AI Mentoring Rules

The AI strictly follows these guidelines:

1. **NEVER** provide complete code solutions
2. **NEVER** write the function body or implementation
3. **ALWAYS** guide with questions and hints
4. **FOCUS** on teaching concepts and problem-solving

Example AI response:
> "I notice you're trying to find the maximum element. Think about this: what happens when you compare two numbers? How could you use that comparison as you go through each element?"


## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 Support

For questions or issues, please open a GitHub issue or contact the team.

---

<div align="center">
  Built with ❤️ for aspiring developers
</div>
