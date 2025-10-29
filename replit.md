# CRM and Presales Monitoring System

## Overview
This Flask-based CRM and Presales Monitoring System tracks projects, quotations, RFQs, and sales performance, managing the entire sales pipeline from lead generation to project completion. It provides comprehensive features for user authentication, project and customer relationship management, sales and presales tools, and analytics. The system supports a public registration process with admin approval and integrates robust password security, including an admin-assisted password reset mechanism.

## Recent Updates (2025-10-29)

### Database Merge ✅
- Successfully imported 3 new records from production database
- New contractor: Talha Gulf (ID 52)
- New project: Al hammadi (ID 130) - ACT system, quotation sent
- New registered project: Talha Gulf (ID 105) - Proposal prep stage, 50K deal value
- All existing security features preserved (permissions, password tokens, comments)
- Automatic backups created before merge
- Total records: 52 contractors, 130 projects, 105 registered projects

### RFQ Comments System ✅
- Complete comments/history functionality added to RFQ module (matching PO comments)
- New database table: `rfq_comments` with full audit trail
- New routes: `/add_rfq_comment/<rfq_id>`, `/get_rfq_comments/<rfq_id>`
- Comments button added to RFQ Summary actions column
- Professional modal with comment history and add comment sections
- AJAX-based real-time comment loading
- User attribution and timestamps for all comments

### Password Migration & Security ✅
- All 41 passwords encrypted with scrypt:32768:8:1 hashing
- Migration script created: `migrate_passwords.py`
- Automatic password upgrade on login for legacy accounts
- Database ready for PythonAnywhere deployment

### Complete Route Protection ✅
- All 130 protected routes secured with @login_required or @permission_required
- 7 public routes (login, register, password reset flows)
- 0 unprotected routes - 100% secure

## User Preferences
- **Email Provider**: Resend (configured with API key, not using Replit integration)
- **Note**: User declined Replit's Resend integration, using manual secret configuration instead

## System Architecture

### UI/UX Decisions
The system features a comprehensive admin access control UI at `/access_control` for managing granular page-level permissions. It also includes an admin OTP Dashboard at `/pending_otp_requests` for assisting with password resets without email. The UI provides real-time permission updates via AJAX and visual indicators for permission sources. Dynamic UI elements are supported through `user_has_permission()` in templates.

### Technical Implementations
- **Backend**: Flask (Python web framework)
- **Database**: SQLite3
- **Data Processing**: Pandas, openpyxl, xlsxwriter
- **PDF Generation**: ReportLab
- **Frontend**: HTML templates with Jinja2
- **User Authentication & Authorization**: Role-based access control (e.g., General Manager, Technical Team Leader, Presale Engineer, Sales Engineer) with `werkzeug.security` for password hashing (scrypt:32768:8:1). Includes login/logout, session management, and a comprehensive page-level permission system. All routes are protected by `@login_required` or `@permission_required`.
- **Password Management**: Implements secure password hashing with automatic migration for plaintext passwords. Supports two password reset methods: OTP via email (if domain verified) and an admin-assisted manual OTP distribution dashboard. An admin-only direct password reset feature is also available.
- **Registration**: Public registration page with admin approval workflow.
- **Project Management**: Features project registration, quotation submission, status updates, and tracking through multiple stages.
- **CRM Features**: Manages customers, vendors, distributors, contractors, consultants, end-users, and technical support requests.
- **Sales & Presales Tools**: RFQ management, quotation builder, solution builder (Fiber, Passive), and cost sheet management.
- **Analytics & Reporting**: Sales and presales performance dashboards, pipeline analysis, and aging reports.
- **Document Management**: File upload/download for quotations and cost sheets, with Excel export functionality.
- **Product Catalog**: Includes fire alarm, CCTV, and passive products.

### Feature Specifications
- **Granular Access Control**: A page-level permission system with three database tables (`permissions`, `role_permissions`, `user_permissions`) allows for role-based defaults and user-specific overrides (Allow, Deny, Inherit). Permissions are cached in sessions and refreshed upon changes.
- **Admin-Assisted Password Reset**: A dashboard displays active OTP requests for administrators to manually provide OTPs to users, especially useful when email services are not fully configured. OTPs expire after 15 minutes and are single-use.
- **Public Registration with Admin Approval**: New users can register and their accounts require approval from General Managers or Technical Team Leaders.
- **User Management System**: An admin panel allows General Managers and Technical Team Leaders to add, edit, or delete user accounts, reset passwords, and assign roles.

### System Design Choices
- The application uses environment variables for configuration (e.g., `HOST`, `PORT`, `FLASK_DEBUG`, `SECRET_KEY`, email provider settings).
- A robust security architecture with complete route protection ensures all sensitive data and functions require authentication and authorization.
- Automatic password migration handles legacy plaintext passwords by upgrading them to hashed format upon first login.
- Multi-source email lookup for password resets checks `users`, `registration_requests`, and `engineers` tables.
- All 24 protected routes enforce server-side permissions.

## External Dependencies
- **Email Service**: Resend API (used for OTP via email, manual configuration without Replit's built-in integration).
- **Database**: SQLite3 (for application data).