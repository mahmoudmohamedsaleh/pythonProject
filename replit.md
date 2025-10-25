# CRM and Presales Monitoring System

## Overview
This is a Flask-based CRM (Customer Relationship Management) and Presales Monitoring System designed for tracking projects, quotations, RFQs, and sales performance. The application provides comprehensive features for managing the entire sales pipeline from lead generation to project completion.

## Recent Changes
- **2025-10-25**: Initial Replit setup completed
  - Installed missing Python dependencies (xlsxwriter, openpyxl)
  - Fixed duplicate `if __name__ == '__main__'` blocks in app.py
  - Updated app.py to use environment variables (HOST, PORT, FLASK_DEBUG) for flexible configuration
  - Configured Flask to run on 0.0.0.0:5000 for Replit environment
  - Created symbolic link from Static to static directory
  - Initialized SQLite database
  - Configured deployment for autoscale mode
  - Created .gitignore for Python project

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

## CRITICAL SECURITY WARNINGS

⚠️ **This application has serious security vulnerabilities that must be addressed before production deployment:**

1. **Hard-coded Secret Key**: The Flask `app.secret_key` is set to 'your_secret_key' (line 47 in app.py), which is:
   - A literal string known to anyone with source access
   - Shared across all instances, allowing session forgery
   - **REQUIRED FIX**: Move to environment variable with a strong random value
   ```python
   app.secret_key = os.getenv('SECRET_KEY', os.urandom(24).hex())
   ```

2. **Plaintext Password Storage**: User passwords are stored in cleartext in SQLite:
   - Direct string comparison in login function (line 124)
   - Database breach would expose all passwords
   - **REQUIRED FIX**: Implement password hashing using werkzeug.security:
   ```python
   from werkzeug.security import generate_password_hash, check_password_hash
   ```

3. **Database Security**: SQLite database file contains sensitive data but is:
   - Not encrypted at rest
   - Accessible to anyone with file system access
   - **RECOMMENDED**: Migrate to PostgreSQL with proper access controls for production

## Known Issues
- Static folder case sensitivity resolved with symbolic link (should rename Static/ to static/ in source control)
- Some LSP warnings about imports (resolved at runtime)
