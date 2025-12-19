# CRM and Presales Monitoring System

## Overview
This Flask-based CRM and Presales Monitoring System provides end-to-end management of the sales pipeline, from lead generation to project completion. It tracks projects, quotations, RFQs, and sales performance. The system offers features for user authentication, comprehensive project and customer relationship management, sales and presales tools, and analytics. It supports public registration with admin approval and ensures robust password security with an admin-assisted reset mechanism. The business vision is to streamline sales and presales operations, improve efficiency, and provide actionable insights for better decision-making within an organization.

## User Preferences
- **Email Provider**: Resend (configured with API key, not using Replit integration)
- **Note**: User declined Replit's Resend integration, using manual secret configuration instead

## System Architecture

### UI/UX Decisions
The system features an admin access control UI, an admin OTP Dashboard for password resets, and real-time permission updates via AJAX. It uses visual indicators for permission sources, dynamic UI elements, purple gradient badges, and consistent UI across client management, aiming for a modern and intuitive user experience. Custom-prefixed modal classes are used to avoid Bootstrap conflicts, alongside enhanced visual designs featuring gradient hero sections, improved stat cards with hover effects, and stylized category headers.

### Technical Implementations
- **Backend**: Flask
- **Database**: SQLite3
- **Data Processing**: Pandas, openpyxl, xlsxwriter
- **PDF Generation**: ReportLab
- **Frontend**: HTML templates with Jinja2
- **User Management**: Role-based access control, secure authentication (`werkzeug.security`), password resets via OTP, and public registration with admin approval.
- **CRM Features**: Manages customers, vendors, distributors, contractors, consultants, end-users, technical support, client status, and sales engineer assignments, including comprehensive client profile pages with statistics and follow-up tracking. Includes a **Client Tier System** (VIP, Key Account, Standard, New) for prioritizing and categorizing client importance with a redesigned All Clients page featuring a statistics dashboard, filtering, and sorting capabilities.
- **Project Management**: Registration, quotation submission, status updates, tracking, admin approval, client designation, automated deal value calculation, and comprehensive project profile pages showing the project lifecycle, documents, and chat.
- **Sales & Presales Tools**: RFQ management (with comments and notifications), quotation builder, solution builder, cost sheet management, product catalog (fire alarm, CCTV, passive), and an AI-Powered CCTV Smart Selector for intelligent product recommendations.
- **Access Control**: Granular, page-level permissions with a dynamic, database-driven role management system allowing administrators to create and manage custom roles.
- **Supplier Relationship Management (SRM)**: Comprehensive vendor and distributor management, including activity logs, performance metrics, and purchase order integration.
- **Purchase Order (PO) Management**: Workflow for PO approval, supplier quotation management, PO profile system with VAT management, per-item tracking, delivery note functionality, and modernized dashboards with inline editing.
- **Document Management**: Project-specific document uploads (BOQ, specifications, Google Drive links) with version tracking, and company-level document management for essential company files.
- **Collaboration**: Real-time project chat system for team communication, supporting text, image, and PDF sharing. Features **WhatsApp-like chat notifications** with sound alerts, floating popup toasts, browser notifications, and click-to-navigate functionality.
- **Follow-up & Task Management**: Multi-channel follow-up reminder system (in-app, browser, email) integrated with a bidirectional task management synchronization system across clients, RFQs, RFTS, and POs.
- **Solution Profile Management**: Solution profiles with vendor categories, editable by M.Saleh, supporting custom categories, icons, colors, and vendor logo uploads.
- **Company Profile Management**: Editable hero section, footprint, contact information, and "Our Clients" section on the company profile page by M.Saleh, supporting text and image uploads.
- **Project Profile Management**: Individual project profile pages accessible by clicking Featured Projects, featuring project certificates and approvals management with file upload support. Editable by M.Saleh only.
- **Active Users Tracking**: Admin dashboard for real-time monitoring of logged-in users, including session details, activity status, and termination capabilities.

### System Design Choices
- Environment variables are used for configuration.
- Robust security architecture with complete route protection.
- Automatic password migration for legacy passwords.
- Multi-source email lookup for password resets.
- Automatic timezone conversion for all timestamps using browser's local timezone, with user-configurable preferences.

## External Dependencies
- **Email Service**: Resend API (for OTP via email and follow-up reminders).
- **Database**: SQLite3 (for application data).