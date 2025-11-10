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
- **CCTV Products Management**: Comprehensive CCTV camera product catalog with advanced filtering capabilities. Features: (1) Product registration with image upload, (2) Advanced multi-parameter filtering sidebar (Vendor, Model, Camera Type, Image Sensor, Max Resolution, Min Illumination, WDR, Built-in Mic, Supplement Light Range, Lens Type, Focal Length), (3) Modern card-based product display with vendor branding, model details, key specifications (Camera Type, Lens Type, Max Resolution, Image Sensor), and pricing, (4) Responsive grid layout with hover effects, (5) Clean, professional UI with gradient headers and sticky sidebar filters, (6) Excel bulk import for products, (7) Admin-only delete functionality (form-based with confirmation dialog) with automatic notifications, (8) Enhanced product cards display quick-reference specifications in a 2x2 grid with color-coded labels and icons. Database table: `cctv_products`. Routes: `/cctv_products`, `/register_product`, `/edit_product/<id>`, `/delete_product/<id>`, `/import_products_excel`.
- **CCTV Product Comparison**: Side-by-side comparison feature allowing users to select 2-4 products for detailed specification comparison. Features: (1) Checkbox selection on product cards with gradient styling, (2) Floating compare button that appears when products are selected, (3) Product count indicator, (4) Comprehensive comparison table displaying all 17 product attributes (image, vendor, model, price, camera specs, lens details, lighting features), (5) Responsive design with horizontal scroll for mobile devices, (6) Action buttons for datasheets and detailed views, (7) Styled "N/A" indicators for missing values. Routes: `/compare_products`.
- **AI-Powered CCTV Smart Selector**: Advanced intelligent selection system for HIKVISION cameras (312 products) featuring: (1) Smart wizard with one-click quick filters (Indoor/Outdoor/Budget/Premium), (2) AI-powered recommendation engine with budget-based, purpose-driven (Indoor/Outdoor/General), and priority optimization (Price/Quality/Features), (3) Advanced multi-parameter filtering (resolution, camera type, price range, features, full-text search), (4) Side-by-side product comparison tool (compare up to 4 products), (5) Modern responsive card-based UI with badges, hover effects, and feature tags. Separate database table `cctv_hikvision_products` maintains compatibility with existing `cctv_products` table. Routes: `/cctv_smart_selector`, `/api/cctv/recommend`, `/api/cctv/compare`.
- **Supplier Relationship Management (SRM) Module**: Comprehensive vendor and distributor management system with: (1) **Multi-Contact Management** - Multiple contacts per entity with role designation and primary contact flagging via `vendor_contacts` and `distributor_contacts` tables, (2) **Account Manager Assignment** - Link users to vendors/distributors via `account_manager_assignments` table for relationship tracking, (3) **Performance Metrics Tracking** - Track delivery_score, quality_score, response_time_score with overall_rating calculation stored in `performance_metrics` table, (4) **Document Management** - Secure file uploads/downloads with expiry tracking stored in `static/srm_documents/` directory via `srm_documents` table, (5) **Activity Log** - Complete audit trail in `srm_activity_log` table tracking all entity interactions, (6) **Enhanced Vendor/Distributor Detail Pages** - Comprehensive detail views with key metrics, contacts, POs, documents, performance, and activity timeline at `/vendor_detail/<id>` and `/distributor_detail/<id>`, (7) **SRM Analytics Dashboard** - Centralized analytics at `/srm_analytics` with Chart.js visualizations showing top performers, spending trends, document expiry alerts, and recent activities, (8) **Complete PO Integration** - Full purchase order integration with vendor/distributor profiles showing PO counts, total spending in stats cards, sortable PO tables (columns: PO Request #, PO Number, Project, Source [Direct/Via Distributor], Distributor Name, Date, Total Amount, Approval Status, Delivery Status, Documents with view/download links), Excel export functionality via `/download_vendor_pos_excel/<id>` and `/download_distributor_pos_excel/<id>` with auto-adjusted column widths, proper TEXT casting for distributor ID matching (IDs stored as TEXT in purchase_orders table), pagination showing first 10 POs with "Show All" button, and **Direct Vendor Linking** - POs can be optionally linked directly to vendors via new `vendor` column in purchase_orders table, enabling both direct purchases and distributor-mediated purchases with visual badges to distinguish PO source, (9) **Secure Document Access** - Protected download route `/download_srm_document/<id>` with @login_required authorization, (10) **Modern List Pages** - Refactored `/vendors` and `/distributors` routes with SRM data enrichment (contacts, account managers, associated entities) and modern card-based UI with gradient headers and direct access to detail pages. Database schema includes 7 new tables with proper relationships and audit fields. All legacy routes cleaned up and replaced with SRM-enabled versions.

### System Design Choices
- Environment variables are used for configuration (e.g., `HOST`, `PORT`, `FLASK_DEBUG`, `SECRET_KEY`, email settings).
- Robust security architecture with complete route protection (100% of protected routes secured).
- Automatic password migration for legacy plaintext passwords.
- Multi-source email lookup for password resets.
- **Timezone Handling**: Automatic timezone conversion for all timestamps using browser's local timezone. Users table includes timezone preference field (default: Asia/Riyadh). Notification timestamps display as relative time (e.g., "5 minutes ago") with automatic conversion to user's local time.

## External Dependencies
- **Email Service**: Resend API (for OTP via email).
- **Database**: SQLite3 (for application data).