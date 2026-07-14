from flask import Flask, render_template, request, redirect, url_for, flash, Response, session, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
import socket
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'kunci_rahasia_jaringan_komputer'

# =========================================================================
# KONFIGURASI CORS & COOKIE CROSS-ORIGIN
# =========================================================================
# Izinkan frontend lokal (127.0.0.1:8080) mengakses backend ini dengan cookie
CORS(app, supports_credentials=True, origins=["http://127.0.0.1:8080"])

app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True  # wajib True karena backend diakses via HTTPS

# =========================================================================
# KONFIGURASI EMAIL
# =========================================================================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "willymin783@gmail.com"
EMAIL_PASSWORD = "akfj pywy ryab snih"  # Ganti dengan App Password Gmail Anda

def kirim_email_verifikasi(email_tujuan):
    isi_email = "Halo,\n\nTerima kasih telah mendaftar di Aplikasi Jaringan Web kami. Akun Anda berhasil dibuat dan sudah dapat digunakan untuk login."
    msg = MIMEText(isi_email)
    msg['Subject'] = 'Registrasi Berhasil - Konfirmasi Akun'
    msg['From'] = EMAIL_SENDER
    msg['To'] = email_tujuan

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, email_tujuan, msg.as_string())
        server.quit()
        print(f"[*] Email konfirmasi sukses dikirim ke {email_tujuan}")
    except Exception as e:
        print(f"[!] Gagal mengirim email: {e}")

# =========================================================================
# FUNGSI BANTUAN DATABASE
# =========================================================================
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# =========================================================================
# ROUTING LOGIN, REGISTRASI & LOGOUT (JSON API untuk frontend lokal)
# =========================================================================

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    if not email or not password:
        return jsonify(success=False, message="Email dan password wajib diisi."), 400

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()

    if user and check_password_hash(user['password'], password):
        session['user_email'] = email
        return jsonify(success=True, message="Login berhasil.", email=email)
    else:
        return jsonify(success=False, message="Email tidak ditemukan atau password salah."), 401


@app.route('/register', methods=['POST'])
def register():
    email = request.form.get('email')
    password = request.form.get('password')

    if not email or not password:
        return jsonify(success=False, message="Email dan password wajib diisi."), 400

    hashed_password = generate_password_hash(password)

    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, hashed_password))
        conn.commit()
        kirim_email_verifikasi(email)
        return jsonify(success=True, message="Registrasi sukses!")
    except sqlite3.IntegrityError:
        return jsonify(success=False, message="Email tersebut sudah terdaftar! Gunakan email lain atau silakan login."), 409
    finally:
        conn.close()


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_email', None)
    return jsonify(success=True, message="Anda telah berhasil keluar (Logout).")


# =========================================================================
# INTERFACES JALUR TCP UPLOAD (AJAX)
# =========================================================================
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'user_email' not in session:
        return jsonify(success=False, message="Akses ditolak, silakan login."), 403

    if 'file' not in request.files:
        return jsonify(success=False, message="Tidak ada file."), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify(success=False, message="Nama file tidak valid."), 400

    file_data = file.read()
    try:
        tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_sock.connect(('127.0.0.1', 9001))
        paket = file.filename.encode('utf-8') + b'|||' + file_data
        tcp_sock.sendall(paket)
        tcp_sock.close()
        return f"File '{file.filename}' sudah terkirim", 200
    except Exception as e:
        return f"Koneksi TCP Error: {e}", 500

# =========================================================================
# INTERFACES JALUR STREAMING UDP VIDEO FEED
# =========================================================================
def dapatkan_frame_udp():
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp_sock.bind(('127.0.0.1', 9002))
    while True:
        data, addr = udp_sock.recvfrom(65535)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + data + b'\r\n')

@app.route('/video_feed')
def video_feed():
    if 'user_email' not in session:
        return "Akses Ditolak", 403
    return Response(dapatkan_frame_udp(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True, port=5000)