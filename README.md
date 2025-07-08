
# Personal Finance Management — Retrieval-Augmented Generation (RAG) v2.0

This repository contains an **enhanced Personal Finance Management** system that uses **OpenAI GPT-4** to answer queries about your financial documents. It leverages **semantic search** (via embeddings) and a **vector database** to store and retrieve document chunks with advanced analytics and insights.

---

## 🚀 **New Features in v2.0**

### **Enhanced Document Processing**
- **PDF Support**: Full PDF text extraction and processing
- **File Validation**: Size limits, type validation, and duplicate detection
- **Smart Chunking**: Improved text segmentation for better context
- **Processing Metadata**: File size, word count, and chunk statistics

### **Advanced Analytics Dashboard**
- **System Statistics**: Document counts, query metrics, processing times
- **Query History**: Track all queries with performance metrics
- **Financial Insights**: AI-powered trend analysis and entity extraction
- **Real-time Monitoring**: Live system performance tracking

### **Improved AI Capabilities**
- **GPT-4 Integration**: Latest model for better financial analysis
- **Enhanced Embeddings**: Updated to text-embedding-3-small
- **Retry Logic**: Robust error handling with automatic retries
- **Financial Entity Extraction**: Automatic detection of amounts, dates, accounts

### **Better User Experience**
- **Tabbed Interface**: Organized sections for Upload, Query, Analytics, and History
- **Document Type Filtering**: Query specific document types
- **Processing Time Display**: Real-time performance feedback
- **Enhanced Error Handling**: Better error messages and validation

---

## 🛠 **Tech Stack**

### **Backend**
- [Python 3.11+](https://www.python.org/)
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [SQLAlchemy 2.0](https://www.sqlalchemy.org/) - Database ORM
- [Alembic](https://alembic.sqlalchemy.org/) - Database migrations
- [OpenAI GPT-4](https://platform.openai.com/) - Advanced AI models
- [pgvector](https://github.com/pgvector/pgvector) - Vector similarity search
- [PostgreSQL 16](https://www.postgresql.org/) - Primary database

### **Frontend**
- [React 18](https://reactjs.org/) - Modern UI framework
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS
- [Heroicons](https://heroicons.com/) - Beautiful icons
- [Axios](https://axios-http.com/) - HTTP client

### **DevOps**
- [Docker](https://www.docker.com/) - Containerization
- [Docker Compose](https://docs.docker.com/compose/) - Multi-container orchestration

---

## 📁 **Project Structure**

```
RAG-Personal-Finance-Management/
├── alembic/                    # Database migrations
├── app/
│   ├── api/v1/endpoints/       # API endpoints
│   │   ├── analysis.py         # Query and analytics endpoints
│   │   └── documents.py        # Document management
│   ├── core/
│   │   └── config.py           # Configuration settings
│   ├── db/
│   │   ├── models/
│   │   │   └── document.py     # Database models
│   │   └── session.py          # Database session
│   ├── schemas/                # Pydantic models
│   ├── services/               # Business logic
│   │   ├── document_service.py # Document processing
│   │   └── openai_service.py   # AI integration
│   └── main.py                 # FastAPI application
├── frontend/                   # React application
├── docker-compose.yml          # Multi-container setup
├── Dockerfile                  # Backend container
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## 🚀 **Quick Start**

### **Option 1: Docker Compose (Recommended)**

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/rag-finance-management.git
   cd rag-finance-management
   ```

2. **Set Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. **Start the Application**
   ```bash
   docker-compose up -d
   ```

4. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### **Option 2: Local Development**

1. **Prerequisites**
   ```bash
   # Install PostgreSQL with pgvector
   # Install Python 3.11+
   # Install Node.js 18+
   ```

2. **Backend Setup**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
   # Set up database
   alembic upgrade head
   
   # Start backend
   uvicorn app.main:app --reload
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm start
   ```

---

## 📊 **API Endpoints**

### **Document Management**
- `POST /api/v1/documents/upload/` - Upload financial documents
- `GET /api/v1/documents/list/` - List uploaded documents

### **Query & Analysis**
- `POST /api/v1/analysis/query/` - Ask questions about documents
- `POST /api/v1/analysis/analyze-trends/` - Analyze financial trends
- `POST /api/v1/analysis/extract-entities/` - Extract financial entities
- `GET /api/v1/analysis/query-history/` - Get query history
- `GET /api/v1/analysis/analytics/` - Get system analytics

### **System**
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation

---

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_SERVER=localhost
POSTGRES_DB=finance_database

# OpenAI
OPENAI_API_KEY=sk-your-api-key-here

# Optional: Custom settings
MAX_FILE_SIZE=10485760  # 10MB
CHUNK_SIZE=1000
SIMILARITY_THRESHOLD=0.2
```

### **File Processing Settings**
- **Supported Formats**: PDF, TXT, DOC, DOCX
- **Max File Size**: 10MB (configurable)
- **Chunk Size**: 1000 characters (configurable)
- **Chunk Overlap**: 200 characters (configurable)

---

## 📈 **Usage Examples**

### **Upload Documents**
1. Navigate to the Upload tab
2. Select your financial document (PDF, TXT, etc.)
3. The system will automatically process and index the content

### **Ask Questions**
1. Go to the Query tab
2. Optionally select a document type filter
3. Ask natural language questions like:
   - "What is my closing balance for January?"
   - "How many transactions over $1000?"
   - "Show me all utility payments"
   - "What's my average monthly spending?"

### **View Analytics**
1. Visit the Analytics tab to see:
   - Total documents and queries
   - Average processing times
   - Recent activity
   - Document type distribution

### **Check History**
1. Go to the History tab to review:
   - All previous queries
   - Processing times
   - Relevant documents used

---

## 🔒 **Security Features**

- **File Validation**: Type and size restrictions
- **Duplicate Detection**: SHA-256 hash-based deduplication
- **Input Sanitization**: Protection against malicious uploads
- **CORS Configuration**: Configurable cross-origin settings
- **Error Handling**: Secure error messages without data leakage

---

## 🚀 **Performance Optimizations**

- **Vector Indexing**: Efficient similarity search with pgvector
- **Chunking Strategy**: Smart text segmentation for better context
- **Caching**: Embedding and query result caching
- **Async Processing**: Non-blocking document processing
- **Connection Pooling**: Optimized database connections

---

## 🧪 **Testing**

### **Backend Tests**
```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app
```

### **Frontend Tests**
```bash
cd frontend
npm test
```

---

## 📝 **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 **Support**

- **Documentation**: Check the API docs at `/docs`
- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Join the community discussions

---

## 🔄 **Changelog**

### **v2.0.0** (Current)
- ✨ Enhanced document processing with PDF support
- 📊 New analytics dashboard
- 🤖 Upgraded to GPT-4 and latest embeddings
- 🎨 Improved UI with tabbed interface
- 🔍 Advanced query filtering
- 📈 Query history and performance tracking
- 🐳 Docker Compose deployment
- 🔒 Enhanced security features

### **v1.0.0**
- 🎉 Initial release with basic RAG functionality
- 📄 Text document support
- 🔍 Basic semantic search
- 💬 Simple Q&A interface
