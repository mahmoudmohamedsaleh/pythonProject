# CRM and Presales Monitoring System

## Overview
This is a Flask-based CRM (Customer Relationship Management) and Presales Monitoring System designed for tracking projects, quotations, RFQs, and sales performance. The application provides comprehensive features for managing the entire sales pipeline from lead generation to project completion.

## Recent Changes
- **2025-10-29**: Admin-Assisted Password Reset System (Complete Implementation)
  
  **Manual OTP Distribution Dashboard** ⭐ RECOMMENDED WORKFLOW
  - Complete admin-assisted password reset system (workaround until domain verified)
  - Three-step user workflow: Request Reset → Contact Admin → Verify OTP → Set New Password
  - **Admin OTP Dashboard**: New route `/pending_otp_requests` for General Manager and Technical Team Leader
  - Dashboard shows all active password reset requests with:
    * Username and role of requester
    * Email address (if available)
    * **OTP code displayed prominently** (large blue box, copyable)
    * Created timestamp and expiration time
    * Request status (pending/used/expired)
  - Admins can copy OTP codes and share via phone, WhatsApp, or in-person
  - **User workflow updated**: Forgot password page now instructs users to contact admin for OTP
  - No email sending required - perfect for test environment without verified domain
  - Automatic OTP expiration after 15 minutes
  - One-time use validation prevents OTP reuse
  - New menu item: "Password Reset OTPs" in Administration section
  - Multi-source email lookup: users, registration_requests, engineers tables
  
- **2025-10-29**: Password Reset System (Two Methods)
  
  **Method 1: OTP via Email** (requires domain verification)
  - Complete password reset workflow using One-Time Password (OTP)
  - Three-step process: Request Reset → Verify OTP → Set New Password
  - OTP sent via email with 15-minute expiration
  - Secure OTP generation using Python secrets module
  - Email support for multiple providers (Gmail, SendGrid, Resend, generic SMTP)
  - Configuration via environment variables (EMAIL_PROVIDER, RESEND_API_KEY, SENDER_EMAIL)
  - New database table: `password_reset_tokens` (stores OTP with expiration)
  - New routes: `/forgot_password`, `/verify_otp`, `/reset_password_with_otp`, `/resend_otp`
  - HTML email templates with professional design
  - Fallback to console output if email not configured (for testing)
  - Resend API integration with proper error handling
  - **Email Column Added to Users Table**: All users can now have email addresses
  - **Multi-source Email Lookup**: Checks users table, registration_requests, and engineers table
  - **Note**: Resend requires domain verification to send to all users (test mode limited to verified email)
  
  **Method 2: Admin Password Reset** (no email required) ⭐ RECOMMENDED
  - **New Feature (2025-10-29)**: Direct admin password reset without email
  - Accessible by General Manager and Technical Team Leader roles
  - New route: `/admin_reset_password/<user_id>`
  - Admin can reset any user's password instantly
  - No email verification required - perfect for users without email
  - Password immediately encrypted using werkzeug.security
  - Updates both users and engineers tables simultaneously
  - Yellow "Reset Password" button (🔑 icon) in user management table
  - Confirmation dialog before resetting password
  - Flash message confirms successful password reset
  - **Use this method until domain is verified for Resend!**
  
- **2025-10-29**: Public Registration with Admin Approval System
  - Created public registration page at `/register` (no login required)
  - Users can request account access by filling out registration form
  - All passwords encrypted immediately upon registration
  - Admin approval workflow: pending → approved/rejected
  - General Manager and Technical Team Leader can review, approve, or reject registration requests
  - New database table: `registration_requests` (tracks all registration requests)
  - Admin panel: `/pending_registrations` (shows pending and reviewed requests)
  - Email and reason fields for better user tracking
  - Automatic account activation upon approval
  - Updated login page with "Request Account Access" link
  - Added "Pending Registrations" to Administration menu
  - Role-based access: Both General Manager and Technical Team Leader have full admin access
  
- **2025-10-28**: User Management System added with password encryption
  - Created admin panel for General Managers and Technical Team Leaders to manage user accounts
  - Add/Edit/Delete users with industry-standard password encryption (werkzeug.security)
  - Password validation (minimum 6 characters, confirmation matching)
  - Secure password hashing using `generate_password_hash()` and `check_password_hash()`
  - Role-based access control (General Manager and Technical Team Leader can access user management)
  - All passwords stored encrypted in database - never in plaintext
  - New routes: `/manage_users`, `/add_user`, `/edit_user`, `/delete_user`, `/admin_reset_password/<user_id>`
  - Added "Administration" menu in sidebar (visible to General Manager and Technical Team Leader)
  - **Admin Password Reset**: Three-button interface (Edit, Reset Password, Delete) for each user
  - Email field added to Add/Edit user forms with password reset reminder
  
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
- **Email Provider**: Resend (configured with API key, not using Replit integration)
- **Note**: User declined Replit's Resend integration, using manual secret configuration instead

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
