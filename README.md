# Multi-Tenant SaaS Project Management Application

[![CI/CD Pipeline](https://github.com/z1000biker/MultiTenantSaaSDemo/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/z1000biker/MultiTenantSaaSDemo/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A sophisticated, enterprise-grade project management tool (Trello-like) demonstrating **multi-tenant SaaS architecture**, **role-based access control (RBAC)**, and modern full-stack development practices.

## 🌟 Features

### Multi-Tenancy
- **Schema-per-Tenant Architecture**: Each tenant gets isolated PostgreSQL schema
- **Subdomain-based Tenant Identification**: `acme.yourapp.com`
- **Complete Data Isolation**: Zero cross-tenant data leakage
- **Dynamic Schema Creation**: Automatic tenant provisioning

### Role-Based Access Control (RBAC)
- **Admin**: Full tenant management, user management, all operations
- **Manager**: Create/manage projects, manage team members, all task operations
- **Member**: View projects, manage own tasks, comment on tasks

### Project Management
- **Trello-like Kanban Boards**: Drag-and-drop lists and tasks
- **Project Workspaces**: Multiple boards per tenant
- **Task Management**: Assignments, due dates, priorities, labels
- **Team Collaboration**: Comments, mentions, activity tracking

### Security & Authentication
- **JWT-based Authentication**: Access and refresh tokens
- **Password Hashing**: Werkzeug secure password storage
- **Token Refresh**: Automatic token renewal
- **Permission Middleware**: Route-level access control

### Modern UI/UX
- **Glassmorphism Design**: Premium, modern aesthetic
- **Responsive Layout**: Mobile-first design
- **Smooth Animations**: Micro-interactions and transitions
- **Dark Theme**: Eye-friendly color palette

## 🏗️ Architecture

### Technology Stack

**Backend**
- Flask 3.0 - Python web framework
- SQLAlchemy 2.0 - ORM with PostgreSQL
- Flask-JWT-Extended - JWT authentication
- Flask-CORS - Cross-origin resource sharing
- Gunicorn - Production WSGI server

**Frontend**
- React 18 - UI library
- Vite - Build tool and dev server
- React Router - Client-side routing
- Axios - HTTP client
- Modern CSS - Glassmorphism, animations

**Database**
- PostgreSQL 15 - Relational database
- Schema-based multi-tenancy
- Row-level security ready

**DevOps**
- Docker & Docker Compose - Containerization
- GitHub Actions - CI/CD pipeline
- Nginx - Frontend web server

### Multi-Tenant Design

```
┌─────────────────────────────────────────────────────────┐
│                    Master Database                       │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Tenants Table                                       │ │
│  │ - id, name, subdomain, schema_name, is_active      │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌───────▼──────┐  ┌───────▼──────┐  ┌───────▼──────┐
│ tenant_acme  │  │ tenant_demo  │  │ tenant_xyz   │
│ Schema       │  │ Schema       │  │ Schema       │
│              │  │              │  │              │
│ - users      │  │ - users      │  │ - users      │
│ - projects   │  │ - projects   │  │ - projects   │
│ - lists      │  │ - lists      │  │ - lists      │
│ - tasks      │  │ - tasks      │  │ - tasks      │
│ - comments   │  │ - comments   │  │ - comments   │
└──────────────┘  └──────────────┘  └──────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/z1000biker/MultiTenantSaaSDemo.git
cd MultiTenantSaaSDemo
```

2. **Create environment file**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start with Docker Compose**
```bash
docker-compose up -d
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- API Docs: http://localhost:5000/

### First Time Setup

1. **Create a tenant workspace**
   - Navigate to http://localhost:3000/register
   - Fill in workspace details:
     - Workspace Name: "Acme Inc."
     - Subdomain: "acme"
     - Admin credentials

2. **Login**
├── backend/
│   ├── models/           # Database models
│   │   ├── tenant.py     # Tenant model (master DB)
│   │   ├── user.py       # User model with RBAC
│   │   ├── project.py    # Project/Board model
│   │   ├── list.py       # List/Column model
│   │   └── task.py       # Task/Card model
│   ├── routes/           # API endpoints
│   │   ├── auth.py       # Authentication routes
│   │   ├── tenants.py    # Tenant management
│   │   ├── users.py      # User management
│   │   ├── projects.py   # Project CRUD
│   │   ├── lists.py      # List management
│   │   └── tasks.py      # Task management
│   ├── middleware/       # Custom middleware
│   │   ├── tenant_middleware.py  # Schema switching
│   │   └── rbac.py       # Role-based access control
│   ├── utils/            # Utility functions
│   │   └── database.py   # Schema management
│   ├── app.py            # Flask application
│   ├── config.py         # Configuration
│   └── requirements.txt  # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   │   ├── Auth/     # Login, Register
│   │   │   ├── Dashboard/# Project dashboard
│   │   │   └── Board/    # Kanban board
│   │   ├── context/      # React Context
│   │   │   └── AuthContext.jsx
│   │   ├── utils/        # Utilities
│   │   │   └── api.js    # API client
│   │   ├── styles/       # Global styles
│   │   ├── App.jsx       # Main app component
│   │   └── main.jsx      # Entry point
│   ├── package.json      # Node dependencies
│   └── vite.config.js    # Vite configuration
├── .github/
│   └── workflows/
│       └── ci-cd.yml     # GitHub Actions pipeline
├── docker-compose.yml    # Docker Compose config
├── .env.example          # Environment template
└── README.md             # This file
```

## 🔧 Development

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### Database Migrations

```bash
cd backend

# Initialize migrations
flask db init

# Create migration
flask db migrate -m "Description"

# Apply migration
flask db upgrade
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v --cov=app --cov-report=html
```

### Frontend Tests
```bash
cd frontend
npm run test
```

## 📚 API Documentation

### Authentication

**Register User**
```http
POST /api/auth/register
Content-Type: application/json
X-Tenant-Subdomain: acme

{
  "email": "user@example.com",
  "password": "securepassword",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Login**
```http
POST /api/auth/login
Content-Type: application/json
X-Tenant-Subdomain: acme

{
  "email": "user@example.com",
  "password": "securepassword"
}
```

### Projects

**Create Project**
```http
POST /api/projects
Authorization: Bearer {access_token}
X-Tenant-Subdomain: acme

{
  "name": "Website Redesign",
  "description": "Q1 2024 website redesign project",
  "color": "#4A90E2"
}
```

**Get All Projects**
```http
GET /api/projects
Authorization: Bearer {access_token}
X-Tenant-Subdomain: acme
```

### Tasks

**Create Task**
```http
POST /api/tasks/lists/{list_id}/tasks
Authorization: Bearer {access_token}
X-Tenant-Subdomain: acme

{
  "title": "Design homepage mockup",
  "description": "Create high-fidelity mockup",
  "priority": "high",
  "due_date": "2024-01-15T00:00:00"
}
```

## 🔒 Security Considerations

- **Environment Variables**: Never commit `.env` files
- **JWT Secrets**: Use strong, random secrets in production
- **Database Credentials**: Rotate regularly
- **CORS**: Configure allowed origins properly
- **HTTPS**: Use SSL/TLS in production
- **Rate Limiting**: Implement API rate limiting
- **Input Validation**: All inputs are validated
- **SQL Injection**: Protected via SQLAlchemy ORM
- **XSS**: React escapes output by default

## 🚢 Deployment

### Production Checklist

- [ ] Set strong `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] Configure production database
- [ ] Set `FLASK_ENV=production`
- [ ] Configure CORS origins
- [ ] Enable HTTPS
- [ ] Set up database backups
- [ ] Configure logging and monitoring
- [ ] Set up error tracking (e.g., Sentry)
- [ ] Implement rate limiting
- [ ] Configure CDN for static assets

### Docker Production Build

```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d
```

## 📊 Performance

- **Backend**: Gunicorn with 4 workers
- **Frontend**: Nginx with gzip compression
- **Database**: PostgreSQL with connection pooling
- **Caching**: Ready for Redis integration
- **CDN**: Static assets can be served via CDN

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Nik** - [z1000biker](https://github.com/z1000biker)

## 🙏 Acknowledgments

- Flask community for excellent documentation
- React team for the amazing framework
- PostgreSQL for robust multi-tenancy support
- All open-source contributors

## 📧 Support

For support, email your-email@example.com or open an issue on GitHub.

---

**Built with ❤️ to demonstrate enterprise-level SaaS architecture**
