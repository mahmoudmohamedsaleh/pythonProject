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
- **Dynamic Role Management System**: Database-driven roles table enabling administrators to create, edit, and delete custom roles. Features include Manage Roles page with role statistics (user count, permission count), inline role editing, role permissions management page for configuring default permissions per role, "Add New Role" button integrated into Add User and Edit User forms with AJAX-based role creation, and automatic synchronization with access control system.
- **Supplier Relationship Management (SRM) Module**: Comprehensive vendor and distributor management with multi-contact, account manager assignment, performance metrics, document management, activity log, analytics, and PO integration.
- **Project Profile Pages**: Comprehensive detail views showing project lifecycle, statistics, quotations, RFQs, purchase orders, quick actions, timeline, approval status, and Excel export.
- **Request for PO Approval Workflow**: System for submitting purchase order requests, requiring TTL or GM approval. Includes supplier quotation PDF attachment, project coordinator assignment, server-side validation, dashboard with filtering, notifications, audit trail, and duplicate request prevention.
- **Supplier Quotation Management**: Tracks multiple supplier quotation PDFs per project with distributor/vendor association, system categorization, file validation, view/download functionality, and direct "Request PO" button integration.
- **Quotation Products Catalog**: System for building a reusable product library from supplier quotations, featuring a dedicated database table, "Add Product" modal, Products Dashboard with advanced filtering, price tracking, and security measures.
- **PO Profile System**: Modernized purchase order profile pages with VAT management, VAT invoice PDF upload, financial summary, per-item tracking (add/edit/delete), Excel import/export for bulk item management, per-item delivery status, delivery notes history with PDF attachment, and integrated contact information.
- **Delivery Note Edit Functionality**: Modal interface for editing delivery note status and notes with authorization and real-time updates.
- **Edit PO Modernization**: Overhauled Edit PO page to match Register PO layout, supporting vendors, named field access, consistent card-based sections, and quick-access buttons for new projects, vendors, and distributors. Technical Team Leaders are now selectable in the presale engineer dropdown.
- **Purchase Order Status Dashboard Modernization**: Redesigned view_po_status page with purple gradient hero header, KPI statistics cards, enhanced table layout with vendor display, presale engineer column, account manager column (renamed from "Manager"), LEFT JOIN fix to display all POs with username-based JOIN conditions for engineers and name-based JOIN for distributors/vendors, inline editing for key fields via AJAX, server-side validation, filter integration (including new vendor filter), and admin-only delete functionality. Technical Team Leaders are now selectable in the presale engineer dropdown on Register PO page. Database migration completed to convert all ID-based references to name/username-based references (21 POs total). Admin delete button with double confirmation removes PO and all associated data (items, delivery notes, supplier quotations).
- **Project Documents Management**: Comprehensive document upload system for project profiles allowing users to upload BOQ files (Excel format), specification documents (PDF format), and store Google Drive folder links. Documents are stored in database as BLOBs with version tracking, showing uploader name and timestamp. Features separate download buttons for each document type and direct link to Google Drive folder for centralized document access.
- **Project Chat System**: Real-time communication system enabling team collaboration on individual projects. Each project has an isolated chat room where authorized users can send text messages, upload images (JPG, PNG, GIF), and share PDF documents. Features include auto-refresh polling (10-second interval), inline image previews, PDF download links, file size validation (10MB max), secure file storage in project-specific directories, message history with timestamps and usernames, and HTML sanitization for security. Chat interface integrated into project detail page with scrollable message container and file attachment support.
- **Active Users Tracking**: Admin page (General Manager and Technical Team Leader via `view_active_users` permission) showing currently logged-in users in real-time. Features include session tracking via database table (active_sessions), login/logout recording, last activity timestamp updates on each request, user status indicators (Online/Idle/Away based on activity time), session termination capability, auto-refresh every 30 seconds, KPI cards showing active count, total users, and online rate percentage, device/browser detection via user-agent, IP address logging, and automatic stale session cleanup (24-hour timeout). Access controlled through Access Control system.
- **Client Profile System**: Comprehensive profile pages for all client types (End Users, Contractors, Consultants) with type-specific gradient headers, statistics cards (projects, quotations, deal value, pending follow-ups), contact information, pipeline breakdown, associated projects table, and direct navigation from All Clients page via "View Profile" button.
- **Follow-up Tracking System**: Database tables (client_follow_ups, client_activity_log) for managing client interactions. Features include scheduling follow-ups with type, date, time, priority, and notes; status tracking (Pending, Completed, Cancelled); activity logging for all client interactions; overdue detection with visual indicators.
- **Follow-up Reminder System**: Multi-channel reminder system for pending follow-ups. Includes in-app notifications via notification service, browser notifications (Web Notifications API) on page load, email reminders via Resend API with styled HTML templates showing overdue/due today/upcoming categorization, "Email Reminder" button on client profile page, automatic reminder check on every page load for logged-in users.
- **Bidirectional Task Management Sync**: Fully integrated task management synchronized with all follow-up systems (Client, RFQ, RFTS, Purchase Orders). Features automatic task creation when follow-ups are scheduled, bidirectional status propagation (Pending↔To Do, Completed↔Done, Cancelled→Done), source metadata tracking (source_type, source_id, client_name, client_type), color-coded task badges (pink/purple for Client, green for RFQ, purple gradient for RFTS, orange gradient for PO), unique constraint preventing duplicate syncs, and helper functions for retrieving client names, RFQ references, RFTS project names, and PO numbers.
- **PO Follow-up and Activity Log System**: Comprehensive follow-up tracking and activity logging for Purchase Orders. Features include database tables (po_follow_ups, po_activity_log), follow-up scheduling with type, contact, date/time, priority, and notes; status tracking (Pending, Completed, Cancelled); activity logging with contact details; visual overdue indicators; green gradient Follow-ups section and blue gradient Activity Log section on PO Profile pages; bidirectional sync with Task Management system.
- **Solution Profile with Vendor Categories**: Solution profile pages (/solution/<id>) support vendor management with a flexible category system. Any solution can have custom vendor categories (e.g., "Active", "Passive", "Network", etc.) created by M.Saleh. Categories feature custom names, icons, and colors. Vendors are grouped under their assigned categories with visual headers. Solutions without categories show a flat "Vendors & Partners" list. Features include: solution_vendor_categories database table, category CRUD APIs, category color picker, icon selection, vendor logo images (via URL) with graceful fallback to initials. Only M.Saleh can add/edit/delete vendors and categories.

### System Design Choices
- Environment variables are used for configuration.
- Robust security architecture with complete route protection.
- Automatic password migration for legacy passwords.
- Multi-source email lookup for password resets.
- Automatic timezone conversion for all timestamps using browser's local timezone, with user-configurable preferences.

## External Dependencies
- **Email Service**: Resend API (for OTP via email).
- **Database**: SQLite3 (for application data).