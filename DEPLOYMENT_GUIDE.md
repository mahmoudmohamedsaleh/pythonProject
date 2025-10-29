# PythonAnywhere Deployment Guide

## ✅ Your System is Ready for Deployment!

All passwords have been encrypted and all routes are protected. Follow these steps to deploy to PythonAnywhere.

---

## 📋 Pre-Deployment Checklist

✅ **All passwords encrypted** (41 passwords migrated to scrypt hashing)  
✅ **All 130 routes protected** with authentication  
✅ **Database ready** (ProjectStatus.db with encrypted passwords)  
✅ **Migration script available** (migrate_passwords.py)

---

## 🚀 Deployment Steps

### Step 1: Upload Files to PythonAnywhere

1. **Go to PythonAnywhere Dashboard** → Files
2. **Upload these files:**
   - `app.py` (main Flask application)
   - `ProjectStatus.db` (database with encrypted passwords)
   - `templates/` folder (all HTML templates)
   - `static/` or `Static/` folder (CSS, JS, images)
   - `migrate_passwords.py` (in case you need it later)

### Step 2: Install Python Packages

1. Open a **Bash console** on PythonAnywhere
2. Install required packages:
   ```bash
   pip3 install flask pandas openpyxl xlsxwriter reportlab requests werkzeug
   ```

### Step 3: Configure WSGI File

1. Go to **Web** tab → Your web app
2. Edit the **WSGI configuration file**
3. Replace the contents with:
   ```python
   import sys
   import os
   
   # Add your project directory to the sys.path
   path = '/home/YOUR_USERNAME/YOUR_PROJECT_FOLDER'
   if path not in sys.path:
       sys.path.append(path)
   
   # Set environment variables
   os.environ['SECRET_KEY'] = 'your-secret-key-here-change-this'
   os.environ['FLASK_DEBUG'] = '0'
   
   # Import Flask app
   from app import app as application
   ```
4. **Replace:**
   - `YOUR_USERNAME` with your PythonAnywhere username
   - `YOUR_PROJECT_FOLDER` with your project folder name
   - `your-secret-key-here-change-this` with a strong random secret key

### Step 4: Set Static Files Path

1. In **Web** tab → **Static files** section
2. Add static file mapping:
   - **URL**: `/static/`
   - **Directory**: `/home/YOUR_USERNAME/YOUR_PROJECT_FOLDER/static/`

### Step 5: Reload Web App

1. Click **Reload** button in Web tab
2. Your app should now be live!

---

## 🔐 Login Instructions

### For All Users:

**Use the SAME password you had before!**

The system has automatically encrypted all passwords, but users log in with their **original plaintext password**.

#### Example:
- **Before migration**: Database showed password as `ajt512i3456`
- **After migration**: Database shows encrypted hash `scrypt:32768:8:1$...`
- **Login with**: `ajt512i3456` (the original password)

### Test Login:

From your database screenshot, here are some example logins:

| Username | Password (use this) |
|----------|-------------------|
| M.saleh  | ejt512i3456 |
| samar.h  | ejt$41@1 |
| A.Ashraf | cutcofeX |
| M.Farouk | MF1234567 |

---

## 🔧 Troubleshooting

### Problem: "Invalid username or password"

**Solution 1: Re-run migration on PythonAnywhere**
```bash
# In PythonAnywhere bash console
cd /home/YOUR_USERNAME/YOUR_PROJECT_FOLDER
python3 migrate_passwords.py
```

**Solution 2: Check database file**
- Make sure you uploaded the CORRECT `ProjectStatus.db` file
- The database should have encrypted passwords (starting with `scrypt:`)

### Problem: "Module not found" errors

**Solution: Install missing packages**
```bash
pip3 install flask pandas openpyxl xlsxwriter reportlab requests werkzeug
```

### Problem: Static files not loading

**Solution: Check static files mapping**
1. Web tab → Static files
2. Make sure URL is `/static/` and directory points to correct folder
3. If your folder is named `Static` (capital S), update the path accordingly

---

## 🔒 Security Recommendations

### 1. Generate Strong Secret Key

```python
# In Python console:
import secrets
print(secrets.token_hex(32))
# Use this output as your SECRET_KEY in WSGI file
```

### 2. Disable Debug Mode

Make sure in WSGI file:
```python
os.environ['FLASK_DEBUG'] = '0'
```

### 3. Regular Backups

- Download `ProjectStatus.db` regularly from PythonAnywhere
- Keep backup copies of your database

---

## 📧 Email Configuration (Optional)

If you want password reset emails to work:

1. Add these environment variables in WSGI file:
   ```python
   os.environ['EMAIL_PROVIDER'] = 'resend'
   os.environ['RESEND_API_KEY'] = 'your-resend-api-key'
   os.environ['SENDER_EMAIL'] = 'noreply@yourdomain.com'
   ```

2. Verify your domain with Resend

**Alternative:** Use the **Admin Password Reset** feature:
- Admins can reset any user's password from `/manage_users`
- No email configuration required!

---

## ✅ Verification Checklist

After deployment, verify these work:

- [ ] Can access login page
- [ ] Can log in with encrypted password
- [ ] Unauthorized pages redirect to login
- [ ] Dashboard loads after login
- [ ] Static files (images, CSS) load correctly
- [ ] Permission system works (users see only allowed pages)
- [ ] Admin features work (for General Manager/Technical Team Leader)

---

## 📞 Support

If you encounter issues:

1. **Check PythonAnywhere error logs**:
   - Web tab → Log files → Error log
   
2. **Check server log**:
   - Web tab → Log files → Server log

3. **Common fixes**:
   - Reload web app
   - Check file paths in WSGI config
   - Verify all packages installed
   - Ensure database file uploaded correctly

---

## 🎉 Success!

Once deployed, your CRM system will be:
- ✅ Fully secured with encrypted passwords
- ✅ Protected routes requiring authentication
- ✅ Page-level permissions enforced
- ✅ Ready for production use!

Your app URL will be: `https://YOUR_USERNAME.pythonanywhere.com`

Enjoy your secure CRM system! 🚀
