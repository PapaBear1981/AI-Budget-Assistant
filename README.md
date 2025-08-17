# AI Budget Assistant

A comprehensive household budget management application built with Flutter frontend and Python FastAPI backend, featuring AI-powered financial insights and recommendations.

## 🚀 Features

- **AI-Powered Financial Insights**: Leverages CrewAI framework with specialized agents for financial analysis, transaction processing, and budget advice
- **Cross-Platform Flutter App**: Beautiful, responsive UI with animations and modern design
- **Secure Backend**: FastAPI with comprehensive security middleware and authentication
- **Real-time Chat Interface**: Natural language interaction with AI financial advisors
- **Transaction Management**: Automated categorization and analysis
- **Budget Tracking**: Smart budget recommendations and spending insights
- **Security First**: Comprehensive security architecture with threat modeling

## 🏗️ Architecture

### Frontend (Flutter)
- **Framework**: Flutter with Dart
- **Architecture**: Clean Architecture with feature-based organization
- **Navigation**: Go Router for declarative routing
- **State Management**: Provider/Riverpod (to be implemented)
- **UI/UX**: Material Design 3 with custom animations

### Backend (Python)
- **Framework**: FastAPI
- **AI Framework**: CrewAI with specialized agents
- **Database**: SQLite with Alembic migrations
- **Authentication**: JWT-based with secure middleware
- **Security**: Comprehensive security layers and monitoring

## 🤖 AI Agents

The application uses CrewAI framework with three specialized agents:

1. **Financial Analyst Agent**: Analyzes spending patterns and financial health
2. **Transaction Processor Agent**: Categorizes and processes transactions
3. **Budget Advisor Agent**: Provides personalized budget recommendations

## 📁 Project Structure

```
├── lib/                    # Flutter frontend
│   ├── core/              # Core functionality (theme, navigation)
│   ├── features/          # Feature modules
│   └── shared/            # Shared widgets and utilities
├── backend/               # Python FastAPI backend
│   ├── ai/               # AI agents and CrewAI setup
│   ├── core/             # Core backend functionality
│   ├── routers/          # API endpoints
│   ├── services/         # Business logic
│   └── middleware/       # Security and middleware
├── docs/                 # Documentation
├── specs/                # Project specifications
└── tests/                # Test suites
```

## 🛠️ Setup and Installation

### Prerequisites
- Flutter SDK (latest stable)
- Python 3.11+
- Git

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

6. Start the backend server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup
1. Install Flutter dependencies:
   ```bash
   flutter pub get
   ```

2. Run the Flutter app:
   ```bash
   flutter run
   ```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
flutter test
```

## 📚 Documentation

- [Architecture Documentation](docs/architecture/)
- [Security Documentation](docs/security/)
- [API Contracts](docs/architecture/api-contracts.md)
- [Project Specifications](specs/)

## 🔒 Security

This project implements comprehensive security measures:
- JWT authentication with secure token handling
- Input validation and sanitization
- Rate limiting and DDoS protection
- Comprehensive logging and monitoring
- Threat modeling and incident response plans

See [Security Architecture](docs/security/security-architecture.md) for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- CrewAI framework for AI agent orchestration
- Flutter team for the amazing cross-platform framework
- FastAPI for the high-performance Python web framework
