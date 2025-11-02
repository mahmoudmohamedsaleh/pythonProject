# CRM and Presales Monitoring System

## Overview
This Flask-based CRM and Presales Monitoring System tracks projects, quotations, RFQs, and sales performance, managing the entire sales pipeline from lead generation to project completion. It provides comprehensive features for user authentication, project and customer relationship management, sales and presales tools, and analytics. The system supports a public registration process with admin approval and integrates robust password security, including an admin-assisted password reset mechanism.

## User Preferences
- **Email Provider**: Resend (configured with API key, not using Replit integration)
- **Note**: User declined Replit's Resend integration, using manual secret configuration instead

## System Architecture

### UI/UX Decisions
The system features a comprehensive admin access control UI at `/access_control` for managing granular page-level permissions. It also includes an admin OTP Dashboard at `/pending_otp_requests` for assisting with password resets without email. The UI provides real-time permission updates via AJAX and visual indicators for permission sources. Dynamic UI elements are supported through `user_has_permission()` in templates. Visual styling includes purple gradient badges for client designation and consistent UI across client management.

### Technical Implementations
- **Backend**: Flask (Python web framework)
- **Database**: SQLite3
- **Data Processing**: Pandas, openpyxl, xlsxwriter
- **PDF Generation**: ReportLab
- **Frontend**: HTML templates with Jinja2
- **User Authentication & Authorization**: Role-based access control (General Manager, Technical Team Leader, Presale Engineer, Sales Engineer) with `werkzeug.security` for password hashing (scrypt:32768:8:1). All routes are protected by `@login_required` or `@permission_required`.
- **Password Management**: Secure password hashing with automatic migration, OTP via email, and an admin-assisted manual OTP distribution dashboard.
- **Registration**: Public registration with admin approval workflow.
- **Project Management**: Project registration, quotation submission, status updates, and tracking; includes admin approval workflow for new projects, client designation, and automated deal value calculation.
- **CRM Features**: Manages customers, vendors, distributors, contractors, consultants, end-users, and technical support requests, including client status tracking and sales engineer assignment.
- **Sales & Presales Tools**: RFQ management (with comments system and edit notifications), quotation builder, solution builder (Fiber, Passive), and cost sheet management.
- **Analytics & Reporting**: Sales and presales performance dashboards, pipeline analysis, and aging reports.
- **Document Management**: File upload/download for quotations and cost sheets, with Excel export.
- **Product Catalog**: Fire alarm, CCTV, and passive products.
- **AI-Powered CCTV Smart Selector**: Intelligent product selection wizard for HIKVISION cameras with AI recommendations, advanced filtering, budget optimization, and side-by-side product comparison (separate database table: `cctv_hikvision_products`).

### Feature Specifications
- **Granular Access Control**: Page-level permission system using `permissions`, `role_permissions`, and `user_permissions` tables for role-based defaults and user-specific overrides.
- **Admin-Assisted Password Reset**: Dashboard for administrators to manually provide OTPs, especially when email services are not fully configured.
- **Public Registration with Admin Approval**: New user accounts require approval from General Managers or Technical Team Leaders.
- **User Management System**: Admin panel for General Managers and Technical Team Leaders to add, edit, delete users, reset passwords, and assign roles.
- **AI-Powered Deal Value Calculation**: Automatically calculates deal values from quotations using intelligent quote revision detection, matching, and duplicate prevention logic.
- **Project Approval System**: New projects require admin approval before entering the main pipeline, with notifications for approval/rejection.
- **Client Management System**: Dedicated admin interface to manage client status and assign sales engineers to end-users, contractors, and consultants.
- **Client Designation in Projects**: Projects can designate which entity (End User, Contractor, or Consultant) is the primary client, displayed with purple gradient badges throughout the system.
- **Smart Form Auto-Selection**: Project registration form automatically defaults to "Lead" stage and pre-selects the logged-in user as sales engineer for streamlined data entry.
- **All Clients Dashboard**: Unified view displaying all entities marked as clients across End Users, Contractors, and Consultants in a searchable card-based interface with type badges and project counts.
- **Role-Based Data Filtering**: Sales Engineers see only entities assigned to them in All Clients, End Users, Contractors, and Consultants pages, while General Managers, Technical Team Leaders, and Presale Engineers see all entities. Filtering applies to both search and normal view modes.
- **RFQ Creation Notifications**: Automatic notifications sent to all Presale Engineers, Technical Team Leaders, General Managers, and the assigned Sales Engineer when a new RFQ is created. Notifications include: RFQ reference, project name, priority, and status.
- **RFQ Edit Notifications**: Automatic notifications sent to all Presale Engineers, Technical Team Leaders, General Managers, and the assigned Sales Engineer when an RFQ is edited. Notifications include updated data: RFQ reference, project name, status, priority, and deadline.
- **RFQ Comment Notifications**: Automatic notifications sent to all Presale Engineers, Technical Team Leaders, and General Managers when a comment is added to an RFQ. Notifications include: RFQ reference, project name, and comment preview (first 50 characters).
- **RFQ Chronological Ordering**: RFQs displayed from newest to oldest across all views (RFQ Summary, Pipeline, Excel exports) using requested_time descending order.
- **AI-Powered CCTV Product Selector**: Advanced intelligent selection system for HIKVISION cameras (312 products) featuring: (1) Smart wizard with one-click quick filters (Indoor/Outdoor/Budget/Premium), (2) AI-powered recommendation engine with budget-based, purpose-driven (Indoor/Outdoor/General), and priority optimization (Price/Quality/Features), (3) Advanced multi-parameter filtering (resolution, camera type, price range, features, full-text search), (4) Side-by-side product comparison tool (compare up to 4 products), (5) Modern responsive card-based UI with badges, hover effects, and feature tags. Separate database table `cctv_hikvision_products` maintains compatibility with existing `cctv_products` table. Routes: `/cctv_smart_selector`, `/api/cctv/recommend`, `/api/cctv/compare`.
- **Hikvision Product Selector (Official Replica)**: Exact replica of Hikvision's official product selector (https://www.hikvision.com/en/products/product-selector/) featuring: (1) Web scraper module (`hikvision_scraper.py`) to fetch live product data from Hikvision website, (2) Full filter compatibility with all Hikvision categories (Case Type, Resolution, Lens Type, AI Features, Environmental Protection, Illumination Distance, Low-Light Imaging, Power Supply, Storage Type, Supplemental Light, WDR, Wireless Network), (3) Manual sync capability for administrators (General Managers and Technical Team Leaders only), (4) Product database table (`hikvision_products`) with comprehensive specifications, (5) Modern UI matching Hikvision's design with product cards, spec badges, and responsive grid layout. Routes: `/hikvision_selector`, `/api/hikvision/sync`, `/api/hikvision/stats`. Auto-sync capability ready for scheduled updates.

### System Design Choices
- Environment variables are used for configuration (e.g., `HOST`, `PORT`, `FLASK_DEBUG`, `SECRET_KEY`, email settings).
- Robust security architecture with complete route protection (100% of protected routes secured).
- Automatic password migration for legacy plaintext passwords.
- Multi-source email lookup for password resets.
- **Timezone Handling**: Automatic timezone conversion for all timestamps using browser's local timezone. Users table includes timezone preference field (default: Asia/Riyadh). Notification timestamps display as relative time (e.g., "5 minutes ago") with automatic conversion to user's local time.

## External Dependencies
- **Email Service**: Resend API (for OTP via email).
- **Database**: SQLite3 (for application data).