<p align="center">
  <span style="font-family:Montserrat,sans-serif;font-size:2.5rem;font-weight:700;">
    <span style="color:#14b8a6;">Life</span><span style="color:#2563eb;">Tag</span>
  </span>
  <br>
  <em style="color:#0d9488;font-size:1.15rem;">Your Emergency Medical ID &amp; QR Code System</em>
</p>

---

## 🚨 The Intuition Behind LifeTag

Imagine a world where your crucial medical information is always at hand—secure, accurate, and ready in emergencies. LifeTag is built to make that vision a reality. By generating a unique QR code for every user, LifeTag connects people with their emergency medical profile, allowing quick and safe access for themselves and trusted medical representatives.

The goal: **Save lives by making information accessible, yet secure—only showing the right details to the right people at the right time.**

---

## 🏃 Process Flow: How LifeTag Works

1. **User Journey**
   - Sign up, create your personal medical profile.
   - Generate your LifeTag—a dynamic QR code tied to your information.
   - Place your LifeTag on keychains, cards, or wearables.

2. **Scanning & Access**
   - **Public Scanner:** Anyone (bystander, friend, paramedic) can scan to get essential, non-sensitive emergency info (like allergies, blood group, emergency contacts).
   - **Medical Representative Scanner:** Verified professionals log in to access and safely edit detailed medical data, ensuring your profile is always up to date and accurate.

3. **Role-Based Security**
   - **Users:** Can view and update their own profiles, control privacy, and manage which data is public.
   - **Medical Representatives:** After verification, can edit user medical details safely—ensuring only authorized personnel can make changes.

4. **Seamless, Secure, and Human-Centric**
   - Everything from registration to emergency scanning is designed for clarity, safety, and speed—because every second counts.

---

## 🛠️ Features Implemented

- **Secure Authentication** for both users and medical representatives.
- **Medical Profile Management**: Add, update, or restrict visibility of health info.
- **QR Code Generation**: Instantly create your LifeTag for physical use.
- **Role-Based Interfaces**:
  - **User Interface** – Personal dashboard for profile management and QR code.
  - **Medical Rep Interface** – Verified portal for safely updating/validating medical data.
- **Public & Verified Scanners**:
  - [General Public Scanner](https://lifetag-publicscanner.onrender.com/)
  - [Medical Rep Scanner](https://lifetag-verifiedscanner.onrender.com/)
- **Responsive UI** with dual-colored logo text heading, styled using Tailwind CSS for a modern and accessible look.
- **PostgreSQL Database** hosted on **NeonDB** for robust, scalable data storage.
- **Deployment** on Render for reliable cloud hosting.

---

## 🏗️ Tech Stack

| Layer            | Technology            |
|------------------|----------------------|
| Backend          | Python (Flask)       |
| Frontend         | HTML, Tailwind CSS   |
| QR/Images        | Pillow               |
| Web Server       | Gunicorn             |
| Deployment       | Render               |
| Database         | PostgreSQL (NeonDB)  |

---

## 📦 Required Modules & Installation

```bash
# Clone the repository
git clone https://github.com/NIKHIL-BANALA/LifeTag-app.git
cd LifeTag-app

# (Recommended) Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

**Key Modules:**
- Flask
- Pillow
- Gunicorn
- psycopg2-binary  # PostgreSQL driver
- python-dotenv

---

## 🗄️ Database

- **PostgreSQL**: All user and medical data are stored securely in a PostgreSQL database, deployed on [NeonDB](https://neon.tech/). This ensures data integrity, scalability, and safety.
- Connection is handled securely via environment variables.

---

## 🌐 Live Deployments

| Interface                          | Link                                                      |
|-------------------------------------|-----------------------------------------------------------|
| Main App                           | [lifetag-app.onrender.com](https://lifetag-app.onrender.com/)               |
| General Public Scanner              | [lifetag-publicscanner.onrender.com](https://lifetag-publicscanner.onrender.com/) |
| Verified Medical Rep Scanner        | [lifetag-verifiedscanner.onrender.com](https://lifetag-verifiedscanner.onrender.com/) |

---

## 🤝 Human-Centered, Role-Based Design

- **For Users:**  
  You control your medical data, decide what’s public, and can update your profile anytime. Your QR code can be placed anywhere you wish—wallet, helmet, phone case, etc.—so help is always a scan away.

- **For Medical Reps:**  
  Verified medical staff have a secure portal to access and responsibly update user medical records. This helps keep data current and accurate in emergencies, with full audit control.

All interfaces are designed for clarity, speed, and peace of mind—because your health and privacy matter.

---

## 📖 Usage

1. Register and set up your profile on the [main app](https://lifetag-app.onrender.com/).
2. Generate your LifeTag and print the QR code.
3. In emergencies, scan with the public or verified portal as needed.
4. Medical representatives can log in for safe, verified updating of medical information.

---

## 👨‍💻 Author

Made with ❤️ by [NIKHIL BANALA](https://github.com/NIKHIL-BANALA)

---

> For issues, feedback, or feature requests, please use the GitHub repository’s Issues section.
