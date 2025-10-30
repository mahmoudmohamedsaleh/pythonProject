-- Notification System Database Schema
-- Created: 2025-10-30
-- Purpose: Comprehensive notification tracking for CRM activities

-- Main notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipient_id INTEGER NOT NULL,
    actor_id INTEGER,
    event_type VARCHAR(50) NOT NULL,
    event_code VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    context_data TEXT,
    priority VARCHAR(20) DEFAULT 'normal',
    is_read BOOLEAN DEFAULT 0,
    url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP,
    FOREIGN KEY (recipient_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (actor_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_notifications_recipient_read 
    ON notifications(recipient_id, is_read, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_notifications_event_type 
    ON notifications(event_type);
CREATE INDEX IF NOT EXISTS idx_notifications_created 
    ON notifications(created_at DESC);

-- User notification preferences
CREATE TABLE IF NOT EXISTS notification_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    event_code VARCHAR(100) NOT NULL,
    in_app_enabled BOOLEAN DEFAULT 1,
    email_enabled BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, event_code)
);

-- Event type mapping and configuration
CREATE TABLE IF NOT EXISTS notification_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_code VARCHAR(100) UNIQUE NOT NULL,
    event_name VARCHAR(255) NOT NULL,
    event_category VARCHAR(50) NOT NULL,
    default_priority VARCHAR(20) DEFAULT 'normal',
    email_by_default BOOLEAN DEFAULT 0,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default notification event types
INSERT OR IGNORE INTO notification_events (event_code, event_name, event_category, default_priority, email_by_default, description) VALUES
-- Project events
('project.created', 'Project Created', 'project', 'normal', 0, 'A new project has been registered'),
('project.updated', 'Project Updated', 'project', 'normal', 0, 'A project has been updated'),
('project.deleted', 'Project Deleted', 'project', 'high', 1, 'A project has been deleted'),
('project.stage_changed', 'Project Stage Changed', 'project', 'normal', 0, 'Project stage has been updated'),

-- Quotation events
('quotation.submitted', 'Quotation Submitted', 'quotation', 'normal', 0, 'A new quotation has been submitted'),
('quotation.updated', 'Quotation Updated', 'quotation', 'normal', 0, 'A quotation has been updated'),
('quotation.approved', 'Quotation Approved', 'quotation', 'high', 1, 'A quotation has been approved'),

-- Purchase Order events
('po.created', 'Purchase Order Created', 'po', 'normal', 0, 'A new purchase order has been created'),
('po.updated', 'Purchase Order Updated', 'po', 'normal', 0, 'A purchase order has been updated'),
('po.status_changed', 'PO Status Changed', 'po', 'normal', 0, 'Purchase order status has changed'),

-- RFQ events
('rfq.created', 'RFQ Created', 'rfq', 'normal', 0, 'A new RFQ has been created'),
('rfq.updated', 'RFQ Updated', 'rfq', 'normal', 0, 'An RFQ has been updated'),
('rfq.comment_added', 'RFQ Comment Added', 'rfq', 'normal', 0, 'A comment was added to an RFQ'),

-- User/Auth events
('user.registered', 'New User Registration', 'user', 'high', 1, 'A new user has requested registration'),
('user.approved', 'Registration Approved', 'user', 'high', 1, 'Your registration has been approved'),
('user.rejected', 'Registration Rejected', 'user', 'high', 1, 'Your registration has been rejected'),
('user.password_reset', 'Password Reset Request', 'user', 'high', 1, 'A user has requested password reset'),

-- Comment events
('comment.added', 'Comment Added', 'comment', 'normal', 0, 'A new comment has been added'),

-- Task events
('task.assigned', 'Task Assigned', 'task', 'normal', 0, 'A task has been assigned to you'),
('task.completed', 'Task Completed', 'task', 'normal', 0, 'A task has been completed'),

-- System events
('system.alert', 'System Alert', 'system', 'high', 1, 'Important system alert');

-- Create default preferences for existing users
INSERT OR IGNORE INTO notification_preferences (user_id, event_code, in_app_enabled, email_enabled)
SELECT u.id, e.event_code, 1, e.email_by_default
FROM users u
CROSS JOIN notification_events e;
