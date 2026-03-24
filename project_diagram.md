# MarketingOptix Project Diagram

This document provides a visual overview of the MarketingOptix project architecture, database schema, and core user flows.

## 1. System Architecture

The following diagram illustrates the high-level architecture of the Django-based application.

```mermaid
graph TD
    User((User/Browser))
    
    subgraph "Frontend Layer"
        UI[Bootstrap 5 + Custom CSS]
        ThreeJS[Three.js 3D Animation Engine]
        AOS[AOS - Animate On Scroll]
    end
    
    subgraph "Backend Layer (Django)"
        URL[URL Dispatcher]
        View[Views.py - Business Logic]
        CP[Context Processors - Global Data]
        Template[Django Template Engine]
    end
    
    subgraph "Data Layer"
        DB[(SQLite Database)]
        Media[Media Storage - Profile Pics, PDFs]
    end
    
    User <--> UI
    UI <--> URL
    URL --> View
    View <--> DB
    View <--> Media
    View --> Template
    CP --> Template
    Template --> UI
    ThreeJS --> UI
```

## 2. Entity Relationship (ER) Diagram

This diagram shows the relationships between the core database models in the `user` app.

```mermaid
erDiagram
    STATE ||--o{ CITY : "contains"
    CITY ||--o{ USER : "location for"
    CATEGORY ||--o{ SERVICE : "groups"
    
    USER ||--o{ PROJECT : "posts"
    USER ||--o{ QUOTATION : "submits"
    USER ||--o{ REVIEW : "receives/gives"
    USER ||--o{ MESSAGE : "sends/receives"
    USER ||--o{ NOTIFICATION : "receives"
    USER ||--o{ USER_LANGUAGE : "speaks"
    USER ||--o{ USER_IMAGE : "portfolio"
    USER ||--o{ SAVED_PROJECT : "saves"

    PROJECT ||--o{ PROJECT_SERVICE : "requires"
    SERVICE ||--o{ PROJECT_SERVICE : "linked to"
    PROJECT ||--o{ QUOTATION : "has"
    PROJECT ||--o{ REVIEW : "reviewed in"
    PROJECT ||--o{ SAVED_PROJECT : "saved as"

    USER {
        int userid PK
        string username
        string email
        string role
        string bio
    }
    PROJECT {
        int projectid PK
        string title
        float budget
        int status
    }
    QUOTATION {
        int quotationid PK
        float budget
        string status
    }
```

## 3. Core User Flow (Hiring Process)

The sequence below illustrates the typical interaction between a Client and a Marketer.

```mermaid
sequenceDiagram
    participant Client
    participant System
    participant Marketer

    Client->>System: Post Project (with Budget & Services)
    System-->>Marketer: Notification: New Project Available
    Marketer->>System: Submit Quotation (PDF + Bid)
    System-->>Client: Notification: New Quotation Received
    Client->>System: Review Quotation & Accept
    System->>Project: Update Status to In-Progress
    System-->>Marketer: Notification: Hired!
    Marketer->>Client: Send Message (Chat System)
    Client->>System: Complete Project & Pay
    System->>Project: Update Status to Completed
    Client->>System: Leave Review & Rating
    System->>Marketer: Update Rating Profile
```
