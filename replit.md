# CRM and Presales Monitoring System

## Overview
This Flask-based CRM and Presales Monitoring System provides end-to-end management of the sales pipeline, from lead generation to project completion. It tracks projects, quotations, RFQs, and sales performance, offering features for user authentication, comprehensive project and customer relationship management, sales and presales tools, and analytics. The system supports public registration with admin approval and ensures robust password security with an admin-assisted reset mechanism.

## User Preferences
- **Email Provider**: Resend (configured with API key, not using Replit integration)
- **Note**: User declined Replit's Resend integration, using manual secret configuration instead

## System Architecture

### UI/UX Decisions
The system features a comprehensive admin access control UI, an admin OTP Dashboard for password resets, and real-time permission updates via AJAX. It uses visual indicators for permission sources, dynamic UI elements, purple gradient badges, and consistent UI across client management.

### Technical Implementations
- **Backend**: Flask
- **Database**: SQLite3
- **Data Processing**: Pandas, openpyxl, xlsxwriter
- **PDF Generation**: ReportLab
- **Frontend**: HTML templates with Jinja2
- **User Authentication & Authorization**: Role-based access control, `werkzeug.security` for password hashing, and protected routes.
- **Password Management**: Secure hashing, OTP via email, and admin-assisted manual OTP dashboard.
- **Registration**: Public registration with admin approval.
- **Project Management**: Registration, quotation submission, status updates, tracking, admin approval, client designation, and automated deal value calculation.
- **CRM Features**: Manages customers, vendors, distributors, contractors, consultants, end-users, technical support, client status, and sales engineer assignments.
- **Sales & Presales Tools**: RFQ management (with comments and notifications), quotation builder, solution builder, and cost sheet management.
- **Analytics & Reporting**: Sales and presales performance dashboards, pipeline analysis, and aging reports.
- **Document Management**: File upload/download for quotations and cost sheets, with Excel export.
- **Product Catalog**: Fire alarm, CCTV, and passive products.
- **AI-Powered CCTV Smart Selector**: Intelligent product selection wizard for HIKVISION cameras with AI recommendations, advanced filtering, budget optimization, and side-by-side comparison.
- **Granular Access Control**: Page-level permissions using database tables for role-based defaults and user-specific overrides.
- **Supplier Relationship Management (SRM) Module**: Comprehensive vendor and distributor management with multi-contact, account manager assignment, performance metrics, document management, activity log, analytics, and PO integration.
- **Project Profile Pages**: Comprehensive detail views showing project lifecycle, statistics, quotations, RFQs, purchase orders, quick actions, timeline, approval status, and Excel export.
- **Request for PO Approval Workflow**: System for submitting purchase order requests, requiring TTL or GM approval. Includes supplier quotation PDF attachment, project coordinator assignment, server-side validation, dashboard with filtering, notifications, audit trail, and duplicate request prevention.
- **Supplier Quotation Management**: Tracks multiple supplier quotation PDFs per project with distributor/vendor association, system categorization, file validation, view/download functionality, and direct "Request PO" button integration.
- **Quotation Products Catalog**: System for building a reusable product library from supplier quotations, featuring a dedicated database table, "Add Product" modal, Products Dashboard with advanced filtering, price tracking, and security measures.
- **PO Profile System**: Modernized purchase order profile pages with VAT management, VAT invoice PDF upload, financial summary, per-item tracking (add/edit/delete), Excel import/export for bulk item management, per-item delivery status, delivery notes history with PDF attachment, and integrated contact information.
- **Delivery Note Edit Functionality**: Modal interface for editing delivery note status and notes with authorization and real-time updates.
- **Edit PO Modernization**: Overhauled Edit PO page to match Register PO layout, supporting vendors, named field access, consistent card-based sections, and quick-access buttons for new projects, vendors, and distributors.
- **Purchase Order Status Dashboard Modernization**: Redesigned view_po_status page with a hero header, KPI statistics cards, enhanced table layout with vendor display, inline editing for key fields via AJAX, server-side validation, and filter integration.

### System Design Choices
- Environment variables are used for configuration.
- Robust security architecture with complete route protection.
- Automatic password migration for legacy passwords.
- Multi-source email lookup for password resets.
- Automatic timezone conversion for all timestamps using browser's local timezone, with user-configurable preferences.

## External Dependencies
- **Email Service**: Resend API (for OTP via email).
- **Database**: SQLite3 (for application data).