"""
Notifications Service Module
Created: 2025-10-30
Purpose: Centralized notification management for CRM activities
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from flask import session


class NotificationService:
    """Service class for managing notifications"""
    
    def __init__(self, db_path='ProjectStatus.db'):
        self.db_path = db_path
    
    def _get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def notify_activity(
        self,
        event_code: str,
        recipient_ids: List[int],
        actor_id: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
        url: Optional[str] = None
    ) -> bool:
        """
        Create notifications for an activity
        
        Args:
            event_code: Event code (e.g., 'project.created')
            recipient_ids: List of user IDs to notify
            actor_id: ID of user who performed the action
            context: Additional context data (dict)
            url: URL to link to (optional)
        
        Returns:
            bool: True if notifications created successfully
        """
        if not recipient_ids:
            return False
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Get event details
            cursor.execute("""
                SELECT event_name, event_category, default_priority
                FROM notification_events
                WHERE event_code = ?
            """, (event_code,))
            event = cursor.fetchone()
            
            if not event:
                print(f"Warning: Event code '{event_code}' not found")
                return False
            
            event_name = event['event_name']
            event_category = event['event_category']
            priority = event['default_priority']
            
            # Generate message from context
            message = self._generate_message(event_code, context)
            title = event_name
            
            # Convert context to JSON
            context_json = json.dumps(context) if context else None
            
            # Create notifications for each recipient
            for recipient_id in recipient_ids:
                # Check user's notification preferences
                cursor.execute("""
                    SELECT in_app_enabled
                    FROM notification_preferences
                    WHERE user_id = ? AND event_code = ?
                """, (recipient_id, event_code))
                
                pref = cursor.fetchone()
                
                # If no preference exists or in-app is enabled, create notification
                if not pref or pref['in_app_enabled']:
                    cursor.execute("""
                        INSERT INTO notifications 
                        (user_id, actor_id, event_type, event_code, title, message, 
                         context_data, priority, url, is_read, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, CURRENT_TIMESTAMP)
                    """, (recipient_id, actor_id, event_category, event_code, title, 
                          message, context_json, priority, url))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"Error creating notification: {e}")
            return False
        finally:
            conn.close()
    
    def _generate_message(self, event_code: str, context: Optional[Dict[str, Any]]) -> str:
        """Generate notification message based on event and context"""
        if not context:
            return "Activity notification"
        
        actor = context.get('actor_name', 'A user')
        
        # Project events
        if event_code == 'project.created':
            return f"{actor} created a new project: {context.get('project_name', 'Unknown')}"
        elif event_code == 'project.pending_approval':
            return f"{actor} registered a new project that needs your approval: {context.get('project_name', 'Unknown')}"
        elif event_code == 'project.approved':
            return f"{actor} approved your project: {context.get('project_name', 'Unknown')}"
        elif event_code == 'project.rejected':
            reason = context.get('rejection_reason', 'No reason provided')
            return f"{actor} rejected your project: {context.get('project_name', 'Unknown')}. Reason: {reason}"
        elif event_code == 'project.updated':
            return f"{actor} updated project: {context.get('project_name', 'Unknown')}"
        elif event_code == 'project.deleted':
            return f"{actor} deleted project: {context.get('project_name', 'Unknown')}"
        elif event_code == 'project.stage_changed':
            return f"Project {context.get('project_name', 'Unknown')} stage changed to {context.get('new_stage', 'Unknown')}"
        
        # Quotation events
        elif event_code == 'quotation.submitted':
            return f"{actor} submitted quotation for project: {context.get('project_name', 'Unknown')}"
        elif event_code == 'quotation.updated':
            return f"{actor} updated quotation: {context.get('quotation_ref', 'Unknown')}"
        
        # PO events
        elif event_code == 'po.created':
            return f"{actor} created purchase order: {context.get('po_number', 'Unknown')}"
        elif event_code == 'po.updated':
            return f"{actor} updated purchase order: {context.get('po_number', 'Unknown')}"
        
        # RFQ events
        elif event_code == 'rfq.created':
            return f"{actor} created RFQ for project: {context.get('project_name', 'Unknown')}"
        elif event_code == 'rfq.comment_added':
            return f"{actor} added a comment to RFQ: {context.get('rfq_ref', 'Unknown')}"
        
        # User events
        elif event_code == 'user.registered':
            return f"New user registration request from: {context.get('username', 'Unknown')}"
        elif event_code == 'user.approved':
            return f"Your registration has been approved by {actor}"
        elif event_code == 'user.rejected':
            return f"Your registration has been rejected"
        elif event_code == 'user.password_reset':
            return f"Password reset request from: {context.get('username', 'Unknown')}"
        
        # Comment events
        elif event_code == 'comment.added':
            return f"{actor} added a comment"
        
        # Default
        return f"{actor} performed an action"
    
    def get_notifications(
        self,
        user_id: int,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get notifications for a user
        
        Args:
            user_id: User ID
            unread_only: Only return unread notifications
            limit: Maximum number of notifications to return
            offset: Offset for pagination
        
        Returns:
            List of notification dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                n.*,
                u.username as actor_name
            FROM notifications n
            LEFT JOIN users u ON n.actor_id = u.id
            WHERE n.user_id = ?
        """
        params = [user_id]
        
        if unread_only:
            query += " AND n.is_read = 0"
        
        query += " ORDER BY n.created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        notifications = []
        for row in rows:
            notif = dict(row)
            # Parse context_data if it exists
            if notif['context_data']:
                try:
                    notif['context'] = json.loads(notif['context_data'])
                except:
                    notif['context'] = {}
            else:
                notif['context'] = {}
            notifications.append(notif)
        
        return notifications
    
    def get_unread_count(self, user_id: int) -> int:
        """Get count of unread notifications for a user"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM notifications
            WHERE user_id = ? AND is_read = 0
        """, (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return result['count'] if result else 0
    
    def mark_as_read(self, notification_ids: List[int], user_id: int) -> bool:
        """Mark notifications as read"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            placeholders = ','.join('?' * len(notification_ids))
            cursor.execute(f"""
                UPDATE notifications
                SET is_read = 1, read_at = CURRENT_TIMESTAMP
                WHERE id IN ({placeholders}) AND user_id = ?
            """, notification_ids + [user_id])
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error marking notifications as read: {e}")
            return False
        finally:
            conn.close()
    
    def mark_all_as_read(self, user_id: int) -> bool:
        """Mark all notifications as read for a user"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE notifications
                SET is_read = 1, read_at = CURRENT_TIMESTAMP
                WHERE user_id = ? AND is_read = 0
            """, (user_id,))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error marking all notifications as read: {e}")
            return False
        finally:
            conn.close()
    
    def delete_old_notifications(self, days: int = 180) -> int:
        """
        Delete notifications older than specified days
        
        Args:
            days: Number of days to keep notifications
        
        Returns:
            Number of notifications deleted
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                DELETE FROM notifications
                WHERE created_at < datetime('now', '-' || ? || ' days')
            """, (days,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            return deleted_count
        except Exception as e:
            conn.rollback()
            print(f"Error deleting old notifications: {e}")
            return 0
        finally:
            conn.close()
    
    def get_admin_recipients(self) -> List[int]:
        """Get all admin user IDs (General Managers and Technical Team Leaders)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id
            FROM users
            WHERE role IN ('General Manager', 'Technical Team Leader')
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [row['id'] for row in rows]
    
    def get_user_id_by_username(self, username: str) -> Optional[int]:
        """Get user ID by username"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        
        return result['id'] if result else None
    
    def get_project_stakeholders(self, project_id: int) -> List[int]:
        """Get all users involved with a project (sales engineer, admins)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Get sales engineer for the project
        cursor.execute("""
            SELECT en.username
            FROM register_project rp
            LEFT JOIN engineers en ON rp.sales_engineer_id = en.id
            WHERE rp.id = ?
        """, (project_id,))
        
        result = cursor.fetchone()
        stakeholders = []
        
        if result and result['username']:
            user_id = self.get_user_id_by_username(result['username'])
            if user_id:
                stakeholders.append(user_id)
        
        # Add all admins
        stakeholders.extend(self.get_admin_recipients())
        
        conn.close()
        
        # Remove duplicates
        return list(set(stakeholders))


# Global instance
notification_service = NotificationService()
