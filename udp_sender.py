import cv2
import socket
import time
import os

# Konfigurasi Target
TARGET_IP = '127.0.0.1'
TARGET_PORT = 9002

# Ganti 'video_tugas.mp4' dengan nama file video yang Anda miliki
FILE_VIDEO = 'video_tugas.mp4'  

# Memastikan file video benar-benar ada di folder
if not os.path.exists(FILE_VIDEO):
    print(f"[!] Error: File video '{FILE_VIDEO}' tidak ditemukan di folder ini.")
    exit()

# 1. Inisialisasi Socket UDP (AF_INET = IPv4, SOCK_DGRAM = UDP)
udp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 2. Membaca file video lokal
cap = cv2.VideoCapture(FILE_VIDEO)

print(f"[*] Pengirim Video UDP Aktif. Mengalirkan file '{FILE_VIDEO}' secara diam-diam ke {TARGET_IP}:{TARGET_PORT}...")
print("[*] Tekan 'Ctrl + C' di terminal ini untuk menghentikan pengiriman.")

try:
    while True:
        # Membaca frame demi frame dari video lokal
        ret, frame = cap.read()
        
        # Jika video sudah mencapai akhir (habis), ulang kembali dari awal (Looping)
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        # Kompresi resolusi agar ukuran file selalu < 64KB (Batas maksimal paket UDP)
        frame_kecil = cv2.resize(frame, (480, 360))

        # Kompresi kualitas JPEG menjadi 50%
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
        result, label_biner = cv2.imencode('.jpg', frame_kecil, encode_param)
        
        if result:
            data_paket = label_biner.tobytes()
            ukuran_paket = len(data_paket)
            
            # Keamanan UDP: Abaikan frame jika ukurannya melebihi kapasitas maksimal
            if ukuran_paket > 65507:
                continue
            
            # 3. Kirim paket data biner menggunakan protokol UDP murni
            udp_client_socket.sendto(data_paket, (TARGET_IP, TARGET_PORT))
        
        # Mengatur delay agar kecepatan streaming wajar (sekitar 30 FPS)
        time.sleep(0.03)

        # CATATAN: Fungsi cv2.imshow() dan cv2.waitKey() sudah dihapus di sini
        # sehingga tidak akan ada lagi pop-up window yang mengganggu.

except KeyboardInterrupt:
    print("\n[-] Streaming UDP dihentikan secara manual.")

finally:
    # Bersihkan memori dan tutup socket
    cap.release()
    udp_client_socket.close()
    print("[*] Socket UDP telah ditutup.")