# 📈 ATUR UANG

![ATUR UANG](https://img.shields.io/badge/Flask-Atur--Uang-blue?style=for-the-badge&logo=flask)  
Aplikasi web sederhana untuk **mencatat pemasukan, pengeluaran, dan mengatur budget bulanan**.  
Dibuat dengan **Python Flask + SQLAlchemy** dan desain responsif Bootstrap 5.

---

## ✨ Fitur Utama
✅ Tambah, edit, dan hapus transaksi (Income / Expense)  
✅ Dashboard interaktif dengan grafik **Chart.js**  
✅ Ringkasan saldo, income, dan expense otomatis  
✅ Budget bulanan per kategori dengan progress bar  
✅ Dark mode / Light mode (auto detect)  
✅ Support kategori dinamis (otomatis bikin kategori baru saat input transaksi)  
✅ Responsive design — nyaman di desktop & mobile  

---

## 📸 Screenshots

### Dashboard
<img width="1313" height="916" alt="image" src="https://github.com/user-attachments/assets/4a922b0d-036e-4d2e-9b64-41e1e625ccd6" />


### Budget
<img width="1246" height="896" alt="image" src="https://github.com/user-attachments/assets/fc1d40e6-7875-47ea-93d2-7dbc8a445f5a" />


### Transactions
<img width="1227" height="375" alt="image" src="https://github.com/user-attachments/assets/d90fb533-b2c9-4b16-974c-9a262e989b91" />



---

## 🚀 Cara Menjalankan di Lokal

1. Clone repo:
   ```bash
   git clone https://github.com/Arroychaan/Atur-Uang-App.git
   cd Atur-Uang-App
   
2. Buat virtual environment & install requirements:
   ```bash
    python -m venv .venv
    source .venv/bin/activate   # Mac / Linux
    .venv\Scripts\activate      # Windows
    pip install -r requirements.txt
   
3. Buat file .env
   ```bash
   SECRET_KEY=changeme123
   DATABASE_URL=sqlite:///finance.db
   FLASK_ENV=development


4. Jalankan Aplikasi
     ```bash
     python app.py

    Atau
   
    flask run

5. Buka Browser di  :
   ```bash
   http://127.0.0.1:5000


---
🛠️ Tech Stack

Flask
 — Web framework

Flask SQLAlchemy
 — ORM

Bootstrap 5
 — Styling

Chart.js
 — Grafik interaktif

Gunicorn
 — Production server

Render
 — Deployment

📦 Deployment (Render)

Push project ke GitHub

Deploy di Render
 dengan Gunicorn:

gunicorn app:app


Tambahkan Environment Variables di Render:

SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///finance.db   # atau PostgreSQL
FLASK_ENV=production

❤️ Dukungan

Kalau aplikasi ini bermanfaat buat lu, boleh banget dukung gua di Saweria 🙏

👉 Saweria.co/achmadroychan

atau mampir ke Instagram gua:
📸 @ar.roychan

👨‍💻 Author

Achmad Roychan
💼 Developer | 📊 Finance Enthusiast | 🚀 Learner

