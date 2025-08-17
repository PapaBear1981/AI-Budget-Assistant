# API Contracts and Integration Specifications
## Personal AI Budget Assistant

**Version:** 1.0  
**Date:** 2025-08-17  
**Status:** Draft  

---

## Overview

This document defines the API contracts and integration specifications for the Personal AI Budget Assistant, including REST API endpoints, data schemas, error handling, and integration boundaries between system components.

## API Architecture

### Base Configuration
- **Base URL**: `https://api.budgetassistant.local`
- **API Version**: `v1`
- **Authentication**: JWT Bearer tokens
- **Content Type**: `application/json`
- **Rate Limiting**: 100 requests/minute per user

### Security Headers
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
X-API-Version: v1
X-Request-ID: <uuid>
X-Client-Version: <version>
```

## Core API Endpoints

### Authentication Endpoints

#### POST /auth/login
**Purpose**: User authentication with PIN/password

```json
// Request
{
  "pin": "string",
  "device_id": "string",
  "biometric_token": "string?" // Optional
}

// Response (200)
{
  "access_token": "string",
  "refresh_token": "string",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "preferences": {
      "theme": "dark|light",
      "currency": "USD",
      "locale": "en-US"
    }
  }
}

// Error Response (401)
{
  "error": "invalid_credentials",
  "message": "Invalid PIN or device not recognized",
  "retry_after": 30
}
```

#### POST /auth/refresh
**Purpose**: Refresh access token

```json
// Request
{
  "refresh_token": "string"
}

// Response (200)
{
  "access_token": "string",
  "expires_in": 3600
}
```

### AI Chat Endpoints

#### POST /ai/chat
**Purpose**: Send message to AI assistant

```json
// Request
{
  "message": "string",
  "conversation_id": "uuid?",
  "context": {
    "current_screen": "dashboard|transactions|budgets",
    "selected_data": "object?",
    "user_intent": "string?"
  },
  "options": {
    "voice_response": "boolean",
    "include_charts": "boolean",
    "response_format": "text|structured"
  }
}

// Response (200)
{
  "response": "string",
  "conversation_id": "uuid",
  "timestamp": "iso_datetime",
  "processing_info": {
    "response_time_ms": 2500,
    "confidence_score": 0.95,
    "modules_used": ["financial_analysis", "nlp_processing"],
    "data_sources": ["transactions", "budgets"]
  },
  "suggested_actions": [
    {
      "type": "view_chart",
      "label": "View spending chart",
      "action": "navigate",
      "target": "/charts/spending"
    }
  ],
  "voice_response": {
    "audio_url": "string?",
    "duration_seconds": 15
  }
}

// Error Response (400)
{
  "error": "invalid_input",
  "message": "Message contains potentially harmful content",
  "details": {
    "filtered_content": ["account_number"],
    "suggestions": ["Try asking about spending categories instead"]
  }
}
```

#### GET /ai/conversations
**Purpose**: Retrieve conversation history

```json
// Response (200)
{
  "conversations": [
    {
      "id": "uuid",
      "title": "Monthly spending analysis",
      "created_at": "iso_datetime",
      "updated_at": "iso_datetime",
      "message_count": 15,
      "last_message": "Your grocery spending increased by 15% this month"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 45,
    "has_next": true
  }
}
```

#### GET /ai/conversations/{conversation_id}/messages
**Purpose**: Retrieve messages from specific conversation

```json
// Response (200)
{
  "messages": [
    {
      "id": "uuid",
      "role": "user|assistant",
      "content": "string",
      "timestamp": "iso_datetime",
      "metadata": {
        "processing_time_ms": 2500,
        "confidence_score": 0.95,
        "voice_input": true
      }
    }
  ],
  "conversation": {
    "id": "uuid",
    "title": "string",
    "created_at": "iso_datetime"
  }
}
```

### Transaction Endpoints

#### GET /transactions
**Purpose**: Retrieve user transactions with filtering

```json
// Query Parameters
{
  "page": 1,
  "per_page": 50,
  "start_date": "2025-01-01",
  "end_date": "2025-01-31",
  "category": "groceries",
  "min_amount": 10.00,
  "max_amount": 500.00,
  "search": "walmart"
}

// Response (200)
{
  "transactions": [
    {
      "id": "uuid",
      "date": "2025-01-15",
      "amount": -45.67,
      "description": "WALMART SUPERCENTER",
      "category": {
        "id": "uuid",
        "name": "Groceries",
        "color": "#4CAF50"
      },
      "account": {
        "id": "uuid",
        "name": "Checking Account",
        "type": "checking"
      },
      "ai_categorized": true,
      "confidence_score": 0.92,
      "tags": ["essential", "recurring"]
    }
  ],
  "summary": {
    "total_amount": -1234.56,
    "transaction_count": 45,
    "categories": {
      "groceries": -567.89,
      "gas": -234.56,
      "entertainment": -123.45
    }
  },
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total": 245,
    "has_next": true
  }
}
```

#### POST /transactions
**Purpose**: Create new transaction

```json
// Request
{
  "date": "2025-01-15",
  "amount": -45.67,
  "description": "Coffee shop purchase",
  "category_id": "uuid?",
  "account_id": "uuid",
  "tags": ["coffee", "daily"],
  "notes": "Morning coffee with client"
}

// Response (201)
{
  "transaction": {
    "id": "uuid",
    "date": "2025-01-15",
    "amount": -45.67,
    "description": "Coffee shop purchase",
    "category": {
      "id": "uuid",
      "name": "Food & Dining",
      "color": "#FF9800"
    },
    "ai_suggestions": {
      "category_confidence": 0.88,
      "similar_transactions": 12,
      "suggested_tags": ["business", "networking"]
    }
  }
}
```

### Budget Endpoints

#### GET /budgets
**Purpose**: Retrieve user budgets

```json
// Response (200)
{
  "budgets": [
    {
      "id": "uuid",
      "name": "Monthly Budget - January 2025",
      "period": {
        "start_date": "2025-01-01",
        "end_date": "2025-01-31",
        "type": "monthly"
      },
      "categories": [
        {
          "category_id": "uuid",
          "category_name": "Groceries",
          "budgeted_amount": 500.00,
          "spent_amount": 387.45,
          "remaining_amount": 112.55,
          "percentage_used": 77.49,
          "status": "on_track|over_budget|under_budget"
        }
      ],
      "total_budgeted": 2500.00,
      "total_spent": 1876.34,
      "ai_insights": {
        "status": "on_track",
        "recommendations": [
          "Consider reducing dining out budget by $100",
          "You're saving well on transportation this month"
        ],
        "projected_end_balance": 234.56
      }
    }
  ]
}
```

### Data Import Endpoints

#### POST /import/upload
**Purpose**: Upload file for import processing

```json
// Request (multipart/form-data)
{
  "file": "binary_data",
  "file_type": "csv|xlsx|pdf",
  "account_id": "uuid",
  "import_options": {
    "date_format": "MM/DD/YYYY",
    "currency_symbol": "$",
    "skip_rows": 1,
    "auto_categorize": true
  }
}

// Response (202)
{
  "import_job": {
    "id": "uuid",
    "status": "processing",
    "file_name": "bank_statement.csv",
    "file_size": 1024000,
    "estimated_completion": "iso_datetime",
    "progress": {
      "stage": "parsing",
      "percentage": 25,
      "message": "Parsing CSV file..."
    }
  }
}
```

#### GET /import/jobs/{job_id}
**Purpose**: Check import job status

```json
// Response (200)
{
  "import_job": {
    "id": "uuid",
    "status": "completed|processing|failed",
    "progress": {
      "stage": "completed",
      "percentage": 100,
      "message": "Import completed successfully"
    },
    "results": {
      "total_rows": 150,
      "imported_transactions": 145,
      "skipped_rows": 3,
      "errors": 2,
      "ai_categorized": 132,
      "manual_review_needed": 13
    },
    "preview": [
      {
        "row": 1,
        "date": "2025-01-15",
        "description": "WALMART SUPERCENTER",
        "amount": -45.67,
        "suggested_category": "Groceries",
        "confidence": 0.92,
        "needs_review": false
      }
    ]
  }
}
```

## Error Handling

### Standard Error Response Format
```json
{
  "error": "error_code",
  "message": "Human-readable error message",
  "details": {
    "field": "specific_field_error",
    "validation_errors": ["list", "of", "errors"]
  },
  "request_id": "uuid",
  "timestamp": "iso_datetime",
  "suggestions": [
    "Try reducing the date range",
    "Check your internet connection"
  ]
}
```

### HTTP Status Codes
- **200**: Success
- **201**: Created
- **202**: Accepted (async processing)
- **400**: Bad Request (validation errors)
- **401**: Unauthorized (authentication required)
- **403**: Forbidden (insufficient permissions)
- **404**: Not Found
- **429**: Too Many Requests (rate limited)
- **500**: Internal Server Error
- **503**: Service Unavailable

### Error Codes
- `invalid_credentials`: Authentication failed
- `invalid_input`: Request validation failed
- `rate_limited`: Too many requests
- `ai_processing_error`: AI service unavailable
- `data_validation_error`: Data format issues
- `security_violation`: Security policy violation

## Data Schemas

### Common Types
```typescript
type UUID = string;
type ISODateTime = string;
type Currency = number; // Always in cents/smallest unit

interface PaginationRequest {
  page?: number;
  per_page?: number; // Max 100
}

interface PaginationResponse {
  page: number;
  per_page: number;
  total: number;
  has_next: boolean;
  has_previous: boolean;
}
```

### Transaction Schema
```typescript
interface Transaction {
  id: UUID;
  date: string; // YYYY-MM-DD
  amount: Currency; // Negative for expenses
  description: string;
  category: Category;
  account: Account;
  tags: string[];
  notes?: string;
  ai_categorized: boolean;
  confidence_score?: number;
  created_at: ISODateTime;
  updated_at: ISODateTime;
}

interface Category {
  id: UUID;
  name: string;
  color: string; // Hex color
  icon?: string;
  parent_id?: UUID;
  is_system: boolean;
}

interface Account {
  id: UUID;
  name: string;
  type: 'checking' | 'savings' | 'credit' | 'investment';
  balance?: Currency;
  currency: string; // ISO currency code
}
```

## Integration Boundaries

### Frontend ↔ Backend
- **Protocol**: HTTPS REST API
- **Authentication**: JWT tokens
- **Data Format**: JSON
- **Error Handling**: Standardized error responses
- **Rate Limiting**: Per-user limits

### Backend ↔ AI Services
- **Protocol**: HTTPS API calls
- **Authentication**: API keys
- **Data Format**: JSON
- **Security**: Input sanitization, output filtering
- **Fallback**: Local processing options

### Backend ↔ Database
- **Protocol**: SQLite direct connection
- **Security**: Database encryption (SQLCipher)
- **Transactions**: ACID compliance
- **Backup**: Encrypted backup files

## Performance Requirements

### Response Time Targets
- **Authentication**: < 1 second
- **Transaction CRUD**: < 2 seconds
- **AI Chat**: < 5 seconds
- **Data Import**: < 30 seconds (async)
- **Report Generation**: < 10 seconds

### Throughput Requirements
- **Concurrent Users**: 100 users
- **Requests per Second**: 50 RPS
- **Data Volume**: 100,000 transactions per user
- **File Upload**: 10MB maximum file size

### Availability Requirements
- **Uptime**: 99.5% availability
- **Recovery Time**: < 5 minutes
- **Backup Frequency**: Daily automated backups
- **Disaster Recovery**: 24-hour RTO

---

**Document Control:**
- **Author**: API Team
- **Reviewed By**: Security Team, Frontend Team
- **Approved By**: Technical Lead
- **Next Review**: 2025-09-17
