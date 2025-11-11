# CRM and Presales Monitoring System

## Overview
This Flask-based CRM and Presales Monitoring System tracks projects, quotations, RFQs, and sales performance, managing the entire sales pipeline from lead generation to project completion. It provides comprehensive features for user authentication, project and customer relationship management, sales and presales tools, and analytics. The system supports public registration with admin approval and integrates robust password security, including an admin-assisted password reset mechanism.

## User Preferences
- **Email Provider**: Resend (configured with API key, not using Replit integration)
- **Note**: User declined Replit's Resend integration, using manual secret configuration instead

## System Architecture

### UI/UX Decisions
The system features a comprehensive admin access control UI and an admin OTP Dashboard for assisting with password resets. It provides real-time permission updates via AJAX, visual indicators for permission sources, and dynamic UI elements. Visual styling includes purple gradient badges and consistent UI across client management.

### Technical Implementations
- **Backend**: Flask
- **Database**: SQLite3
- **Data Processing**: Pandas, openpyxl, xlsxwriter
- **PDF Generation**: ReportLab
- **Frontend**: HTML templates with Jinja2
- **User Authentication & Authorization**: Role-based access control with `werkzeug.security` for password hashing. All routes are protected.
- **Password Management**: Secure password hashing, OTP via email, and an admin-assisted manual OTP dashboard.
- **Registration**: Public registration with admin approval workflow.
- **Project Management**: Project registration, quotation submission, status updates, tracking, admin approval, client designation, and automated deal value calculation.
- **CRM Features**: Manages customers, vendors, distributors, contractors, consultants, end-users, and technical support requests, including client status tracking and sales engineer assignment.
- **Sales & Presales Tools**: RFQ management (with comments and notifications), quotation builder, solution builder, and cost sheet management.
- **Analytics & Reporting**: Sales and presales performance dashboards, pipeline analysis, and aging reports.
- **Document Management**: File upload/download for quotations and cost sheets, with Excel export.
- **Product Catalog**: Fire alarm, CCTV, and passive products.
- **AI-Powered CCTV Smart Selector**: Intelligent product selection wizard for HIKVISION cameras with AI recommendations, advanced filtering, budget optimization, and side-by-side comparison.

### Feature Specifications
- **Granular Access Control**: Page-level permission system using database tables for role-based defaults and user-specific overrides.
- **Admin-Assisted Password Reset**: Dashboard for administrators to manually provide OTPs.
- **Public Registration with Admin Approval**: New user accounts require approval.
- **User Management System**: Admin panel for managing users, roles, and resetting passwords.
- **AI-Powered Deal Value Calculation**: Automatically calculates deal values from quotations.
- **Project Approval System**: New projects require admin approval with notifications.
- **Client Management System**: Admin interface to manage client status and assign sales engineers.
- **Client Designation in Projects**: Projects can designate a primary client (End User, Contractor, or Consultant).
- **Smart Form Auto-Selection**: Project registration form defaults to "Lead" and pre-selects the logged-in user.
- **All Clients Dashboard**: Unified view of all entities marked as clients.
- **Role-Based Data Filtering**: Sales Engineers see only assigned entities; GMs, TTLs, PSEs see all.
- **RFQ Notifications**: Automatic notifications for RFQ creation, edits, and comments to relevant users.
- **RFQ Chronological Ordering**: RFQs displayed from newest to oldest.
- **CCTV Products Management**: Comprehensive product catalog with advanced filtering, card-based display, bulk import, and admin-only deletion.
- **CCTV Product Comparison**: Side-by-side comparison feature for 2-4 products with detailed specifications.
- **AI-Powered CCTV Smart Selector**: Advanced intelligent selection system for HIKVISION cameras featuring a smart wizard, AI recommendations, multi-parameter filtering, and comparison tool.
- **Supplier Relationship Management (SRM) Module**: Comprehensive vendor and distributor management with multi-contact, account manager assignment, performance metrics, document management, activity log, enhanced detail pages, analytics dashboard, and complete PO integration.
- **Project Profile Pages**: Comprehensive project detail views showing project lifecycle, key statistics, quotations, RFQs, purchase orders, quick actions sidebar, timeline information, approval status, and Excel export.
- **Request for PO Approval Workflow**: Comprehensive purchase order request system requiring approval from Technical Team Leader or General Manager before PO creation. Features include:
  - PO request submission from quotations with auto-filled project data
  - Server-side validation of all authoritative fields (distributors, vendors, project managers)
  - PO Requests Dashboard with filtering (status, requester, distributor, vendor, dates), status chart, and Excel export
  - Approval/rejection routes restricted to TTL and GM with mandatory rejection reasons
  - Automatic notifications to requesters on approval/rejection decisions
  - Unique RFPO reference format (RFPO-YYYYMMDD###)
  - Duplicate request prevention for pending approvals
  - Complete audit trail with timestamps and approver/rejector tracking
  - Create PO action button in project profile for approved RFPO requests
- **Supplier Quotation Management**: Track multiple supplier quotation PDFs per project with distributor/vendor association. Features include:
  - Dedicated supplier_quotations database table with distributor/vendor tracking and system field
  - Upload supplier quotation PDFs for each quotation reference with both distributor AND vendor selection (at least one required)
  - System field to categorize the quotation (e.g., Fire Alarm, CCTV, Access Control)
  - File validation (PDF only), notes field, and uploaded_by tracking
  - Supplier Quotations section in Project Profile with upload form and comprehensive table display
  - Download functionality for all uploaded supplier quotations
  - Both distributor and vendor fields visible simultaneously for flexible supplier tracking
  - Client-side and server-side validation requiring at least one supplier (distributor or vendor)
  - Complete audit trail with timestamps and uploader information

### System Design Choices
- Environment variables are used for configuration.
- Robust security architecture with complete route protection.
- Automatic password migration for legacy passwords.
- Multi-source email lookup for password resets.
- **Timezone Handling**: Automatic timezone conversion for all timestamps using browser's local timezone, with user-configurable preferences.

## External Dependencies
- **Email Service**: Resend API (for OTP via email).
- **Database**: SQLite3 (for application data).