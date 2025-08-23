# Overview

This is a Flask-based cost accumulation system for product pricing management called "Akumulasi Harga Produk". The application allows users to track and calculate the total cost of products by managing three types of costs: material costs, service costs, and maintenance costs. It provides a web interface for creating products and adding various cost components to calculate comprehensive product pricing.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Architecture
- **Framework**: Flask web framework with SQLAlchemy ORM for database operations
- **Database**: SQLite dengan SQLAlchemy models for data persistence
- **Application Structure**: Modular design with separate files for models, routes, and application configuration
- **Session Management**: Flask sessions with configurable secret key for security

## Database Design
- **Product Model**: Central entity storing product information with name, description, and timestamps
- **Cost Models**: Three separate cost types (MaterialCost, ServiceCost, MaintenanceCost) linked to products via foreign keys
- **Relationships**: One-to-many relationships between products and their associated costs with cascade delete
- **Computed Properties**: Dynamic cost calculations using SQLAlchemy aggregate functions

## Frontend Architecture
- **Template Engine**: Jinja2 templating with Bootstrap 5 dark theme
- **UI Components**: Responsive card-based layout with navigation breadcrumbs
- **Styling**: Custom CSS with CSS variables for consistent theming and hover effects
- **Icons**: Font Awesome integration for visual elements

## Cost Calculation System
- **Aggregation Logic**: Automatic calculation of total costs by summing all cost types per product
- **Unit Cost Calculation**: Built-in method to calculate cost per unit for pricing analysis
- **Real-time Updates**: Dynamic cost recalculation when cost components are modified

# External Dependencies

## Frontend Dependencies
- **Bootstrap 5**: CSS framework with dark theme variant from Replit CDN
- **Font Awesome 6.4.0**: Icon library for UI elements

## Backend Dependencies
- **Flask**: Web framework for routing and request handling
- **Flask-SQLAlchemy**: Database ORM integration
- **Werkzeug**: WSGI utilities including ProxyFix middleware for reverse proxy compatibility

## Database
- **SQLite**: Primary database system untuk local storage yang ringan
- **SQLAlchemy**: Database abstraction layer with automatic table creation and migration support
- **File Database**: Database disimpan sebagai file akumulasi_harga.db

## Environment Configuration
- **DATABASE_URL**: Environment variable for database connection string
- **SESSION_SECRET**: Environment variable for Flask session security
- **Debug Mode**: Development configuration with debug logging enabled