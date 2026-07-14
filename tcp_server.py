import socket
import os

# Konfigurasi Server TCP
HOST = '127.0.0.1'  # Localhost
PORT = 9001         # Port TCP khusus untuk menerima file
SAVE_DIR = 'uploads'# Folder tujuan penyimpanan

# Pastikan folder uploads tersedia
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

def start_tcp_server():
    # 1. Inisialisasi socket TCP (IPv4, Stream/TCP)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Mencegah error "Address already in use" saat server di-restart
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # 2. Bind ke alamat dan port
    server_socket.bind((HOST, PORT))
    
    # 3. Mode listen (maksimal 5 antrean koneksi)
    server_socket.listen(5)
    print(f"[*] Server TCP Listener aktif dan menunggu file di {HOST}:{PORT}...")

    try:
        while True:
            # 4. Terima koneksi masuk dari app.py
            client_socket, addr = server_socket.accept()
            print(f"[+] Menerima transmisi TCP dari: {addr}")
            
            # 5. Loop untuk menerima seluruh potongan data (chunk)
            data_masuk = b""
            while True:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                data_masuk += chunk
                
            # 6. Ekstrak data (Format dari app.py: NamaFile|||IsiBinerFile)
            if b'|||' in data_masuk:
                nama_file_bytes, isi_file = data_masuk.split(b'|||', 1)
                nama_file = nama_file_bytes.decode('utf-8')
                
                filepath = os.path.join(SAVE_DIR, nama_file)
                
                # 7. Tulis data biner menjadi file utuh
                with open(filepath, 'wb') as f:
                    f.write(isi_file)
                    
                print(f"[✔] File '{nama_file}' berhasil diterima dan disimpan di folder /{SAVE_DIR}")
            else:
                print("[!] Data diterima, tetapi format delimiter '|||' tidak ditemukan.")
            
            # Tutup socket klien setelah selesai
            client_socket.close()

    except KeyboardInterrupt:
        print("\n[-] Server TCP dihentikan secara manual.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_tcp_server()