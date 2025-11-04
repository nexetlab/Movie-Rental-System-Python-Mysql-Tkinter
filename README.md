```
# 🎬 Movie Rental Management System

A Python-based Movie Rental Management System that allows a rental store to manage movies, customers, rentals, returns, and generate reports.
The project uses **MySQL** as the database and **Tkinter** for the GUI.

---

## 📁 Project Structure
```

movie_rental_system/
├─ db/
│ ├─ init_database.py
│ ├─ setup_database.py
├─ utils/
│ ├─ security.py
│ └─ **init**.py
├─ main.py
├─ config.py
├─ requirements.txt
├─ README.md

````

---

## 🛠 Prerequisites

- Python 3.12+
- MySQL 8+
- GUI: Tkinter (included with most Python distributions)
- Python packages:

```text
mysql-connector-python
bcrypt
python-dotenv
openpyxl
matplotlib
````

---

## ⚡ Setup Instructions

### 1️⃣ Install Python Dependencies

**Activate your virtual environment first**:

```bash
# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install required packages:

```bash
pip install -r requirements.txt
```

If you don’t have `requirements.txt`:

```bash
pip install mysql-connector-python bcrypt python-dotenv openpyxl matplotlib
```

---

### 2️⃣ GUI Setup (Tkinter)

#### macOS:

1. Install Tcl/Tk via Homebrew:

```bash
brew install tcl-tk
```

2. Add these to your `~/.zshrc` or `~/.bash_profile`:

```bash
export PATH="/opt/homebrew/opt/tcl-tk/bin:$PATH"
export LDFLAGS="-L/opt/homebrew/opt/tcl-tk/lib"
export CPPFLAGS="-I/opt/homebrew/opt/tcl-tk/include"
export PKG_CONFIG_PATH="/opt/homebrew/opt/tcl-tk/lib/pkgconfig"
```

Reload shell:

```bash
source ~/.zshrc
```

3. If Tkinter still fails, reinstall Python via Homebrew:

```bash
brew reinstall python@3.12 --with-tcl-tk
```

---

#### Windows:

- Tkinter comes **pre-installed** with standard Python distributions.
- If you get `_tkinter` errors, install Python from [python.org](https://www.python.org/downloads/) and check the **“tcl/tk and IDLE”** option during installation.

---

### 3️⃣ Configure Database

1. Start MySQL server.
2. Create the database manually if needed:

```sql
CREATE DATABASE movie_rental_db;
```

3. Update `config.py` with your MySQL credentials:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',       # empty string if no password
    'database': 'movie_rental_db',
    'port': 3306
}
```

---

### 4️⃣ Initialize Database

Run the setup script to create tables and default admin:

```bash
python db/setup_database.py
```

You should see logs confirming that tables were created successfully.

---

### 5️⃣ Run the Application

```bash
python main.py
```

- A login window should appear.
- Use the **default admin credentials** created by `init_database.py`.
- Access **Movie Management**, **Customer Management**, and **Rental Management** from the dashboard.

---

## ⚡ Notes

- Run all commands from the **project root**.
- Some database constraints (like release year limits) are enforced in Python instead of MySQL for MySQL 8+ compatibility.
- Reports and charts can be generated from the GUI.

---

## ✅ Troubleshooting

| Issue                      | Solution                                                                                 |
| -------------------------- | ---------------------------------------------------------------------------------------- |
| `_tkinter` not found       | macOS: install Tcl/Tk via Homebrew. Windows: ensure Python installation includes Tcl/Tk. |
| Database connection errors | Check `config.py` and ensure MySQL server is running.                                    |
| Missing Python modules     | Install using `pip install <module>` inside the virtual environment.                     |

---

## 👨‍💻 Author

- Developed by **Your Team Name**
- Roles and contributions should be listed in the project report.

---

## 🎯 Features

- Secure employee login
- Movie, Customer, and Rental management
- CRUD operations
- Search and filter functionality
- Reports generation in Excel
- Data visualization with charts
