# Overview

This is a Flask-based invoice management system specifically designed for FJ Service Center, a computer, laptop, and mobile phone repair service business in Indonesia. The system enables staff to create, manage, and track service invoices with features like PDF generation, customer data management, and basic reporting. The application is built with SQLite database storage using Flask-SQLAlchemy and focuses on Indonesian business requirements with Rupiah currency formatting and Indonesian language interface.

# User Preferences

Preferred communication style: Simple, everyday language.
Chrome auto-launch: One-time full screen mode launch requested
Port configuration: Application runs on port 5001 (not default 5000)
Invoice format: 10 rows instead of 20 rows in tables

# System Architecture

## Frontend Architecture
The system uses a traditional server-rendered architecture with Flask templates and Bootstrap 5 for responsive UI. The frontend consists of:
- **Template Engine**: Jinja2 templates with a base layout pattern for consistent navigation and styling
- **UI Framework**: Bootstrap 5 with Font Awesome icons for a professional Indonesian business appearance
- **Client-Side Logic**: Vanilla JavaScript for form validation, dynamic service item management, currency formatting, and search functionality
- **Styling**: Custom CSS with Indonesian business color scheme and professional layout

## Backend Architecture
Built on Flask with a simple MVC-like pattern:
- **Application Layer**: Flask app with route handlers in `routes.py` managing HTTP requests and responses
- **Business Logic**: `InvoiceManager` class in `models.py` handling all invoice operations and data validation
- **PDF Generation**: ReportLab-based system in `pdf_generator.py` for creating professional invoice PDFs
- **Session Management**: Flask sessions with configurable secret key for flash messages and user feedback

## Data Storage Solution
Uses SQLite database with Flask-SQLAlchemy ORM:
- **Database**: SQLite (`invoices.db`) with proper relational structure
- **Models**: Invoice and ServiceItem models with proper relationships
- **ORM**: Flask-SQLAlchemy for database operations and migrations
- **Rationale**: Reliable, ACID-compliant storage with better concurrent access and data integrity
- **Benefits**: Proper foreign key constraints, better query performance, and easier data management

## Key Features
- **Invoice Management**: Complete CRUD operations for service invoices with automatic ID generation
- **Customer Tracking**: Basic customer information storage with phone and name tracking
- **Service Items**: Flexible line items for different repair services with quantity and pricing
- **Financial Calculations**: Automatic subtotal, discount, and total calculations with Rupiah formatting
- **PDF Export**: Professional invoice PDF generation matching Indonesian business standards
- **Search and Filter**: Basic search functionality for invoice retrieval by customer information
- **Dashboard**: Simple analytics showing total invoices and revenue

# External Dependencies

## Python Packages
- **Flask**: Web framework for application structure and routing
- **Flask-SQLAlchemy**: SQLAlchemy ORM integration for database operations
- **Werkzeug**: WSGI utilities including ProxyFix for deployment behind reverse proxies
- **ReportLab**: PDF generation library for creating professional invoice documents

## Frontend Libraries
- **Bootstrap 5**: CSS framework delivered via CDN for responsive design and components
- **Font Awesome 6**: Icon library via CDN for professional UI elements

## Database Dependencies
- **SQLite Database**: Local database file (`invoices.db`) for data persistence
- **PDF Generation**: Temporary file handling for PDF creation and download
- **Static Assets**: CSS and JavaScript files served from Flask static directory

## Runtime Environment
- **Python 3.x**: Required for Flask and ReportLab functionality
- **File System Access**: Requires read/write permissions for data directory and temporary file creation
- **Network Access**: CDN access for Bootstrap and Font Awesome resources (fallback handling not implemented)