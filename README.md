# Slippi Stats Server

A comprehensive web application for analyzing Super Smash Bros. Melee replay data with advanced player statistics, interactive charts, and real-time filtering capabilities.

## **Quick Start** 🚀

### **Development Setup**
```bash
# Clone and setup
git clone <repository>
cd slippi-stats-server

# Windows (recommended)
start_dev.bat

# Manual setup
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate.bat on Windows
pip install -r requirements.txt
python app.py
```

### **Access Points**
- **Web Interface**: `http://localhost:5000`
- **API Documentation**: See [API Reference](#api-reference) below
- **Observability**: `docker-compose up -d` (optional)

## **Features** ✨

### **Player Analytics**
- **Basic Profiles**: Win rates, character usage, recent games, performance highlights
- **Advanced Filtering**: Filter by character, opponent, opponent character, stage, date range
- **Performance Trends**: Time-series charts showing improvement over time
- **Character Statistics**: Detailed win rates and usage patterns for each character
- **Matchup Analysis**: Head-to-head performance against specific opponents

### **Data Management**
- **Automated Collection**: Client applications upload replay data automatically
- **File Upload System**: Secure upload and storage of .slp replay files
- **API Authentication**: Secure API key system for client access
- **Data Validation**: Comprehensive validation and error handling
- **Real-time Processing**: Immediate statistics updates after data upload

### **User Experience**
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Interactive Charts**: Chart.js powered visualizations with drill-down capabilities
- **Character Icons**: Visual character representations throughout the interface
- **Smart Search**: Flexible player search with case-insensitive matching
- **Real-time Filtering**: Frontend filtering with instant results

## **Architecture** 🏗️

### **Backend: Service-Oriented Architecture**
```
Routes → Services → Database → External SQL
- Clean separation of concerns
- External SQL file management
- Hybrid monolithic + domain services
- Comprehensive error handling
```

### **Frontend: Component-Based Architecture**
```
Pages → Layouts → Components
- Self-contained UI components
- Progressive enhancement
- Auto-initialization patterns
- Asset ownership model
```

**Detailed Documentation**: [ARCHITECTURE.md](ARCHITECTURE.md)

## **API Reference** 📚

### **Player Endpoints**
```bash
# Basic player statistics
GET /api/player/{player_code}/stats

# Advanced filtering and analysis
POST /api/player/{player_code}/detailed
Content-Type: application/json
{
  "character": "Fox",
  "opponent": "all",
  "opponent_character": "Falco",
  "stage": "all",
  "limit": 100
}

# Paginated game history
GET /api/player/{player_code}/games?page=1&per_page=20
```

### **Data Management Endpoints**
```bash
# Client registration
POST /api/clients/register
Content-Type: application/json
{
  "client_name": "MyApp",
  "version": "1.0.0",
  "hostname": "my-computer"
}

# Game data upload (requires API key)
POST /api/games/upload
X-API-Key: your-api-key-here
Content-Type: application/json
{
  "games": [...],
  "files": [...]
}

# File upload (requires API key)
POST /api/files/upload
X-API-Key: your-api-key-here
Content-Type: application/json
{
  "files": [...]
}
```

### **Server Information**
```bash
# Server statistics and health
GET /api/server/stats

# File listings (requires API key)
GET /api/files
X-API-Key: your-api-key-here
```

### **Authentication**
All data modification endpoints require API key authentication via `X-API-Key` header. Register a client to receive an API key.

## **Configuration** ⚙️

### **Development**
The application uses sensible defaults for development. No additional configuration required.

### **Production**
Set environment variables for production deployment:

```bash
# Database
DATABASE_PATH=/path/to/database.db

# Security
SECRET_KEY=your-secret-key-here
API_KEY_LENGTH=32

# File Upload
MAX_UPLOAD_SIZE=104857600  # 100MB
UPLOADS_DIR=/path/to/uploads

# Rate Limiting
RATE_LIMIT_API=120
RATE_LIMIT_UPLOADS=60
RATE_LIMIT_REGISTRATION=10

# Observability (optional)
ENABLE_OBSERVABILITY=True
JAEGER_ENDPOINT=http://localhost:14268/api/traces
PROMETHEUS_ENDPOINT=http://localhost:9090
```

## **Development** 👨‍💻

### **Project Structure**
```
slippi-stats-server/
├── app.py                     # Flask application entry point
├── backend/                   # Backend services and logic
│   ├── routes/               # HTTP route handlers
│   ├── services/             # Business logic (monolithic + domain)
│   ├── db/                   # Database access layer
│   ├── sql/                  # External SQL queries (organized by category)
│   └── config.py             # Configuration management
├── frontend/                  # Frontend templates and assets
│   ├── components/           # Reusable UI components
│   ├── layouts/              # Page layout templates
│   ├── pages/                # Individual page templates
│   └── static/               # CSS, JavaScript, images
├── tests/                    # Test suite (51% coverage)
└── docs/                     # Additional documentation
```

### **Development Guidelines**
- **Backend**: Follow service layer patterns and external SQL organization
- **Frontend**: Use component-based architecture with progressive enhancement
- **Testing**: Add tests that align with architectural boundaries
- **SQL**: Create external .sql files for all database queries
- **Documentation**: Update relevant docs when making architectural changes

### **Adding New Features**

#### **New API Endpoint**
1. Add route to `backend/routes/api_routes.py`
2. Add business logic to appropriate service in `backend/services/`
3. Create SQL queries in `backend/sql/` if needed
4. Add authentication/rate limiting decorators
5. Update API documentation
6. Add comprehensive tests

#### **New Web Page**
1. Add route to `backend/routes/web_routes.py`
2. Add template data logic to `backend/services/web_service.py`
3. Create page template in `frontend/pages/`
4. Add any required SQL queries
5. Add service layer tests

#### **New Frontend Component**
1. Create component directory in `frontend/components/`
2. Implement self-contained CSS, JS, and template files
3. Add component to appropriate layout
4. Follow progressive enhancement principles

### **Testing**
```bash
# Run all tests
python -m pytest

# Run specific test categories
python -m pytest tests/test_service_layer.py      # Fast service tests
python -m pytest tests/test_database.py           # Database integration
python -m pytest tests/test_api_endpoints.py      # API endpoint tests
python -m pytest tests/test_web_pages.py          # Web page rendering

# Coverage report
python -m pytest --cov=backend --cov-report=html
```

**Current Coverage**: 51% (target: 75%)

## **Documentation** 📖

### **Core Documentation**
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Complete architectural reference
- **[CHANGELOG.md](CHANGELOG.md)** - Project history and recent changes
- **[SERVICE_DIRECTORY.md](SERVICE_DIRECTORY.md)** - Backend service catalog
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Development guidelines

### **Specialized Documentation**
- **[backend/README.md](backend/README.md)** - Backend implementation details
- **[frontend/README.md](frontend/README.md)** - Frontend architecture
- **[tests/README.md](tests/README.md)** - Testing guidelines
- **[backend/sql/README.md](backend/sql/README.md)** - SQL management

## **Deployment** 🚀

### **Production Deployment**
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_PATH=/opt/slippi-server/data/database.db
export SECRET_KEY=your-production-secret

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Or use systemd service
sudo systemctl start slippi-server.service
```

### **Docker Deployment**
```bash
# Build image
docker build -t slippi-server .

# Run container
docker run -d \
  -p 5000:5000 \
  -v /data:/app/data \
  -e DATABASE_PATH=/app/data/database.db \
  slippi-server
```

### **Observability Stack** (Optional)
```bash
# Start monitoring stack
docker-compose up -d

# Access dashboards
# Grafana: http://localhost:3000
# Jaeger: http://localhost:16686
# Prometheus: http://localhost:9090
```

## **Performance** ⚡

### **Current Characteristics**
- **Response Times**: Sub-second for most operations
- **Database**: SQLite with optimized external SQL queries
- **Concurrency**: Multi-worker Gunicorn deployment
- **Caching**: Minimal (opportunity for improvement)
- **Frontend**: Progressive loading with component-based architecture

### **Scaling Considerations**
- **Database**: External SQL makes PostgreSQL migration straightforward
- **Services**: Clear boundaries enable microservice extraction
- **Frontend**: Component architecture supports CDN deployment
- **Monitoring**: Full observability stack for performance tracking

## **Troubleshooting** 🔧

### **Common Issues**

#### **Server Won't Start**
```bash
# Check configuration
python -c "from backend.config import get_config; print(get_config().__dict__)"

# Check dependencies
pip check

# Check database
ls -la data/database.db
```

#### **Frontend Filters Not Working**
- Verify API endpoints are accessible: `curl http://localhost:5000/api/player/TEST%23123/detailed`
- Check browser console for JavaScript errors
- Ensure character data structure is correct

#### **Upload Failures**
- Verify API key is valid: `curl -H "X-API-Key: your-key" http://localhost:5000/api/files`
- Check file size limits and content types
- Review server logs for detailed error messages

### **Getting Help**
1. Check existing issues in the repository
2. Review the troubleshooting section in [SERVICE_DIRECTORY.md](SERVICE_DIRECTORY.md)
3. Enable debug logging: `export FLASK_ENV=development`
4. Create detailed issue with error logs and steps to reproduce

## **License** 📄

This project is open source. Please see the LICENSE file for details.

## **Contributing** 🤝

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup instructions
- Code style guidelines
- Architecture patterns to follow
- Testing requirements
- Pull request process

### **Quick Contributing Guide**
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Follow the established architecture patterns
4. Add tests for new functionality
5. Update documentation as needed
6. Submit a pull request with clear description

---

**Built with**: Flask, SQLite, Bootstrap, Chart.js, OpenTelemetry  
**Architecture**: Service-oriented backend, component-based frontend  
**Status**: Production-ready, actively maintained