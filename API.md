# SmartLearn Hub - API Documentation

## Overview

RESTful API built with Django REST Framework for the SmartLearn Hub platform.

- **Base URL**: `https://api.smartlearn.com/api/v1/`
- **Authentication**: Session-based (cookie) for web, Token for API clients
- **Format**: JSON
- **Versioning**: URL path (`/api/v1/`)

---

## Authentication

### Login

```http
POST /api/v1/auth/login/
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "securepassword"
}
```

**Response (200)**:
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "is_staff": false
  },
  "session_id": "abc123..."
}
```

### Register

```http
POST /api/v1/auth/register/
Content-Type: application/json

{
  "email": "newuser@example.com",
  "username": "newuser",
  "password": "securepassword123",
  "password_confirm": "securepassword123",
  "first_name": "Jane",
  "last_name": "Smith"
}
```

### Logout

```http
POST /api/v1/auth/logout/
```

### Password Reset

```http
POST /api/v1/auth/password/reset/
Content-Type: application/json

{
  "email": "user@example.com"
}
```

```http
POST /api/v1/auth/password/reset/confirm/
Content-Type: application/json

{
  "uid": "base64-encoded-uid",
  "token": "reset-token",
  "new_password": "newsecurepassword123",
  "new_password_confirm": "newsecurepassword123"
}
```

---

## Courses API

### List Courses

```http
GET /api/v1/courses/
```

**Query Parameters**:
- `page` (int): Page number (default: 1)
- `page_size` (int): Results per page (default: 20, max: 100)
- `search` (string): Search in title, description
- `category` (string): Filter by category slug
- `difficulty` (string): Filter by difficulty (beginner, intermediate, advanced)
- `ordering` (string): Sort field (-created_at, title, -enrollment_count)

**Response (200)**:
```json
{
  "count": 150,
  "next": "https://api.smartlearn.com/api/v1/courses/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Introduction to Python",
      "slug": "introduction-to-python",
      "description": "Learn Python basics...",
      "short_description": "Python fundamentals for beginners",
      "thumbnail": "https://cdn.smartlearn.com/media/courses/python-thumb.jpg",
      "category": {
        "id": 1,
        "name": "Programming",
        "slug": "programming"
      },
      "difficulty": "beginner",
      "duration_hours": 10,
      "lesson_count": 25,
      "enrollment_count": 1250,
      "rating": 4.8,
      "instructor": {
        "id": 5,
        "username": "python_expert",
        "full_name": "Jane Python"
      },
      "price": "0.00",
      "is_free": true,
      "tags": ["python", "beginner", "programming"],
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-20T15:30:00Z"
    }
  ]
}
```

### Get Course Detail

```http
GET /api/v1/courses/{slug}/
```

**Response (200)**:
```json
{
  "id": 1,
  "title": "Introduction to Python",
  "slug": "introduction-to-python",
  "description": "<p>Full course description...</p>",
  "short_description": "Python fundamentals for beginners",
  "thumbnail": "https://cdn.smartlearn.com/media/courses/python-thumb.jpg",
  "category": {
    "id": 1,
    "name": "Programming",
    "slug": "programming",
    "description": "Programming courses"
  },
  "difficulty": "beginner",
  "duration_hours": 10,
  "lesson_count": 25,
  "enrollment_count": 1250,
  "rating": 4.8,
  "instructor": {
    "id": 5,
    "username": "python_expert",
    "full_name": "Jane Python",
    "bio": "Senior Python Developer...",
    "avatar": "https://cdn.smartlearn.com/media/avatars/jane.jpg"
  },
  "price": "0.00",
  "is_free": true,
  "tags": ["python", "beginner", "programming"],
  "prerequisites": ["Basic computer skills"],
  "learning_outcomes": [
    "Understand Python syntax",
    "Write basic programs",
    "Work with data structures"
  ],
  "modules": [
    {
      "id": 1,
      "title": "Getting Started",
      "order": 1,
      "lessons": [
        {
          "id": 1,
          "title": "What is Python?",
          "order": 1,
          "duration_minutes": 15,
          "type": "video",
          "is_preview": true
        }
      ]
    }
  ],
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-20T15:30:00Z"
}
```

### Enroll in Course

```http
POST /api/v1/courses/{slug}/enroll/
```

**Response (201)**:
```json
{
  "enrollment": {
    "id": 42,
    "course": 1,
    "user": 1,
    "enrolled_at": "2024-01-25T10:00:00Z",
    "progress": 0,
    "completed_lessons": 0,
    "total_lessons": 25
  }
}
```

### Get Course Progress

```http
GET /api/v1/courses/{slug}/progress/
```

**Response (200)**:
```json
{
  "enrollment_id": 42,
  "progress_percentage": 45.5,
  "completed_lessons": 11,
  "total_lessons": 25,
  "current_lesson": {
    "id": 12,
    "title": "Working with Lists",
    "module": "Data Structures"
  },
  "last_accessed": "2024-01-24T15:30:00Z",
  "completed_at": null
}
```

### Submit Lesson Completion

```http
POST /api/v1/courses/{slug}/lessons/{lesson_id}/complete/
```

**Response (200)**:
```json
{
  "lesson_id": 12,
  "completed": true,
  "completed_at": "2024-01-25T10:15:00Z",
  "new_progress": 48.0,
  "next_lesson": {
    "id": 13,
    "title": "List Methods",
    "module": "Data Structures"
  }
}
```

---

## Notes API

### List Notes

```http
GET /api/v1/notes/
```

**Query Parameters**:
- `course` (int): Filter by course ID
- `search` (string): Search in title, content
- `tags` (string): Comma-separated tag IDs
- `is_public` (bool): Filter public/private
- `ordering` (string): -created_at, updated_at, title

**Response (200)**:
```json
{
  "count": 25,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Python List Comprehension",
      "content": "# List Comprehension\n\n[expr for item in iterable if condition]",
      "course": {
        "id": 1,
        "title": "Introduction to Python"
      },
      "tags": [
        {"id": 1, "name": "python", "color": "#3776AB"},
        {"id": 3, "name": "syntax", "color": "#FFD43B"}
      ],
      "is_public": false,
      "word_count": 150,
      "created_at": "2024-01-20T10:00:00Z",
      "updated_at": "2024-01-22T14:30:00Z"
    }
  ]
}
```

### Create Note

```http
POST /api/v1/notes/
Content-Type: application/json

{
  "title": "My Python Notes",
  "content": "# Variables\n\nx = 5\nname = \"John\"",
  "course": 1,
  "tags": [1, 3],
  "is_public": false
}
```

### Get Note

```http
GET /api/v1/notes/{id}/
```

### Update Note

```http
PATCH /api/v1/notes/{id}/
Content-Type: application/json

{
  "title": "Updated Title",
  "content": "Updated content..."
}
```

### Delete Note

```http
DELETE /api/v1/notes/{id}/
```

---

## Analytics API

### User Dashboard

```http
GET /api/v1/analytics/dashboard/
```

**Response (200)**:
```json
{
  "overview": {
    "total_courses_enrolled": 5,
    "courses_completed": 2,
    "total_study_hours": 45.5,
    "current_streak_days": 7,
    "longest_streak_days": 14,
    "notes_created": 23,
    "ai_questions_asked": 45
  },
  "progress_by_course": [
    {
      "course_id": 1,
      "course_title": "Introduction to Python",
      "progress_percentage": 80.0,
      "lessons_completed": 20,
      "total_lessons": 25,
      "last_accessed": "2024-01-24T15:30:00Z"
    }
  ],
  "weekly_activity": [
    {"date": "2024-01-15", "study_minutes": 120},
    {"date": "2024-01-16", "study_minutes": 90},
    {"date": "2024-01-17", "study_minutes": 60},
    {"date": "2024-01-18", "study_minutes": 0},
    {"date": "2024-01-19", "study_minutes": 150},
    {"date": "2024-01-20", "study_minutes": 90},
    {"date": "2024-01-21", "study_minutes": 60}
  ],
  "recent_achievements": [
    {
      "id": 1,
      "title": "Week Warrior",
      "description": "Studied 7 days in a row",
      "icon": "🏆",
      "earned_at": "2024-01-21T00:00:00Z"
    }
  ]
}
```

### Course Analytics (Instructor)

```http
GET /api/v1/analytics/courses/{course_id}/
```

**Response (200)**:
```json
{
  "course_id": 1,
  "enrollment_stats": {
    "total_enrollments": 1250,
    "active_learners": 890,
    "completed": 420,
    "dropped_off": 340,
    "completion_rate": 33.6
  },
  "engagement": {
    "avg_study_time_hours": 8.5,
    "avg_lessons_per_session": 3.2,
    "most_engaging_module": "Data Structures",
    "least_engaging_module": "Advanced Topics"
  },
  "ratings": {
    "average": 4.8,
    "distribution": {"5": 850, "4": 300, "3": 80, "2": 15, "1": 5},
    "total_reviews": 1250
  },
  "revenue": {
    "total": 0,
    "currency": "USD"
  }
}
```

---

## AI Assistant API

### Ask Question

```http
POST /api/v1/ai/ask/
Content-Type: application/json

{
  "question": "How do I use list comprehension in Python?",
  "context": {
    "course_id": 1,
    "lesson_id": 12
  }
}
```

**Response (200)**:
```json
{
  "answer": "List comprehension provides a concise way to create lists...\n\n```python\n# Basic syntax\n[expression for item in iterable if condition]\n\n# Examples\nsquares = [x**2 for x in range(10)]\nevens = [x for x in range(10) if x % 2 == 0]\n```",
  "sources": [
    {
      "type": "course_content",
      "title": "Working with Lists",
      "url": "/courses/introduction-to-python/lessons/12/"
    }
  ],
  "tokens_used": 150,
  "cost_usd": 0.0003
}
```

### Generate Explanation

```http
POST /api/v1/ai/explain/
Content-Type: application/json

{
  "topic": "Python decorators",
  "level": "intermediate",
  "context": "web development"
}
```

### Generate Quiz

```http
POST /api/v1/ai/quiz/
Content-Type: application/json

{
  "course_id": 1,
  "module_id": 3,
  "num_questions": 5,
  "difficulty": "medium"
}
```

---

## Collaboration API

### Study Groups

```http
GET /api/v1/groups/
POST /api/v1/groups/
GET /api/v1/groups/{id}/
PATCH /api/v1/groups/{id}/
DELETE /api/v1/groups/{id}/
POST /api/v1/groups/{id}/join/
POST /api/v1/groups/{id}/leave/
GET /api/v1/groups/{id}/members/
```

### Group Resources

```http
GET /api/v1/groups/{id}/resources/
POST /api/v1/groups/{id}/resources/
GET /api/v1/groups/{id}/resources/{resource_id}/
DELETE /api/v1/groups/{id}/resources/{resource_id}/
```

### Assignments

```http
GET /api/v1/groups/{id}/assignments/
POST /api/v1/groups/{id}/assignments/
GET /api/v1/groups/{id}/assignments/{assignment_id}/
POST /api/v1/groups/{id}/assignments/{assignment_id}/submit/
GET /api/v1/groups/{id}/assignments/{assignment_id}/submissions/
```

---

## WebSocket API

### Connection

```javascript
const ws = new WebSocket('wss://api.smartlearn.com/ws/notifications/');
ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'auth',
    token: 'your-session-token'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

### Message Types

**Server → Client**:
```json
{
  "type": "notification",
  "payload": {
    "id": 123,
    "title": "New Assignment",
    "message": "You have a new assignment in Python Course",
    "url": "/groups/1/assignments/5/",
    "created_at": "2024-01-25T10:00:00Z"
  }
}
```

```json
{
  "type": "collaboration_update",
  "payload": {
    "room": "note_42",
    "user": "johndoe",
    "action": "edit",
    "content": "Updated note content..."
  }
}
```

**Client → Server**:
```json
{
  "type": "subscribe",
  "channels": ["notifications", "group_1", "note_42"]
}
```

```json
{
  "type": "ping"
}
```

---

## Error Responses

### Standard Error Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "email": ["This field is required."],
      "password": ["This password is too short."]
    }
  }
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 405 | Method Not Allowed |
| 429 | Too Many Requests (rate limited) |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

### Error Codes

| Code | Description |
|------|-------------|
| VALIDATION_ERROR | Request data validation failed |
| AUTHENTICATION_FAILED | Invalid credentials |
| PERMISSION_DENIED | Insufficient permissions |
| NOT_FOUND | Resource not found |
| RATE_LIMITED | Too many requests |
| AI_QUOTA_EXCEEDED | OpenAI API quota exceeded |
| INTERNAL_ERROR | Unexpected server error |

---

## Rate Limiting

| Endpoint Type | Limit |
|---------------|-------|
| Authentication | 5 requests/minute |
| API (authenticated) | 100 requests/minute |
| API (anonymous) | 20 requests/minute |
| AI Assistant | 10 requests/minute |
| File Upload | 10 requests/minute |

Headers returned:
- `X-RateLimit-Limit`: Request limit
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Unix timestamp when limit resets

---

## Pagination

All list endpoints use cursor-based pagination:

```json
{
  "count": 150,
  "next": "https://api.smartlearn.com/api/v1/courses/?cursor=cD0yMDI0LTAxLTE1",
  "previous": null,
  "results": [...]
}
```

Query parameters:
- `cursor`: Pagination cursor (opaque string)
- `page_size`: Results per page (default 20, max 100)

---

## Filtering & Search

Common query parameters:

| Parameter | Description |
|-----------|-------------|
| `search` | Full-text search across relevant fields |
| `ordering` | Sort field (prefix with `-` for descending) |
| `page_size` | Results per page |
| `cursor` | Pagination cursor |

---

## Versioning

API version is in the URL path: `/api/v1/`

Breaking changes will result in a new version (`/api/v2/`).
Current version will be supported for at least 12 months after new version release.

---

## SDKs & Client Libraries

### JavaScript/TypeScript

```bash
npm install @smartlearn/api-client
```

```typescript
import { SmartLearnClient } from '@smartlearn/api-client';

const client = new SmartLearnClient({
  baseUrl: 'https://api.smartlearn.com/api/v1',
  // For browser: cookies handled automatically
  // For Node: provide session cookie or token
});

// Get courses
const courses = await client.courses.list({ page_size: 10 });

// Ask AI
const answer = await client.ai.ask({
  question: 'How do decorators work in Python?',
  context: { course_id: 1 }
});
```

### Python

```bash
pip install smartlearn-python
```

```python
from smartlearn import SmartLearnClient

client = SmartLearnClient(
    base_url='https://api.smartlearn.com/api/v1',
    session_cookie='sessionid=...'  # or token
)

# Get courses
courses = client.courses.list(page_size=10)

# Create note
note = client.notes.create(
    title="My Notes",
    content="# Hello World",
    course_id=1
)
```

---

## OpenAPI/Swagger Documentation

Interactive API documentation available at:
- **Swagger UI**: `https://api.smartlearn.com/api/docs/`
- **ReDoc**: `https://api.smartlearn.com/api/redoc/`
- **OpenAPI Schema**: `https://api.smartlearn.com/api/schema/`

Generated with `drf-spectacular`.