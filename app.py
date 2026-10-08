from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify, send_file, send_from_directory
from datetime import datetime
import sqlite3
import io

app = Flask(__name__)
app.secret_key = 'funaab_geophysics_secure_portal_2026_key'

DEPARTMENT_PASSWORD = "geo254k"
ADMIN_PASSCODE = "geo278k"
DB_NAME = "geophysics.db"

def init_db():
    conn = sqlite3.connect(DB_NAME, timeout=30.0)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS announcements (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, content TEXT NOT NULL, date TEXT NOT NULL, urgent INTEGER DEFAULT 0, likes INTEGER DEFAULT 0, helpful INTEGER DEFAULT 0, important INTEGER DEFAULT 0)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY AUTOINCREMENT, announcement_id INTEGER, author TEXT NOT NULL, text TEXT NOT NULL, date TEXT NOT NULL, FOREIGN KEY (announcement_id) REFERENCES announcements (id) ON DELETE CASCADE)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS materials (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, course_code TEXT NOT NULL, filename TEXT NOT NULL, mimetype TEXT NOT NULL, file_data BLOB NOT NULL, date TEXT NOT NULL)''')

    cursor.execute('SELECT COUNT(*) FROM announcements')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO announcements (title, content, date, urgent, likes, helpful, important) VALUES (?, ?, ?, ?, ?, ?, ?)',
                       ("Welcome to FUNAAB Geophysics Official Portal", "Official 2026 academic broadcast channel for the Department of Geophysics, FUNAAB.", datetime.now().strftime("%b %d, %Y - %I:%M %p"), 0, 42, 28, 35))
        cursor.execute('INSERT INTO comments (announcement_id, author, text, date) VALUES (?, ?, ?, ?)', (1, "Class Rep", "Department portal active! 🌍⚡", "Oct 7"))
    conn.commit()
    conn.close()

init_db()

def query_db(query, args=(), one=False):
    conn = sqlite3.connect(DB_NAME, timeout=30.0)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, args)
    rv = cursor.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def modify_db(query, args=()):
    conn = sqlite3.connect(DB_NAME, timeout=30.0)
    cursor = conn.cursor()
    cursor.execute(query, args)
    conn.commit()
    conn.close()

@app.route('/manifest.json')
def manifest():
    return jsonify({
        "name": "FUNAAB Geophysics Portal",
        "short_name": "GeoPortal",
        "start_url": "/home",
        "display": "standalone",
        "background_color": "#022c22",
        "theme_color": "#10b981"
    })

@app.route('/sw.js')
def service_worker():
    return app.response_class("self.addEventListener('install', e => self.skipWaiting()); self.addEventListener('activate', e => self.clients.claim());", mimetype='application/javascript')

@app.route('/OneSignalSDKWorker.js')
def onesignal_worker():
    return send_from_directory('static', 'OneSignalSDKWorker.js')

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        pwd = request.form.get('password')
        if pwd == DEPARTMENT_PASSWORD:
            session['authenticated'] = True
            session['is_admin'] = False
            return redirect(url_for('home'))
        elif pwd == ADMIN_PASSCODE:
            session['authenticated'] = True
            session['is_admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            error = "Invalid Access Key. Access Denied."
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FUNAAB Geophysics - Login</title><link rel="manifest" href="/manifest.json">
        <script src="https://cdn.onesignal.com/sdks/web/v16/OneSignalSDK.page.js" defer></script>
        <script>
          window.OneSignalDeferred = window.OneSignalDeferred || [];
          window.OneSignalDeferred.push(async function(OneSignal) {
            await OneSignal.init({
              appId: "YOUR-ONESIGNAL-APP-ID",
            });
          });
        </script>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body { background: #022c22; color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background: linear-gradient(135deg, #022c22, #064e3b, #111827); position: relative; overflow: hidden; }
            .card { background: rgba(2, 44, 34, 0.9); backdrop-filter: blur(20px); padding: 40px 25px; border-radius: 28px; box-shadow: 0 30px 60px rgba(0,0,0,0.8), 0 0 40px rgba(16, 185, 129, 0.25); width: 100%; max-width: 400px; border-top: 5px solid #34d399; text-align: center; border: 1px solid rgba(52, 211, 153, 0.4); z-index: 10; position: relative; }
            .geo-logo { width: 95px; height: 95px; border-radius: 50%; margin: 0 auto 18px auto; box-shadow: 0 0 25px rgba(52, 211, 153, 0.6); border: 2px solid #34d399; background: #ffffff; display: flex; flex-direction: column; align-items: center; justify-content: center; font-weight: 900; color: #022c22; font-size: 14px; letter-spacing: 1px; }
            .geo-logo span { font-size: 10px; color: #059669; margin-top: 2px; }
            .badge { background: rgba(52, 211, 153, 0.2); color: #34d399; font-size: 11px; font-weight: 800; padding: 6px 14px; border-radius: 30px; display: inline-block; margin-bottom: 15px; border: 1px solid rgba(52, 211, 153, 0.4); letter-spacing: 1px; }
            h2 { margin-bottom: 8px; color: #ffffff; font-size: 24px; font-weight: 900; }
            p { color: #d1d5db; font-size: 13px; margin-bottom: 25px; line-height: 1.5; }
            input { width: 100%; padding: 15px; margin-bottom: 18px; background: rgba(3, 7, 18, 0.85); border: 1px solid #10b981; color: #fff; border-radius: 14px; font-size: 16px; text-align: center; letter-spacing: 3px; outline: none; }
            input:focus { border-color: #34d399; box-shadow: 0 0 20px rgba(52, 211, 153, 0.5); }
            button { width: 100%; padding: 15px; background: linear-gradient(135deg, #10b981, #059669); color: #fff; border: none; font-weight: 800; border-radius: 14px; font-size: 16px; cursor: pointer; box-shadow: 0 8px 25px rgba(16, 185, 129, 0.5); }
            .error { background: rgba(239, 68, 68, 0.2); border: 1px solid rgba(239, 68, 68, 0.4); color: #fca5a5; font-size: 13px; padding: 12px; border-radius: 10px; margin-bottom: 20px; font-weight: 700; }
            .footer-note { margin-top: 15px; font-size: 11px; color: #9ca3af; font-weight: 600; }
        </style>
    </head>
    <body>
        <div class="card">
            <div class="geo-logo">FUNAAB<span>GEOPHYSICS</span></div>
            <div class="badge">DEPARTMENT OF GEOPHYSICS</div>
            <h2>Departmental Portal</h2>
            <p>Enter your department access password to explore.</p>
            {% if error %}<div class="error">{{ error }}</div>{% endif %}
            <form method="POST">
                <input type="password" name="password" placeholder="••••••••" required autofocus>
                <button type="submit">Unlock Portal 🚀</button>
            </form>
            <div class="footer-note">Federal University of Agriculture, Abeokuta</div>
        </div>
        <script>if ('serviceWorker' in navigator) { navigator.serviceWorker.register('/sw.js').catch(err => {}); }</script>
    </body>
    </html>
    ''', error=error)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        passcode = request.form.get('passcode')
        if passcode == ADMIN_PASSCODE:
            session['authenticated'] = True
            session['is_admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            error = "Strict Admin Access Denied. Incorrect Passcode."
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FUNAAB Geophysics - Admin Gateway</title><link rel="manifest" href="/manifest.json">
        <script src="https://cdn.onesignal.com/sdks/web/v16/OneSignalSDK.page.js" defer></script>
        <script>
          window.OneSignalDeferred = window.OneSignalDeferred || [];
          window.OneSignalDeferred.push(async function(OneSignal) {
            await OneSignal.init({
              appId: "YOUR-ONESIGNAL-APP-ID",
            });
          });
        </script>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body { background: #022c22; color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background: linear-gradient(135deg, #022c22, #064e3b, #111827); position: relative; overflow: hidden; }
            .card { background: rgba(2, 44, 34, 0.9); backdrop-filter: blur(20px); padding: 40px 25px; border-radius: 28px; box-shadow: 0 30px 60px rgba(0,0,0,0.8), 0 0 40px rgba(16, 185, 129, 0.25); width: 100%; max-width: 400px; border-top: 5px solid #10b981; text-align: center; border: 1px solid rgba(52, 211, 153, 0.4); z-index: 10; position: relative; }
            .geo-logo { width: 95px; height: 95px; border-radius: 50%; margin: 0 auto 18px auto; box-shadow: 0 0 30px rgba(16, 185, 129, 0.6); border: 2px solid #34d399; background: #ffffff; display: flex; flex-direction: column; align-items: center; justify-content: center; font-weight: 900; color: #022c22; font-size: 14px; letter-spacing: 1px; }
            .geo-logo span { font-size: 10px; color: #059669; margin-top: 2px; }
            .badge { background: rgba(16, 185, 129, 0.2); color: #34d399; font-size: 11px; font-weight: 800; padding: 6px 14px; border-radius: 30px; display: inline-block; margin-bottom: 15px; border: 1px solid rgba(52, 211, 153, 0.4); letter-spacing: 1px; }
            h2 { margin-bottom: 8px; color: #ffffff; font-size: 24px; font-weight: 900; }
            p { color: #d1d5db; font-size: 13px; margin-bottom: 25px; line-height: 1.5; }
            input { width: 100%; padding: 15px; margin-bottom: 18px; background: rgba(3, 7, 18, 0.85); border: 1px solid #10b981; color: #fff; border-radius: 14px; font-size: 16px; text-align: center; letter-spacing: 3px; outline: none; }
            input:focus { border-color: #34d399; box-shadow: 0 0 20px rgba(16, 185, 129, 0.5); }
            button { width: 100%; padding: 15px; background: linear-gradient(135deg, #10b981, #059669); color: #fff; border: none; font-weight: 800; border-radius: 14px; font-size: 16px; cursor: pointer; box-shadow: 0 8px 25px rgba(16, 185, 129, 0.5); }
            .back-link { margin-top: 18px; display: block; font-size: 12px; color: #34d399; text-decoration: none; font-weight: 700; }
            .back-link:hover { text-decoration: underline; color: #6ee7b7; }
            .footer-note { margin-top: 15px; font-size: 11px; color: #9ca3af; font-weight: 600; }
        </style>
    </head>
    <body>
        <div class="card">
            <div class="geo-logo">FUNAAB<span>GEOPHYSICS</span></div>
            <div class="badge">RESTRICTED ACCESS</div>
            <h2>Admin Login Portal</h2>
            <p>Enter strict admin passcode to manage broadcasts.</p>
            {% if error %}<div class="error">{{ error }}</div>{% endif %}
            <form method="POST">
                <input type="password" name="passcode" placeholder="••••••••" required autofocus>
                <button type="submit">Verify & Enter Admin ⚡</button>
            </form>
            <a href="/" class="back-link">← Back to Student Portal</a>
            <div class="footer-note">FUNAAB Geophysics Department</div>
        </div>
    </body>
    </html>
    ''', error=error)

@app.route('/home')
def home():
    if not session.get('authenticated'): return redirect(url_for('login'))
    is_admin = session.get('is_admin', False)
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FUNAAB Geophysics - Home</title><link rel="manifest" href="/manifest.json">
        <script src="https://cdn.onesignal.com/sdks/web/v16/OneSignalSDK.page.js" defer></script>
        <script>
          window.OneSignalDeferred = window.OneSignalDeferred || [];
          window.OneSignalDeferred.push(async function(OneSignal) {
            await OneSignal.init({
              appId: "YOUR-ONESIGNAL-APP-ID",
            });
          });
        </script>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body { background: #022c22; color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; padding: 20px; padding-bottom: 100px; background: linear-gradient(135deg, #022c22, #064e3b, #111827); text-align: center; position: relative; overflow: hidden; }
            .hero-card { background: rgba(2, 44, 34, 0.9); backdrop-filter: blur(20px); padding: 45px 30px; border-radius: 30px; border: 1px solid rgba(52, 211, 153, 0.4); box-shadow: 0 30px 60px rgba(0,0,0,0.85), 0 0 50px rgba(16, 185, 129, 0.2); max-width: 480px; width: 100%; position: relative; overflow: hidden; z-index: 10; }
            .hero-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 5px; background: linear-gradient(90deg, #10b981, #34d399, #ffffff); }
            .geo-logo { width: 95px; height: 95px; border-radius: 50%; margin: 0 auto 18px auto; box-shadow: 0 0 30px rgba(16, 185, 129, 0.6); border: 2px solid #34d399; background: #ffffff; display: flex; flex-direction: column; align-items: center; justify-content: center; font-weight: 900; color: #022c22; font-size: 14px; letter-spacing: 1px; }
            .geo-logo span { font-size: 10px; color: #059669; margin-top: 2px; }
            .school-badge { background: rgba(52, 211, 153, 0.2); color: #34d399; font-size: 11px; font-weight: 800; padding: 6px 16px; border-radius: 30px; display: inline-block; margin-bottom: 18px; border: 1px solid rgba(52, 211, 153, 0.4); letter-spacing: 1px; text-transform: uppercase; }
            h1 { font-size: 24px; font-weight: 900; color: #fff; margin-bottom: 8px; line-height: 1.3; }
            h2 { font-size: 15px; font-weight: 700; color: #6ee7b7; margin-bottom: 18px; letter-spacing: 0.5px; }
            p { font-size: 13px; color: #d1d5db; line-height: 1.6; margin-bottom: 30px; }
            .enter-btn { display: inline-block; background: linear-gradient(135deg, #10b981, #059669); color: #fff; padding: 14px 32px; font-weight: 800; border-radius: 14px; text-decoration: none; font-size: 15px; box-shadow: 0 8px 25px rgba(16, 185, 129, 0.5); }
            .enter-btn:hover { transform: scale(1.03); }
            .bottom-taskbar { position: fixed; bottom: 0; left: 0; right: 0; background: rgba(2, 44, 34, 0.95); backdrop-filter: blur(15px); border-top: 1px solid rgba(52, 211, 153, 0.3); padding: 12px 10px; display: flex; justify-content: space-around; align-items: center; z-index: 1000; box-shadow: 0 -5px 25px rgba(0,0,0,0.7); }
            .task-item { background: transparent; border: none; color: #9ca3af; font-size: 11px; font-weight: 700; display: flex; flex-direction: column; align-items: center; gap: 4px; cursor: pointer; text-decoration: none; }
            .task-item span { font-size: 18px; }
            .task-item:hover, .task-item.active { color: #34d399; }
            .modal-overlay { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.85); z-index: 2000; justify-content: center; align-items: center; padding: 20px; }
            .modal-card { background: #022c22; border: 1px solid #34d399; padding: 30px 25px; border-radius: 20px; max-width: 360px; width: 100%; text-align: center; box-shadow: 0 15px 50px rgba(0,0,0,0.9); }
            .modal-card h3 { color: #34d399; font-size: 20px; margin-bottom: 12px; }
            .modal-card p { color: #d1d5db; font-size: 14px; line-height: 1.5; margin-bottom: 20px; text-align: left; }
            .modal-card ol { text-align: left; margin-left: 20px; color: #d1d5db; font-size: 13px; margin-bottom: 25px; line-height: 1.6; }
            .close-modal { background: linear-gradient(135deg, #10b981, #059669); color: #fff; border: none; padding: 12px 24px; font-weight: 800; border-radius: 12px; cursor: pointer; width: 100%; }
        </style>
    </head>
    <body>
        <div class="hero-card">
            <div class="geo-logo">FUNAAB<span>GEOPHYSICS</span></div>
            <div class="school-badge">Academic Session 2026</div>
            <h1>Federal University of Agriculture, Abeokuta</h1>
            <h2>Department of Geophysics</h2>
            <p>Welcome to your official departmental broadcast hub. Access real-time announcements, course materials, and verified student feedback.</p>
            <a href="/dashboard" class="enter-btn">Open Announcements Feed 🚀</a>
        </div>
        <div id="installModal" class="modal-overlay">
            <div class="modal-card">
                <h3>📲 Download Portal App</h3>
                <p>Install this website directly onto your phone home screen for instant access like a real app:</p>
                <ol>
                    <li>Tap your browser menu button (<b>3 dots</b> at top right).</li>
                    <li>Select <b>"Add to Home Screen"</b> or <b>"Install App"</b>.</li>
                    <li>Confirm and enjoy lightning-fast offline-ready access!</li>
                </ol>
                <button class="close-modal" onclick="closeModal()">Got It! 👍</button>
            </div>
        </div>
        <div class="bottom-taskbar">
            <a href="/home" class="task-item active"><span>🏠</span> Home</a>
            <a href="/dashboard" class="task-item"><span>📢</span> Feed</a>
            <a href="/materials" class="task-item"><span>📚</span> Materials</a>
            {% if is_admin %}<a href="/admin/dashboard" class="task-item"><span>✍️</span> Admin Portal</a>{% endif %}
            <button class="task-item" onclick="openModal()"><span>📲</span> Download</button>
        </div>
        <script>
            if ('serviceWorker' in navigator) { navigator.serviceWorker.register('/sw.js').catch(err => {}); }
            let deferredPrompt;
            window.addEventListener('beforeinstallprompt', (e) => { e.preventDefault(); deferredPrompt = e; });
            function openModal() {
                if (deferredPrompt) {
                    deferredPrompt.prompt();
                    deferredPrompt.userChoice.then(r => { deferredPrompt = null; });
                } else {
                    document.getElementById('installModal').style.display = 'flex';
                }
            }
            function closeModal() { document.getElementById('installModal').style.display = 'none'; }
        </script>
    </body>
    </html>
    ''', is_admin=is_admin)

@app.route('/dashboard')
def dashboard():
    if not session.get('authenticated'): return redirect(url_for('login'))
    is_admin = session.get('is_admin', False)
    raw_announcements = query_db('SELECT * FROM announcements ORDER BY id DESC')
    announcements = []
    for row in raw_announcements:
        ann_id = row['id']
        comments = query_db('SELECT * FROM comments WHERE announcement_id = ? ORDER BY id ASC', (ann_id,))
        announcements.append({
            "id": ann_id, "title": row['title'], "content": row['content'], "date": row['date'], "urgent": row['urgent'],
            "reactions": {"like": row['likes'], "helpful": row['helpful'], "important": row['important']},
            "comments": [{"author": c['author'], "text": c['text'], "date": c['date']} for c in comments]
        })
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FUNAAB Geophysics - Announcements</title><link rel="manifest" href="/manifest.json">
        <script src="https://cdn.onesignal.com/sdks/web/v16/OneSignalSDK.page.js" defer></script>
        <script>
          window.OneSignalDeferred = window.OneSignalDeferred || [];
          window.OneSignalDeferred.push(async function(OneSignal) {
            await OneSignal.init({
              appId: "YOUR-ONESIGNAL-APP-ID",
            });
          });
        </script>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body { background: #022c22; color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding-bottom: 95px; background: linear-gradient(135deg, #022c22, #064e3b, #111827); min-height: 100vh; position: relative; }
            header { background: rgba(2, 44, 34, 0.9); backdrop-filter: blur(15px); padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(52, 211, 153, 0.3); position: sticky; top: 0; z-index: 100; box-shadow: 0 4px 20px rgba(0,0,0,0.6); }
            .brand { display: flex; align-items: center; gap: 12px; text-decoration: none; }
            .logo-geo { width: 42px; height: 42px; border-radius: 50%; box-shadow: 0 0 15px rgba(52, 211, 153, 0.6); border: 2px solid #34d399; background: #ffffff; display: flex; flex-direction: column; align-items: center; justify-content: center; font-weight: 900; color: #022c22; font-size: 10px; letter-spacing: 0.5px; }
            .logo-geo span { font-size: 7px; color: #059669; }
            h1 { font-size: 15px; color: #fff; font-weight: 800; }
            span.sub { display: block; font-size: 10px; color: #34d399; font-weight: 700; }
            .nav-actions { display: flex; align-items: center; gap: 10px; }
            .badge-admin { background: rgba(239, 68, 68, 0.25); color: #fca5a5; font-size: 11px; padding: 6px 12px; border-radius: 8px; font-weight: 700; border: 1px solid rgba(239, 68, 68, 0.4); text-decoration: none; }
            .logout { color: #fca5a5; text-decoration: none; font-size: 12px; font-weight: 700; background: rgba(239, 68, 68, 0.15); padding: 6px 12px; border-radius: 8px; border: 1px solid rgba(239, 68, 68, 0.3); }
            .container { max-width: 680px; margin: 24px auto; padding: 0 16px; position: relative; z-index: 2; }
            .section-title { font-size: 13px; font-weight: 800; color: #34d399; margin-bottom: 18px; text-transform: uppercase; letter-spacing: 1px; display: flex; align-items: center; gap: 8px; }
            .notice-card { background: #ffffff; color: #111827; border-radius: 20px; padding: 22px; margin-bottom: 22px; border: 1px solid #d1d5db; border-left: 6px solid #10b981; box-shadow: 0 12px 35px rgba(0,0,0,0.3); position: relative; }
            .notice-card.urgent { border-left-color: #ef4444; }
            .notice-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; }
            .notice-title { font-size: 18px; font-weight: 800; color: #111827; line-height: 1.3; }
            .tag-urgent { background: rgba(239, 68, 68, 0.15); color: #dc2626; font-size: 10px; font-weight: 800; padding: 4px 10px; border-radius: 6px; border: 1px solid rgba(239, 68, 68, 0.3); }
            .notice-date { font-size: 11px; color: #4b5563; margin-bottom: 14px; font-weight: 600; }
            .notice-body { font-size: 14px; color: #1f2937; line-height: 1.6; margin-bottom: 18px; white-space: pre-wrap; }
            .reactions-bar { display: flex; gap: 10px; margin-bottom: 18px; padding-bottom: 14px; border-bottom: 1px solid #e5e7eb; flex-wrap: wrap; }
            .reaction-btn { background: #f3f4f6; border: 1px solid #d1d5db; color: #374151; padding: 8px 16px; border-radius: 20px; font-size: 12px; font-weight: 700; cursor: pointer; }
            .reaction-btn:hover { background: #e5e7eb; border-color: #9ca3af; color: #111827; }
            .reaction-btn.reacted { background: #10b981; border-color: #059669; color: #fff; }
            .comments-section { background: #f9fafb; padding: 16px; border-radius: 14px; border: 1px solid #e5e7eb; }
            .comments-title { font-size: 12px; font-weight: 800; color: #047857; margin-bottom: 12px; text-transform: uppercase; }
            .comment-item { font-size: 13px; margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px solid #e5e7eb; }
            .comment-author { color: #047857; font-weight: 800; margin-right: 8px; }
            .comment-text { color: #374151; }
            .comment-form { display: flex; gap: 8px; margin-top: 14px; flex-wrap: wrap; align-items: center; }
            .comment-form input { padding: 10px 14px; background: #ffffff; border: 1px solid #d1d5db; color: #111827; border-radius: 10px; font-size: 13px; outline: none; }
            .comment-form input:focus { border-color: #10b981; }
            .locked-user-badge { background: #ecfdf5; border: 1px solid #10b981; color: #047857; padding: 9px 14px; border-radius: 10px; font-size: 12px; font-weight: 800; display: flex; align-items: center; gap: 6px; }
            .bottom-taskbar { position: fixed; bottom: 0; left: 0; right: 0; background: rgba(2, 44, 34, 0.95); backdrop-filter: blur(15px); border-top: 1px solid rgba(52, 211, 153, 0.3); padding: 12px 10px; display: flex; justify-content: space-around; align-items: center; z-index: 1000; box-shadow: 0 -5px 25px rgba(0,0,0,0.7); }
            .task-item { background: transparent; border: none; color: #9ca3af; font-size: 11px; font-weight: 700; display: flex; flex-direction: column; align-items: center; gap: 4px; cursor: pointer; text-decoration: none; }
            .task-item span { font-size: 18px; }
            .task-item:hover, .task-item.active { color: #34d399; }
            .modal-overlay { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.85); z-index: 2000; justify-content: center; align-items: center; padding: 20px; }
            .modal-card { background: #022c22; border: 1px solid #34d399; padding: 30px 25px; border-radius: 20px; max-width: 360px; width: 100%; text-align: center; }
            .modal-card h3 { color: #34d399; font-size: 20px; margin-bottom: 12px; }
            .modal-card p { color: #d1d5db; font-size: 14px; line-height: 1.5; margin-bottom: 20px; text-align: left; }
            .modal-card ol { text-align: left; margin-left: 20px; color: #d1d5db; font-size: 13px; margin-bottom: 25px; line-height: 1.6; }
            .close-modal { background: linear-gradient(135deg, #10b981, #059669); color: #fff; border: none; padding: 12px 24px; font-weight: 800; border-radius: 12px; cursor: pointer; width: 100%; }
        </style>
    </head>
    <body>
        <header>
            <a href="/home" class="brand">
                <div class="logo-geo">FUNAAB<span>GEO</span></div>
                <div>
                    <h1>FUNAAB Geophysics</h1>
                    <span class="sub">2026 Official Portal</span>
                </div>
            </a>
            <div class="nav-actions">
                {% if is_admin %}
                    <a href="/admin/dashboard" class="badge-admin">👑 ADMIN PORTAL</a>
                {% endif %}
                <a href="/logout" class="logout">Logout</a>
            </div>
        </header>
        <div class="container">
            <div class="section-title">⚡ Official Announcements Feed</div>
            <div>
                {% for notice in announcements %}
                <div class="notice-card {% if notice.urgent %}urgent{% endif %}" id="notice-{{ notice.id }}">
                    <div class="notice-header">
                        <div class="notice-title">{{ notice.title }}</div>
                        {% if notice.urgent %}<div class="tag-urgent">URGENT</div>{% endif %}
                    </div>
                    <div class="notice-date">Published: {{ notice.date }}</div>
                    <div class="notice-body">{{ notice.content }}</div>
                    <div class="reactions-bar">
                        <button class="reaction-btn" id="btn-like-{{ notice.id }}" onclick="react({{ notice.id }}, 'like')">👍 Like <span id="like-{{ notice.id }}">{{ notice.reactions.like }}</span></button>
                        <button class="reaction-btn" id="btn-helpful-{{ notice.id }}" onclick="react({{ notice.id }}, 'helpful')">🔥 Helpful <span id="helpful-{{ notice.id }}">{{ notice.reactions.helpful }}</span></button>
                        <button class="reaction-btn" id="btn-important-{{ notice.id }}" onclick="react({{ notice.id }}, 'important')">💡 Important <span id="important-{{ notice.id }}">{{ notice.reactions.important }}</span></button>
                    </div>
                    <div class="comments-section">
                        <div class="comments-title">💬 Student Feedback & Comments ({{ notice.comments|length }})</div>
                        <div id="comments-list-{{ notice.id }}">
                            {% for comm in notice.comments %}
                            <div class="comment-item"><span class="comment-author">{{ comm.author }}:</span><span class="comment-text">{{ comm.text }}</span></div>
                            {% endfor %}
                        </div>
                        <form class="comment-form" onsubmit="addComment(event, {{ notice.id }})">
                            <div id="author-container-{{ notice.id }}" style="flex: 1; min-width: 140px;">
                                <input type="text" id="author-{{ notice.id }}" placeholder="Your Name / Alias" style="width: 100%;" required>
                            </div>
                            <input type="text" id="text-{{ notice.id }}" placeholder="Drop feedback..." style="flex: 2; min-width: 180px;" required>
                            <button type="submit" style="background: linear-gradient(135deg, #10b981, #059669); color: #fff; border: none; padding: 10px 18px; font-weight: 800; border-radius: 10px; cursor: pointer;">Send</button>
                        </form>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        <div id="installModal" class="modal-overlay">
            <div class="modal-card">
                <h3>📲 Download Portal App</h3>
                <p>Install this website directly onto your phone home screen for instant access like a real app:</p>
                <ol>
                    <li>Tap your browser menu button (<b>3 dots</b> at top right).</li>
                    <li>Select <b>"Add to Home Screen"</b> or <b>"Install App"</b>.</li>
                    <li>Confirm and enjoy lightning-fast offline-ready access!</li>
                </ol>
                <button class="close-modal" onclick="closeModal()">Got It! 👍</button>
            </div>
        </div>
        <div class="bottom-taskbar">
            <a href="/home" class="task-item"><span>🏠</span> Home</a>
            <a href="/dashboard" class="task-item active"><span>📢</span> Feed</a>
            <a href="/materials" class="task-item"><span>📚</span> Materials</a>
            {% if is_admin %}<a href="/admin/dashboard" class="task-item"><span>✍️</span> Admin Portal</a>{% endif %}
            <button class="task-item" onclick="openModal()"><span>📲</span> Download</button>
        </div>
        <script>
            if ('serviceWorker' in navigator) { navigator.serviceWorker.register('/sw.js').catch(err => {}); }
            let deferredPrompt;
            window.addEventListener('beforeinstallprompt', (e) => { e.preventDefault(); deferredPrompt = e; });
            function openModal() {
                if (deferredPrompt) {
                    deferredPrompt.prompt();
                    deferredPrompt.userChoice.then(r => { deferredPrompt = null; });
                } else {
                    document.getElementById('installModal').style.display = 'flex';
                }
            }
            function closeModal() { document.getElementById('installModal').style.display = 'none'; }

            document.addEventListener("DOMContentLoaded", function() {
                let lockedUser = localStorage.getItem('funaab_geo_username');
                document.querySelectorAll('.comment-form').forEach(form => {
                    let noticeId = form.getAttribute('onsubmit').match(/\d+/)[0];
                    let authContainer = document.getElementById(`author-container-${noticeId}`);
                    if (lockedUser) {
                        authContainer.innerHTML = `<div class="locked-user-badge">🔒 <span>${lockedUser}</span></div>`;
                    } else {
                        let inputField = authContainer.querySelector('input');
                        inputField.addEventListener('blur', function() {
                            let val = inputField.value.trim();
                            if(val) { localStorage.setItem('funaab_geo_username', val); location.reload(); }
                        });
                    }
                });
                document.querySelectorAll('.reaction-btn').forEach(btn => {
                    if(localStorage.getItem(btn.id) === 'true') { btn.classList.add('reacted'); }
                });
            });

            function react(id, type) {
                let btnKey = `btn-${type}-${id}`;
                if(localStorage.getItem(btnKey) === 'true') { alert('⚠️ You have already reacted with ' + type + '!'); return; }
                fetch(`/react/${id}/${type}`, { method: 'POST' }).then(res => res.json()).then(data => {
                    document.getElementById(`${type}-${id}`).innerText = data[type];
                    let btn = document.getElementById(btnKey);
                    btn.classList.add('reacted');
                    localStorage.setItem(btnKey, 'true');
                });
            }

            function addComment(e, id) {
                e.preventDefault();
                let lockedUser = localStorage.getItem('funaab_geo_username');
                let authorInput = document.getElementById(`author-${id}`);
                let author = lockedUser ? lockedUser : (authorInput ? authorInput.value.trim() : "Student");
                if(!lockedUser && author) { localStorage.setItem('funaab_geo_username', author); lockedUser = author; }
                let text = document.getElementById(`text-${id}`).value;
                fetch(`/comment/${id}`, {
                    method: 'POST', headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ author, text })
                }).then(res => res.json()).then(data => {
                    let list = document.getElementById(`comments-list-${id}`);
                    list.innerHTML += `<div class="comment-item"><span class="comment-author">${data.author}:</span><span class="comment-text">${data.text}</span></div>`;
                    document.getElementById(`text-${id}`).value = '';
                    location.reload();
                });
            }
        </script>
    </body>
    </html>
    ''', announcements=announcements, is_admin=is_admin)

@app.route('/materials')
def materials():
    if not session.get('authenticated'): return redirect(url_for('login'))
    is_admin = session.get('is_admin', False)
    materials_list = query_db('SELECT id, title, course_code, mimetype, date FROM materials ORDER BY id DESC')
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FUNAAB Geophysics - Course Materials</title><link rel="manifest" href="/manifest.json">
        <script src="https://cdn.onesignal.com/sdks/web/v16/OneSignalSDK.page.js" defer></script>
        <script>
          window.OneSignalDeferred = window.OneSignalDeferred || [];
          window.OneSignalDeferred.push(async function(OneSignal) {
            await OneSignal.init({
              appId: "YOUR-ONESIGNAL-APP-ID",
            });
          });
        </script>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body { background: #022c22; color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding-bottom: 95px; background: linear-gradient(135deg, #022c22, #064e3b, #111827); min-height: 100vh; position: relative; }
            header { background: rgba(2, 44, 34, 0.9); backdrop-filter: blur(15px); padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(52, 211, 153, 0.3); position: sticky; top: 0; z-index: 100; box-shadow: 0 4px 20px rgba(0,0,0,0.6); }
            .brand { display: flex; align-items: center; gap: 12px; text-decoration: none; }
            .logo-geo { width: 42px; height: 42px; border-radius: 50%; box-shadow: 0 0 15px rgba(52, 211, 153, 0.6); border: 2px solid #34d399; background: #ffffff; display: flex; flex-direction: column; align-items: center; justify-content: center; font-weight: 900; color: #022c22; font-size: 10px; letter-spacing: 0.5px; }
            .logo-geo span { font-size: 7px; color: #059669; }
            h1 { font-size: 15px; color: #fff; font-weight: 800; }
            span.sub { display: block; font-size: 10px; color: #34d399; font-weight: 700; }
            .nav-actions { display: flex; align-items: center; gap: 10px; }
            .badge-admin { background: rgba(239, 68, 68, 0.25); color: #fca5a5; font-size: 11px; padding: 6px 12px; border-radius: 8px; font-weight: 700; border: 1px solid rgba(239, 68, 68, 0.4); text-decoration: none; }
            .logout { color: #fca5a5; text-decoration: none; font-size: 12px; font-weight: 700; background: rgba(239, 68, 68, 0.15); padding: 6px 12px; border-radius: 8px; border: 1px solid rgba(239, 68, 68, 0.3); }
            .container { max-width: 680px; margin: 24px auto; padding: 0 16px; position: relative; z-index: 2; }
            .section-title { font-size: 13px; font-weight: 800; color: #34d399; margin-bottom: 18px; text-transform: uppercase; letter-spacing: 1px; display: flex; align-items: center; gap: 8px; }
            .material-card { background: rgba(2, 44, 34, 0.9); backdrop-filter: blur(14px); border-radius: 20px; padding: 20px 22px; margin-bottom: 18px; border: 1px solid rgba(52, 211, 153, 0.3); border-left: 6px solid #34d399; box-shadow: 0 12px 35px rgba(0,0,0,0.6); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px; }
            .mat-info { flex: 1; min-width: 240px; }
            .course-code { background: rgba(52, 211, 153, 0.2); color: #34d399; font-size: 11px; font-weight: 800; padding: 4px 10px; border-radius: 6px; border: 1px solid rgba(52, 211, 153, 0.4); display: inline-block; margin-bottom: 8px; }
            .mat-title { font-size: 16px; font-weight: 800; color: #fff; margin-bottom: 6px; }
            .mat-date { font-size: 11px; color: #9ca3af; font-weight: 600; }
            .mat-actions { display: flex; gap: 10px; }
            .btn-action { background: linear-gradient(135deg, #10b981, #059669); color: #fff; text-decoration: none; padding: 10px 18px; font-weight: 800; border-radius: 10px; font-size: 13px; display: flex; align-items: center; gap: 6px; }
            .btn-action:hover { transform: scale(1.03); }
            .empty-box { background: rgba(2, 44, 34, 0.9); padding: 40px; border-radius: 20px; text-align: center; border: 1px dashed rgba(52, 211, 153, 0.3); color: #9ca3af; }
            .bottom-taskbar { position: fixed; bottom: 0; left: 0; right: 0; background: rgba(2, 44, 34, 0.95); backdrop-filter: blur(15px); border-top: 1px solid rgba(52, 211, 153, 0.3); padding: 12px 10px; display: flex; justify-content: space-around; align-items: center; z-index: 1000; box-shadow: 0 -5px 25px rgba(0,0,0,0.7); }
            .task-item { background: transparent; border: none; color: #9ca3af; font-size: 11px; font-weight: 700; display: flex; flex-direction: column; align-items: center; gap: 4px; cursor: pointer; text-decoration: none; }
            .task-item span { font-size: 18px; }
            .task-item:hover, .task-item.active { color: #34d399; }
            .modal-overlay { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.85); z-index: 2000; justify-content: center; align-items: center; padding: 20px; }
            .modal-card { background: #022c22; border: 1px solid #34d399; padding: 30px 25px; border-radius: 20px; max-width: 360px; width: 100%; text-align: center; }
            .modal-card h3 { color: #34d399; font-size: 20px; margin-bottom: 12px; }
            .modal-card p { color: #d1d5db; font-size: 14px; line-height: 1.5; margin-bottom: 20px; text-align: left; }
            .modal-card ol { text-align: left; margin-left: 20px; color: #d1d5db; font-size: 13px; margin-bottom: 25px; line-height: 1.6; }
            .close-modal { background: linear-gradient(135deg, #10b981, #059669); color: #fff; border: none; padding: 12px 24px; font-weight: 800; border-radius: 12px; cursor: pointer; width: 100%; }
        </style>
    </head>
    <body>
        <header>
            <a href="/home" class="brand">
                <div class="logo-geo">FUNAAB<span>GEO</span></div>
                <div>
                    <h1>FUNAAB Geophysics</h1>
                    <span class="sub">Course Materials Hub</span>
                </div>
            </a>
            <div class="nav-actions">
                {% if is_admin %}
                    <a href="/admin/dashboard" class="badge-admin">👑 ADMIN PORTAL</a>
                {% endif %}
                <a href="/logout" class="logout">Logout</a>
            </div>
        </header>
        <div class="container">
            <div class="section-title">📚 Official Course Materials & Handouts</div>
            {% if materials_list %}
                {% for mat in materials_list %}
                <div class="material-card">
                    <div class="mat-info">
                        <div class="course-code">{{ mat.course_code }}</div>
                        <div class="mat-title">{{ mat.title }}</div>
                        <div class="mat-date">Uploaded: {{ mat.date }} • Type: {{ mat.mimetype.split('/')[-1].upper() }}</div>
                    </div>
                    <div class="mat-actions">
                        <a href="/material/download/{{ mat.id }}" class="btn-action" target="_blank">📥 Download / View</a>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <div class="empty-box">
                    <p>📂 No course materials uploaded yet. Check back soon or contact your admin!</p>
                </div>
            {% endif %}
        </div>
        <div id="installModal" class="modal-overlay">
            <div class="modal-card">
                <h3>📲 Download Portal App</h3>
                <p>Install this website directly onto your phone home screen for instant access like a real app:</p>
                <ol>
                    <li>Tap your browser menu button (<b>3 dots</b> at top right).</li>
                    <li>Select <b>"Add to Home Screen"</b> or <b>"Install App"</b>.</li>
                    <li>Confirm and enjoy lightning-fast offline-ready access!</li>
                </ol>
                <button class="close-modal" onclick="closeModal()">Got It! 👍</button>
            </div>
        </div>
        <div class="bottom-taskbar">
            <a href="/home" class="task-item"><span>🏠</span> Home</a>
            <a href="/dashboard" class="task-item"><span>📢</span> Feed</a>
            <a href="/materials" class="task-item active"><span>📚</span> Materials</a>
            {% if is_admin %}<a href="/admin/dashboard" class="task-item"><span>✍️</span> Admin Portal</a>{% endif %}
            <button class="task-item" onclick="openModal()"><span>📲</span> Download</button>
        </div>
        <script>
            let deferredPrompt;
            window.addEventListener('beforeinstallprompt', (e) => { e.preventDefault(); deferredPrompt = e; });
            function openModal() {
                if (deferredPrompt) {
                    deferredPrompt.prompt();
                    deferredPrompt.userChoice.then(r => { deferredPrompt = null; });
                } else {
                    document.getElementById('installModal').style.display = 'flex';
                }
            }
            function closeModal() { document.getElementById('installModal').style.display = 'none'; }
        </script>
    </body>
    </html>
    ''', materials_list=materials_list, is_admin=is_admin)

@app.route('/material/download/<int:mat_id>')
def download_material(mat_id):
    if not session.get('authenticated'): return redirect(url_for('login'))
    mat = query_db('SELECT title, filename, mimetype, file_data FROM materials WHERE id = ?', (mat_id,), one=True)
    if mat:
        return send_file(io.BytesIO(mat['file_data']), mimetype=mat['mimetype'], download_name=mat['filename'], as_attachment=False)
    return "Material not found", 404

@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if not session.get('authenticated') or not session.get('is_admin'):
        return redirect(url_for('admin_login'))

    success_msg = None
    if request.method == 'POST':
        action_type = request.form.get('action_type')
        if action_type == 'announcement':
            title = request.form.get('title')
            content = request.form.get('content')
            urgent = 1 if request.form.get('urgent') == 'yes' else 0
            date_str = datetime.now().strftime("%b %d, %Y - %I:%M %p")
            modify_db('INSERT INTO announcements (title, content, date, urgent, likes, helpful, important) VALUES (?, ?, ?, ?, 0, 0, 0)', (title, content, date_str, urgent))
            success_msg = "Announcement broadcasted successfully!"
        elif action_type == 'material':
            title = request.form.get('mat_title')
            course_code = request.form.get('course_code').upper()
            file = request.files.get('file')
            if file and file.filename:
                filename = file.filename
                mimetype = file.mimetype
                file_data = file.read()
                date_str = datetime.now().strftime("%b %d, %Y")
                conn = sqlite3.connect(DB_NAME, timeout=30.0)
                cursor = conn.cursor()
                cursor.execute('INSERT INTO materials (title, course_code, filename, mimetype, file_data, date) VALUES (?, ?, ?, ?, ?, ?)',
                               (title, course_code, filename, mimetype, file_data, date_str))
                conn.commit()
                conn.close()
                success_msg = f"Course material ({course_code}) uploaded successfully!"
        elif action_type == 'delete_notice':
            notice_id = request.form.get('notice_id')
            modify_db('DELETE FROM comments WHERE announcement_id = ?', (notice_id,))
            modify_db('DELETE FROM announcements WHERE id = ?', (notice_id,))
            success_msg = "Announcement deleted successfully!"
        elif action_type == 'delete_material':
            mat_id = request.form.get('mat_id')
            modify_db('DELETE FROM materials WHERE id = ?', (mat_id,))
            success_msg = "Course material deleted successfully!"

    announcements = query_db('SELECT id, title, date FROM announcements ORDER BY id DESC')
    materials_list = query_db('SELECT id, title, course_code, date FROM materials ORDER BY id DESC')

    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FUNAAB Geophysics - Admin Control Panel</title><link rel="manifest" href="/manifest.json">
        <script src="https://cdn.onesignal.com/sdks/web/v16/OneSignalSDK.page.js" defer></script>
        <script>
          window.OneSignalDeferred = window.OneSignalDeferred || [];
          window.OneSignalDeferred.push(async function(OneSignal) {
            await OneSignal.init({
              appId: "YOUR-ONESIGNAL-APP-ID",
            });
          });
        </script>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body { background: #022c22; color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding-bottom: 95px; background: linear-gradient(135deg, #022c22, #064e3b, #111827); min-height: 100vh; position: relative; }
            header { background: rgba(2, 44, 34, 0.9); backdrop-filter: blur(15px); padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(239, 68, 68, 0.3); position: sticky; top: 0; z-index: 100; }
            .brand { display: flex; align-items: center; gap: 12px; text-decoration: none; }
            .logo-geo { width: 42px; height: 42px; border-radius: 50%; box-shadow: 0 0 15px rgba(239, 68, 68, 0.6); border: 2px solid #fca5a5; background: #ffffff; display: flex; flex-direction: column; align-items: center; justify-content: center; font-weight: 900; color: #022c22; font-size: 10px; letter-spacing: 0.5px; }
            .logo-geo span { font-size: 7px; color: #059669; }
            h1 { font-size: 15px; color: #fff; font-weight: 800; }
            span.sub { display: block; font-size: 10px; color: #fca5a5; font-weight: 700; }
            .container { max-width: 650px; margin: 30px auto; padding: 0 16px; position: relative; z-index: 2; }
            .admin-box { background: rgba(2, 44, 34, 0.9); padding: 28px; border-radius: 20px; border: 1px dashed #10b981; box-shadow: 0 12px 35px rgba(0,0,0,0.7); position: relative; overflow: hidden; margin-bottom: 25px; }
            .admin-box h3 { margin-bottom: 16px; color: #34d399; font-size: 18px; font-weight: 800; }
            input[type="text"], input[type="file"], textarea { width: 100%; padding: 14px; margin-bottom: 16px; background: rgba(3, 7, 18, 0.95); border: 1px solid #10b981; color: #fff; border-radius: 12px; font-family: inherit; font-size: 14px; outline: none; }
            input:focus, textarea:focus { border-color: #34d399; }
            textarea { height: 120px; resize: vertical; }
            .checkbox-label { font-size: 13px; display: flex; align-items: center; gap: 10px; margin-bottom: 20px; color: #d1d5db; font-weight: 600; cursor: pointer; }
            .btn-primary { background: linear-gradient(135deg, #10b981, #059669); color: #fff; border: none; padding: 14px 20px; font-weight: 800; border-radius: 12px; cursor: pointer; font-size: 15px; width: 100%; }
            .success-alert { background: rgba(16, 185, 129, 0.2); border: 1px solid rgba(16, 185, 129, 0.4); color: #34d399; padding: 12px; border-radius: 10px; margin-bottom: 20px; font-weight: 700; text-align: center; }
            .file-hint { font-size: 12px; color: #9ca3af; margin-top: -10px; margin-bottom: 16px; display: block; }
            .notice-manage-item { display: flex; justify-content: space-between; align-items: center; background: rgba(3, 7, 18, 0.75); padding: 12px 16px; border-radius: 12px; margin-bottom: 10px; border: 1px solid rgba(16, 185, 129, 0.2); gap: 10px; flex-wrap: wrap; }
            .notice-manage-title { font-size: 14px; font-weight: 700; color: #fff; flex: 1; min-width: 180px; }
            .btn-delete { background: rgba(239, 68, 68, 0.2); border: 1px solid rgba(239, 68, 68, 0.4); color: #fca5a5; padding: 8px 14px; border-radius: 8px; font-size: 12px; font-weight: 800; cursor: pointer; }
            .btn-delete:hover { background: #ef4444; color: #fff; }
            .bottom-taskbar { position: fixed; bottom: 0; left: 0; right: 0; background: rgba(2, 44, 34, 0.95); backdrop-filter: blur(15px); border-top: 1px solid rgba(52, 211, 153, 0.3); padding: 12px 10px; display: flex; justify-content: space-around; align-items: center; z-index: 1000; box-shadow: 0 -5px 25px rgba(0,0,0,0.7); }
            .task-item { background: transparent; border: none; color: #9ca3af; font-size: 11px; font-weight: 700; display: flex; flex-direction: column; align-items: center; gap: 4px; cursor: pointer; text-decoration: none; }
            .task-item span { font-size: 18px; }
            .task-item:hover, .task-item.active { color: #34d399; }
            .modal-overlay { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.85); z-index: 2000; justify-content: center; align-items: center; padding: 20px; }
            .modal-card { background: #022c22; border: 1px solid #34d399; padding: 30px 25px; border-radius: 20px; max-width: 360px; width: 100%; text-align: center; }
            .modal-card h3 { color: #34d399; font-size: 20px; margin-bottom: 12px; }
            .modal-card p { color: #d1d5db; font-size: 14px; line-height: 1.5; margin-bottom: 20px; text-align: left; }
            .modal-card ol { text-align: left; margin-left: 20px; color: #d1d5db; font-size: 13px; margin-bottom: 25px; line-height: 1.6; }
            .close-modal { background: linear-gradient(135deg, #10b981, #059669); color: #fff; border: none; padding: 12px 24px; font-weight: 800; border-radius: 12px; cursor: pointer; width: 100%; }
        </style>
    </head>
    <body>
        <header>
            <a href="/home" class="brand">
                <div class="logo-geo">FUNAAB<span>GEO</span></div>
                <div><h1>FUNAAB Geophysics</h1><span class="sub">Admin Control Panel</span></div>
            </a>
        </header>
        <div class="container">
            {% if success_msg %}<div class="success-alert">{{ success_msg }}</div>{% endif %}

            <div class="admin-box">
                <h3>✍️ Publish Official Broadcast</h3>
                <form method="POST">
                    <input type="hidden" name="action_type" value="announcement">
                    <input type="text" name="title" placeholder="Notice Title (e.g., GPH 201 Practical Venue Update)" required>
                    <textarea name="content" placeholder="Write full department announcement details here..." required></textarea>
                    <label class="checkbox-label"><input type="checkbox" name="urgent" value="yes"> Mark as Urgent / High Priority Red Flag</label>
                    <button type="submit" class="btn-primary">Publish Broadcast Now 🚀</button>
                </form>
            </div>

            <div class="admin-box">
                <h3>📚 Upload Course Material (PDF / Image)</h3>
                <form method="POST" enctype="multipart/form-data">
                    <input type="hidden" name="action_type" value="material">
                    <input type="text" name="course_code" placeholder="Course Code (e.g., GPH 101, MTH 101)" required>
                    <input type="text" name="mat_title" placeholder="Material Title / Description (e.g., Lecture 1 Notes)" required>
                    <input type="file" name="file" accept=".pdf,image/*" required>
                    <span class="file-hint">Supported formats: PDF documents and Image files (.jpg, .png, etc.)</span>
                    <button type="submit" class="btn-primary" style="background: linear-gradient(135deg, #10b981, #059669);">Upload Material 📂</button>
                </form>
            </div>

            <div class="admin-box">
                <h3>🗑️ Manage / Delete Course Materials</h3>
                {% if materials_list %}
                    {% for mat in materials_list %}
                    <div class="notice-manage-item">
                        <div class="notice-manage-title"><span style="color: #34d399;">[{{ mat.course_code }}]</span> {{ mat.title }} <br><span style="font-size: 11px; color: #9ca3af;">Uploaded: {{ mat.date }}</span></div>
                        <form method="POST" onsubmit="return confirm('Are you sure you want to delete this course material?');" style="margin: 0;">
                            <input type="hidden" name="action_type" value="delete_material">
                            <input type="hidden" name="mat_id" value="{{ mat.id }}">
                            <button type="submit" class="btn-delete">🗑️ Delete Material</button>
                        </form>
                    </div>
                    {% endfor %}
                {% else %}
                    <p style="color: #9ca3af; font-size: 13px;">No course materials uploaded yet.</p>
                {% endif %}
            </div>

            <div class="admin-box">
                <h3>🗑️ Manage / Delete Announcements</h3>
                {% if announcements %}
                    {% for notice in announcements %}
                    <div class="notice-manage-item">
                        <div class="notice-manage-title">{{ notice.title }} <br><span style="font-size: 11px; color: #9ca3af;">{{ notice.date }}</span></div>
                        <form method="POST" onsubmit="return confirm('Are you sure you want to delete this announcement?');" style="margin: 0;">
                            <input type="hidden" name="action_type" value="delete_notice">
                            <input type="hidden" name="notice_id" value="{{ notice.id }}">
                            <button type="submit" class="btn-delete">🗑️ Delete Notice</button>
                        </form>
                    </div>
                    {% endfor %}
                {% else %}
                    <p style="color: #9ca3af; font-size: 13px;">No announcements posted yet.</p>
                {% endif %}
            </div>
        </div>
        <div id="installModal" class="modal-overlay">
            <div class="modal-card">
                <h3>📲 Download Portal App</h3>
                <p>Install this website directly onto your phone home screen for instant access like a real app:</p>
                <ol>
                    <li>Tap your browser menu button (<b>3 dots</b> at top right).</li>
                    <li>Select <b>"Add to Home Screen"</b> or <b>"Install App"</b>.</li>
                    <li>Confirm and enjoy lightning-fast offline-ready access!</li>
                </ol>
                <button class="close-modal" onclick="closeModal()">Got It! 👍</button>
            </div>
        </div>
        <div class="bottom-taskbar">
            <a href="/home" class="task-item"><span>🏠</span> Home</a>
            <a href="/dashboard" class="task-item"><span>📢</span> Feed</a>
            <a href="/materials" class="task-item"><span>📚</span> Materials</a>
            <a href="/admin/dashboard" class="task-item active"><span>✍️</span> Admin Portal</a>
            <button class="task-item" onclick="openModal()"><span>📲</span> Download</button>
        </div>
        <script>
            let deferredPrompt;
            window.addEventListener('beforeinstallprompt', (e) => { e.preventDefault(); deferredPrompt = e; });
            function openModal() {
                if (deferredPrompt) {
                    deferredPrompt.prompt();
                    deferredPrompt.userChoice.then(r => { deferredPrompt = null; });
                } else {
                    document.getElementById('installModal').style.display = 'flex';
                }
            }
            function closeModal() { document.getElementById('installModal').style.display = 'none'; }
        </script>
    </body>
    </html>
    ''', success_msg=success_msg, announcements=announcements, materials_list=materials_list)

@app.route('/react/<int:notice_id>/<string:reaction_type>', methods=['POST'])
def react_notice(notice_id, reaction_type):
    if reaction_type not in ['like', 'helpful', 'important']: return jsonify({})
    col_name = 'likes' if reaction_type == 'like' else reaction_type
    modify_db(f'UPDATE announcements SET {col_name} = {col_name} + 1 WHERE id = ?', (notice_id,))
    row = query_db('SELECT likes, helpful, important FROM announcements WHERE id = ?', (notice_id,), one=True)
    return jsonify({"like": row['likes'], "helpful": row['helpful'], "important": row['important']}) if row else jsonify({})

@app.route('/comment/<int:notice_id>', methods=['POST'])
def add_comment(notice_id):
    data = request.get_json()
    author = data.get('author', 'Student')
    text = data.get('text', '')
    date_str = datetime.now().strftime("%b %d")
    modify_db('INSERT INTO comments (announcement_id, author, text, date) VALUES (?, ?, ?, ?)', (notice_id, author, text, date_str))
    return jsonify({"author": author, "text": text, "date": date_str})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
