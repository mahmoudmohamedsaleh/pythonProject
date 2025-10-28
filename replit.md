# CRM and Presales Monitoring System

## Overview
This is a Flask-based CRM (Customer Relationship Management) and Presales Monitoring System designed for tracking projects, quotations, RFQs, and sales performance. The application provides comprehensive features for managing the entire sales pipeline from lead generation to project completion.

## Recent Changes
- **2025-10-28**: Vendor routes fixed to work with production database schema
  - Fixed vendor management routes to use `vendors` table instead of `srm_vendors`
  - Updated column mappings to match production schema (phone/email vs main_phone/main_email)
  - Disabled vendor contacts feature (not present in production database)
  - Added PO comment system with modal UI and backend routes
  - Fixed navigation highlighting bug in sidebar
  
- **2025-10-25**: Initial Replit setup completed
  - Installed missing Python dependencies (xlsxwriter, openpyxl)
  - Fixed duplicate `if __name__ == '__main__'` blocks in app.py
  - Updated app.py to use environment variables (HOST, PORT, FLASK_DEBUG) for flexible configuration
  - Configured Flask to run on 0.0.0.0:5000 for Replit environment
  - Created symbolic link from Static to static directory
  - Initialized SQLite database
  - Configured deployment for autoscale mode
  - Created .gitignore for Python project
  - **Production Database Integrated**: Replaced with user-provided database (48MB, 22 users, 126 projects, 24 tables)

## Technology Stack
- **Backend**: Flask (Python web framework)
- **Database**: SQLite3
- **Data Processing**: Pandas, openpyxl, xlsxwriter
- **PDF Generation**: ReportLab
- **Frontend**: HTML templates with Jinja2

## Project Architecture

### Key Features
1. **User Authentication & Authorization**
   - Role-based access control (General Manager, Technical Team Leader, Presale Engineer, Sales Engineer, etc.)
   - Login/logout functionality
   - Session management

2. **Project Management**
   - Project registration and tracking
   - Quotation submission and management
   - Project history and status updates
   - Multiple project stages (Lead, Proposal Prep, Proposal Sent, etc.)

3. **CRM Features**
   - Customer relationship tracking
   - Vendor management with contacts
   - Distributor, contractor, consultant, and end-user management
   - Technical support request tracking

4. **Sales & Presales Tools**
   - RFQ (Request for Quotation) management
   - Quotation builder
   - Solution builder (Fiber, Passive, etc.)
   - Cost sheet management

5. **Analytics & Reporting**
   - Sales performance dashboard
   - Presales performance metrics
   - Pipeline analysis
   - Aging dashboard
   - Project summary with filtering

6. **Document Management**
   - File upload/download for quotations and cost sheets
   - Document storage in database (BLOB)
   - Excel export functionality

7. **Product Catalog**
   - Fire alarm products (Detectors, Manual Call Points)
   - CCTV products
   - Passive products

### Database Structure
The application uses SQLite with multiple tables including:
- `users`: User authentication and roles
- `projects`: Project and quotation data
- `register_project`: Project pipeline tracking
- `engineers`: Engineer registration and details
- `rfq_requests`: RFQ tracking
- `vendors`, `distributors`, `contractors`, `consultants`, `end_users`: CRM entities
- `tasks`: Task management system

### Directory Structure
- `app.py`: Main Flask application (5066 lines)
- `templates/`: HTML templates
- `Static/` (symlinked as `static/`): Static assets (images, CSS, JS)
- `uploads/`: User-uploaded files (cost sheets, documents)
- `ProjectStatus.db`: SQLite database

## Configuration

### Development
- Host: 0.0.0.0 (configurable via HOST environment variable)
- Port: 5000 (configurable via PORT environment variable)
- Debug mode: Controlled by FLASK_DEBUG environment variable (1=enabled, 0=disabled)

### Deployment
- Target: Autoscale (stateless)
- Command: `python3 app.py`
- The application respects Replit's PORT environment variable for proper deployment

## User Preferences
(None specified yet)

## Security Improvements

✅ **The following security improvements have been implemented:**

1. **Secret Key Security** (FIXED):
   - Changed from hard-coded 'your_secret_key' to environment-based configuration
   - Implementation: `app.secret_key = os.getenv('SECRET_KEY', os.urandom(24).hex())`
   - Uses random generation as fallback if SECRET_KEY environment variable not set
   - For production deployment, set a strong SECRET_KEY environment variable

2. **Password Hashing** (FIXED):
   - Implemented werkzeug.security password hashing throughout the application
   - New passwords are hashed using `generate_password_hash()` before storage
   - Login verification uses `check_password_hash()` for secure comparison
   - **Password Migration**: Automatic upgrade system for existing plaintext passwords
     - Legacy plaintext passwords are detected and validated on login
     - Upon successful login, plaintext passwords are automatically upgraded to hashed format
     - Both users and engineers tables are updated simultaneously
     - No user intervention required - migration happens transparently

3. **Database Security** (PARTIAL):
   - SQLite database file still not encrypted at rest
   - **RECOMMENDED for Production**: Migrate to Replit PostgreSQL with proper access controls
   - Contact information stored in database should be considered sensitive

## Technical Notes
- Static folder case sensitivity resolved with symbolic link (Static -> static)
- All database tables properly initialized with complete schema
- Password migration system handles legacy accounts automatically
- LSP diagnostics about imports are cosmetic (all imports resolve correctly at runtime)
