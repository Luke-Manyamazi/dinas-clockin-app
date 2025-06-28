# 🕒 Dinas Clock-In App

A simple Flask-based application to manage **child drop-offs and pickups** at a daycare center using QR card scans. It includes child registration, card assignment, attendance tracking, and reporting features — all stored locally in SQLite.

---

## ✨ Features

- 🧒 Register children and link to their guardians
- 🎴 Generate unique QR-based card codes
- 🔄 Assign/unassign cards to children
- 📲 Scan cards for **drop-off** and **pick-up**
- 📅 Monthly attendance reports
- 📷 QR Code generation for each card
- 💾 Local database with SQLite
- 💡 Flash message feedback after every action

---

## 🧰 Tech Stack

- **Backend:** Python, Flask
- **Database:** SQLite
- **QR Codes:** `qrcode` Python module
- **Frontend:** Jinja2 templates (`index.html`, `scan.html`, `reports.html`, etc.)

---

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Luke-Manyamazi/dinas-clockin-app.git
cd dinas-clockin-app
````

### 2. Create a Virtual Environment and Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt
```

If `requirements.txt` is missing, you can install manually:

```bash
pip install flask qrcode
```

### 3. Run the App

```bash
python app.py
```

Then open in your browser: [http://localhost:5002](http://localhost:5002)

---

## 🗃️ Database

The app uses **SQLite** (`daycare.db`) with the following tables:

* `children`
* `cards`
* `attendance`

Tables are automatically created on startup using `init_db()`.

---

## 📋 Usage

* Add a child via the home page
* Generate a card (`/generate_card`)
* Assign a card to a child
* Go to `/scan` to simulate drop-off or pickup
* View `/reports` for monthly attendance logs
* View `/card_qr/<card_code>` to get the card’s QR image

---

## 📁 Folder Structure (simplified)

```
dinas-clockin-app/
├── app.py
├── daycare.db  # auto-created
├── templates/
│   ├── index.html
│   ├── scan.html
│   ├── reports.html
│   └── card_qr.html
├── static/      # optional if using images/css
└── requirements.txt
```

---

## ✅ Future Improvements

* ✅ Export attendance reports to PDF or Excel
* ✅ Email/SMS alerts to parents
* ✅ Role-based login (Admin vs Staff)
* ✅ Daily summary dashboard

---

## 🤝 Contributing

Pull requests are welcome! Please open an issue first to discuss any major changes.

---

## 📧 Contact

For feedback, email: [info.daycare@dinasgroup.co.za](mailto:info.daycare@dinasgroup.co.za)

