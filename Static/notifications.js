/**
 * Notification System JavaScript
 * Handles real-time notification updates via AJAX polling
 * Includes WhatsApp-like chat notifications with sound
 */

let notificationPollingInterval = null;
let notificationDropdownOpen = false;
let chatPollingInterval = null;
let lastSeenChatId = 0;
let chatNotificationSound = null;
let chatSoundEnabled = true;

// Initialize notification system when DOM is ready
$(document).ready(function() {
    // Only initialize if user is logged in
    if ($('#notificationBell').length > 0) {
        initializeNotifications();
        
        // Start polling every 30 seconds
        startNotificationPolling();
        
        // Setup event handlers
        setupNotificationEventHandlers();
        
        // Initialize chat notification system
        initializeChatNotifications();
    }
});

function initializeNotifications() {
    // Load initial notification count
    updateNotificationCount();
    
    // Check for follow-up reminders (creates in-app notifications)
    checkFollowUpReminders();
}

function checkFollowUpReminders() {
    $.ajax({
        url: '/api/check_follow_up_reminders',
        method: 'GET',
        success: function(response) {
            if (response.success && response.reminders && response.reminders.length > 0) {
                // Show browser notification for urgent follow-ups
                const overdue = response.reminders.filter(r => r.is_overdue).length;
                const today = response.reminders.filter(r => r.is_today).length;
                
                if ((overdue > 0 || today > 0) && 'Notification' in window) {
                    if (Notification.permission === 'granted') {
                        showFollowUpBrowserNotification(overdue, today);
                    } else if (Notification.permission === 'default') {
                        Notification.requestPermission().then(function(permission) {
                            if (permission === 'granted') {
                                showFollowUpBrowserNotification(overdue, today);
                            }
                        });
                    }
                }
                
                // Refresh notification count since new notifications may have been created
                setTimeout(function() {
                    updateNotificationCount();
                }, 1000);
            }
        },
        error: function(xhr, status, error) {
            console.log('Follow-up reminder check failed:', error);
        }
    });
}

function showFollowUpBrowserNotification(overdue, today) {
    let message = '';
    if (overdue > 0) message += overdue + ' overdue follow-up' + (overdue > 1 ? 's' : '') + '. ';
    if (today > 0) message += today + ' due today.';
    
    new Notification('Follow-up Reminder', {
        body: message.trim(),
        icon: '/static/ejt.png',
        tag: 'followup-reminder-' + new Date().toDateString(),
        requireInteraction: true
    });
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
    stopChatPolling();
});

/**
 * ==========================================
 * CHAT NOTIFICATION SYSTEM (WhatsApp-like)
 * ==========================================
 */

function initializeChatNotifications() {
    // Create notification sound using Web Audio API
    createNotificationSound();
    
    // Request notification permission
    requestNotificationPermission();
    
    // Get the latest chat message ID to start from
    $.ajax({
        url: '/api/chat/latest_id',
        method: 'GET',
        success: function(response) {
            if (response.success) {
                lastSeenChatId = response.latest_id || 0;
                // Start polling after we have the initial ID
                startChatPolling();
            }
        },
        error: function(xhr, status, error) {
            console.log('Failed to get latest chat ID:', error);
            // Start polling anyway
            startChatPolling();
        }
    });
}

function createNotificationSound() {
    try {
        // Create AudioContext for generating notification sound
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (AudioContext) {
            chatNotificationSound = new AudioContext();
        }
    } catch (e) {
        console.log('Audio not supported:', e);
    }
}

function playNotificationSound() {
    if (!chatSoundEnabled || !chatNotificationSound) return;
    
    try {
        // Resume AudioContext if suspended (required for some browsers)
        if (chatNotificationSound.state === 'suspended') {
            chatNotificationSound.resume();
        }
        
        const oscillator = chatNotificationSound.createOscillator();
        const gainNode = chatNotificationSound.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(chatNotificationSound.destination);
        
        // WhatsApp-like notification sound (two quick beeps)
        oscillator.frequency.setValueAtTime(880, chatNotificationSound.currentTime); // A5
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0, chatNotificationSound.currentTime);
        gainNode.gain.linearRampToValueAtTime(0.3, chatNotificationSound.currentTime + 0.01);
        gainNode.gain.linearRampToValueAtTime(0, chatNotificationSound.currentTime + 0.1);
        gainNode.gain.linearRampToValueAtTime(0.3, chatNotificationSound.currentTime + 0.15);
        gainNode.gain.linearRampToValueAtTime(0, chatNotificationSound.currentTime + 0.25);
        
        oscillator.start(chatNotificationSound.currentTime);
        oscillator.stop(chatNotificationSound.currentTime + 0.3);
    } catch (e) {
        console.log('Error playing notification sound:', e);
    }
}

function requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
}

function startChatPolling() {
    // Poll every 5 seconds for chat messages (faster than general notifications)
    chatPollingInterval = setInterval(checkForNewChatMessages, 5000);
}

function stopChatPolling() {
    if (chatPollingInterval) {
        clearInterval(chatPollingInterval);
        chatPollingInterval = null;
    }
}

function checkForNewChatMessages() {
    console.log('[Chat Notifications] Checking for new messages, last_seen_id:', lastSeenChatId);
    $.ajax({
        url: '/api/chat/notifications?last_seen_id=' + lastSeenChatId,
        method: 'GET',
        success: function(response) {
            console.log('[Chat Notifications] Response:', response);
            if (response.success && response.messages && response.messages.length > 0) {
                console.log('[Chat Notifications] Found', response.messages.length, 'new messages!');
                // Update last seen ID
                if (response.max_id > lastSeenChatId) {
                    lastSeenChatId = response.max_id;
                }
                
                // Show notifications for each new message (limit to 3 at a time)
                const messagesToShow = response.messages.slice(0, 3);
                messagesToShow.forEach(function(msg, index) {
                    setTimeout(function() {
                        showChatToast(msg);
                    }, index * 200); // Stagger the notifications
                });
                
                // Play sound once for all new messages
                playNotificationSound();
                
                // Show browser notification if page is not focused
                if (document.hidden && 'Notification' in window && Notification.permission === 'granted') {
                    showBrowserChatNotification(messagesToShow[0]);
                }
            }
        },
        error: function(xhr, status, error) {
            console.log('Chat notification check failed:', error);
        }
    });
}

function showChatToast(message) {
    const container = $('#chatNotificationContainer');
    if (!container.length) return;
    
    const toastId = 'chat-toast-' + message.id;
    
    // Don't show duplicate toasts
    if ($('#' + toastId).length > 0) return;
    
    // Truncate message text
    let messageText = message.message_text || '';
    if (messageText.length > 80) {
        messageText = messageText.substring(0, 80) + '...';
    }
    
    // Create attachment indicator if has attachment
    let attachmentHtml = '';
    if (message.has_attachment) {
        const icon = message.attachment_filename && message.attachment_filename.match(/\.(jpg|jpeg|png|gif)$/i) 
            ? 'fa-image' : 'fa-paperclip';
        attachmentHtml = `
            <div class="chat-toast-attachment">
                <i class="fas ${icon}"></i>
                <span>${escapeHtml(message.attachment_filename) || 'Attachment'}</span>
            </div>
        `;
    }
    
    // Format time
    const time = formatChatTime(message.created_at);
    
    const toast = $(`
        <div class="chat-toast pulse" id="${toastId}" data-project-id="${message.project_id}">
            <div class="chat-toast-header">
                <div class="chat-toast-project">
                    <i class="fas fa-folder-open"></i>
                    <span>${escapeHtml(message.project_name)}</span>
                </div>
                <button class="chat-toast-close" onclick="closeChatToast('${toastId}'); event.stopPropagation();">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="chat-toast-body">
                <div class="chat-toast-sender">
                    <i class="fas fa-user-circle"></i>
                    ${escapeHtml(message.username)}
                </div>
                <div class="chat-toast-message">
                    ${messageText ? escapeHtml(messageText) : '<i class="text-light opacity-75">[Attachment]</i>'}
                </div>
                ${attachmentHtml}
                <div class="chat-toast-time">
                    <i class="far fa-clock"></i> ${time}
                </div>
            </div>
        </div>
    `);
    
    // Click handler to navigate to project
    toast.on('click', function() {
        const projectId = $(this).data('project-id');
        window.location.href = '/project/' + projectId + '#project-chat';
    });
    
    container.prepend(toast);
    
    // Trigger animation
    setTimeout(function() {
        toast.addClass('show');
    }, 10);
    
    // Auto-remove after 8 seconds
    setTimeout(function() {
        closeChatToast(toastId);
    }, 8000);
    
    // Keep only 3 toasts visible
    const toasts = container.find('.chat-toast');
    if (toasts.length > 3) {
        toasts.slice(3).each(function() {
            closeChatToast($(this).attr('id'));
        });
    }
}

function closeChatToast(toastId) {
    const toast = $('#' + toastId);
    if (toast.length) {
        toast.removeClass('show');
        setTimeout(function() {
            toast.remove();
        }, 400);
    }
}

function showBrowserChatNotification(message) {
    try {
        const notification = new Notification('New message in ' + message.project_name, {
            body: message.username + ': ' + (message.message_text || 'Sent an attachment'),
            icon: '/static/ejt.png',
            tag: 'chat-' + message.id,
            requireInteraction: false
        });
        
        notification.onclick = function() {
            window.focus();
            window.location.href = '/project/' + message.project_id + '#project-chat';
            notification.close();
        };
        
        // Auto-close after 5 seconds
        setTimeout(function() {
            notification.close();
        }, 5000);
    } catch (e) {
        console.log('Browser notification error:', e);
    }
}

function formatChatTime(timestamp) {
    try {
        const msgTime = new Date(timestamp.replace(' ', 'T') + (timestamp.includes('Z') ? '' : 'Z'));
        const now = new Date();
        const diffMs = now - msgTime;
        const diffMins = Math.floor(diffMs / 60000);
        
        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return diffMins + ' min ago';
        
        const diffHours = Math.floor(diffMins / 60);
        if (diffHours < 24) return diffHours + ' hour' + (diffHours > 1 ? 's' : '') + ' ago';
        
        return msgTime.toLocaleDateString();
    } catch (e) {
        return 'Just now';
    }
}

// Global function to toggle chat sound
function toggleChatSound(enabled) {
    chatSoundEnabled = enabled;
    console.log('Chat notification sound ' + (enabled ? 'enabled' : 'disabled'));
}
