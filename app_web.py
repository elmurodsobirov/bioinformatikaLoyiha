# -*- coding: utf-8 -*-
"""
Bioinformatika Loyihasi 13: Xavfsiz Veb-Interfeysli Diagnostik Dastur Serveri
Mavzu: Biologik ma’lumotlar asosida kasalliklarni mashinali o‘qitish yordamida bashoratlash
Mualliflar: Ramanov Rustam va Sobirov Elmurod
Xavfsizlik: Zero-Trust, Localhost Binding (127.0.0.1), Anti-Path Traversal, Hardened HTTP Headers
"""

import os
import sys
import posixpath
import urllib.parse
import webbrowser
import http.server
import socketserver
import threading

PORT = 8501
HOST = "127.0.0.1"  # Xavfsizlik: Faqat lokal kompyuter uchun (tashqi tarmoqdan yopiq)
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class SecureBioinfoHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        # Yuqori xavfsizlik HTTP sarlavhalari (Defense-in-depth)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.send_header("X-XSS-Protection", "1; mode=block")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://fonts.gstatic.com; img-src 'self' data: blob:;"
        )
        super().end_headers()

    def translate_path(self, path):
        # Xavfsizlik: Path Traversal hujumlariga qarshi tekshiruv
        path = path.split('?', 1)[0].split('#', 1)[0]
        path = posixpath.normpath(urllib.parse.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        
        # Loyiha ildiz papkasidan tashqariga chiqishga ruxsat yo'q
        for word in words:
            if word in (os.curdir, os.pardir) or '\\' in word or ':' in word:
                return os.path.join(DIRECTORY, "dastur_web.html")
                
        return super().translate_path(path)

    def do_GET(self):
        if self.path in ("/", ""):
            self.path = "/dastur_web.html"
        return super().do_GET()

    def log_message(self, format, *args):
        # Audit log
        sys.stderr.write(f"[AUDIT LOG] {self.address_string()} - {format % args}\n")

def start_server():
    os.chdir(DIRECTORY)
    
    # TCP port qayta ishlatish
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer((HOST, PORT), SecureBioinfoHTTPHandler) as httpd:
        print("=" * 80)
        print("   BIOINFORMATIKA: BIOLOGIK MA'LUMOTLAR ASOSIDA KASALLIKLARNI")
        print("   MASHINALI O'QITISH YORDAMIDA BASHORATLASH (13-LOYIHA DASTURI)")
        print("   Mualliflar: Ramanov Rustam va Sobirov Elmurod")
        print(f"   Xavfsiz Veb-Server ishga tushdi: http://{HOST}:{PORT}")
        print("   Xavfsizlik darajasi: Yuqori (Faqat 127.0.0.1 Localhost, Zero-Trust himoya)")
        print("   Dasturni to'xtatish uchun: Ctrl + C bosing")
        print("=" * 80)

        # Brauzerda avtomatik ochish
        threading.Timer(1.0, lambda: webbrowser.open(f"http://{HOST}:{PORT}/dastur_web.html")).start()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[*] Server xavfsiz to'xtatildi.")
            httpd.shutdown()

if __name__ == "__main__":
    start_server()
