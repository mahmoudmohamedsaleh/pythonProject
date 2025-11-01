/**
 * Notification System JavaScript
 * Handles real-time notification updates via AJAX polling
 */

let notificationPollingInterval = null;
let notificationDropdownOpen = false;

// Initialize notification system when DOM is ready
$(document).ready(function() {
    // Only initialize if user is logged in
    if ($('#notificationBell').length > 0) {
        initializeNotifications();
        
        // Start polling every 30 seconds
        startNotificationPolling();
        
        // Setup event handlers
        setupNotificationEventHandlers();
    }
});

function initializeNotifications() {
    // Load initial notification count
    updateNotificationCount();
}

function startNotificationPolling() {
    // Fetch notifications immediately
    updateNotificationCount();
    
    // Then poll every 30 seconds
    notificationPollingInterval = setInterval(function() {
        updateNotificationCount();
        
        // If dropdown is open, refresh the list
        if (notificationDropdownOpen) {
            loadNotifications();
        }
    }, 30000); // 30 seconds
}

function stopNotificationPolling() {
    if (notificationPollingInterval) {
        clearInterval(notificationPollingInterval);
        notificationPollingInterval = null;
    }
}

function updateNotificationCount() {
    $.ajax({
        url: '/api/notifications/count',
        method: 'GET',
        success: function(response) {
            if (response.success) {
                const count = response.unread_count;
                const badge = $('#notificationBadge');
                
                if (count > 0) {
                    badge.text(count > 99 ? '99+' : count);
                    badge.show();
                } else {
                    badge.hide();
                }
            }
        },
        error: function(xhr, status, error) {
            console.error('Failed to fetch notification count:', error);
        }
    });
}

function loadNotifications() {
    $.ajax({
        url: '/api/notifications/feed?limit=10&unread_only=false',
        method: 'GET',
        success: function(response) {
            if (response.success) {
                renderNotifications(response.notifications);
            }
        },
        error: function(xhr, status, error) {
            console.error('Failed to load notifications:', error);
            $('#notificationList').html('<div class="text-center text-danger p-3">Failed to load notifications</div>');
        }
    });
}

function renderNotifications(notifications) {
    const list = $('#notificationList');
    list.empty();
    
    if (notifications.length === 0) {
        list.html('<div class="text-center text-muted p-4"><i class="fas fa-bell-slash" style="font-size: 2rem; margin-bottom: 10px;"></i><br>No notifications</div>');
        return;
    }
    
    notifications.forEach(function(notif) {
        const notifDiv = $('<div>')
            .addClass('notification-item')
            .css({
                'padding': '12px',
                'border-bottom': '1px solid #e9ecef',
                'cursor': 'pointer',
                'background-color': notif.is_read ? '#ffffff' : '#f0f8ff'
            })
            .hover(
                function() { $(this).css('background-color', '#f8f9fa'); },
                function() { $(this).css('background-color', notif.is_read ? '#ffffff' : '#f0f8ff'); }
            );
        
        // Priority badge
        let priorityBadge = '';
        if (notif.priority === 'high') {
            priorityBadge = '<span class="badge badge-danger" style="font-size: 0.7rem;">High</span> ';
        }
        
        // Time ago
        const timeAgo = formatTimeAgo(notif.created_at);
        
        // Unread indicator
        const unreadDot = notif.is_read ? '' : '<span style="display: inline-block; width: 8px; height: 8px; background: #007bff; border-radius: 50%; margin-right: 8px;"></span>';
        
        notifDiv.html(`
            <div style="display: flex; align-items: flex-start;">
                ${unreadDot}
                <div style="flex-grow: 1;">
                    <div style="font-weight: ${notif.is_read ? 'normal' : '600'}; color: #343a40; font-size: 0.9rem; margin-bottom: 4px;">
                        ${priorityBadge}${escapeHtml(notif.title)}
                    </div>
                    <div style="font-size: 0.85rem; color: #6c757d; margin-bottom: 4px;">
                        ${escapeHtml(notif.message)}
                    </div>
                    <div style="font-size: 0.75rem; color: #999;">
                        <i class="far fa-clock"></i> ${timeAgo}
                    </div>
                </div>
            </div>
        `);
        
        // Click handler
        notifDiv.on('click', function() {
            if (!notif.is_read) {
                markAsRead([notif.id]);
            }
            
            if (notif.url) {
                window.location.href = notif.url;
            }
        });
        
        list.append(notifDiv);
    });
}

function markAsRead(notificationIds) {
    $.ajax({
        url: '/api/notifications/mark_read',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ notification_ids: notificationIds }),
        success: function(response) {
            if (response.success) {
                updateNotificationCount();
                if (notificationDropdownOpen) {
                    loadNotifications();
                }
            }
        },
        error: function(xhr, status, error) {
            console.error('Failed to mark notifications as read:', error);
        }
    });
}

function markAllAsRead() {
    $.ajax({
        url: '/api/notifications/mark_read',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ all: true }),
        success: function(response) {
            if (response.success) {
                updateNotificationCount();
                loadNotifications();
            }
        },
        error: function(xhr, status, error) {
            console.error('Failed to mark all as read:', error);
        }
    });
}

function setupNotificationEventHandlers() {
    // Toggle dropdown
    $('#notificationBell').on('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const dropdown = $('#notificationDropdown');
        
        if (notificationDropdownOpen) {
            dropdown.hide();
            notificationDropdownOpen = false;
        } else {
            dropdown.show();
            notificationDropdownOpen = true;
            loadNotifications();
        }
    });
    
    // Mark all as read button
    $('#markAllRead').on('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        markAllAsRead();
    });
    
    // Close dropdown when clicking outside
    $(document).on('click', function(e) {
        if (notificationDropdownOpen && 
            !$(e.target).closest('#notificationDropdown').length && 
            !$(e.target).closest('#notificationBell').length) {
            $('#notificationDropdown').hide();
            notificationDropdownOpen = false;
        }
    });
}

function formatTimeAgo(timestamp) {
    try {
        // Parse timestamp - handle both ISO format and SQL datetime format
        const notifTime = new Date(timestamp.replace(' ', 'T') + (timestamp.includes('Z') ? '' : 'Z'));
        const now = new Date();
        
        // Calculate difference in milliseconds
        const diffMs = now - notifTime;
        const diffSecs = Math.floor(diffMs / 1000);
        const diffMins = Math.floor(diffSecs / 60);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);
        
        // Return human-readable relative time
        if (diffSecs < 10) return 'Just now';
        if (diffSecs < 60) return `${diffSecs} seconds ago`;
        if (diffMins === 1) return '1 minute ago';
        if (diffMins < 60) return `${diffMins} minutes ago`;
        if (diffHours === 1) return '1 hour ago';
        if (diffHours < 24) return `${diffHours} hours ago`;
        if (diffDays === 1) return '1 day ago';
        if (diffDays < 7) return `${diffDays} days ago`;
        if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
        if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
        
        // For older notifications, show the actual date in user's timezone
        return notifTime.toLocaleString(undefined, {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (e) {
        console.error('Error formatting time:', e, timestamp);
        return 'Unknown time';
    }
}

function escapeHtml(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

function viewAllNotifications() {
    window.location.href = '/notifications';
}

// Cleanup on page unload
$(window).on('unload', function() {
    stopNotificationPolling();
});
