````markdown
# Step-by-step Guide (PowerShell or Command Prompt)

### 1. Go to your Desktop
```powershell
cd C:\Users\user\Desktop
````

---

### 2. Clone the repo

```powershell
git clone https://github.com/AllanCerveaux/svg_repo_dl.git
```

---

### 3. Enter the project folder

```powershell
cd svg_repo_dl
```

---

### 4. Check Python is available (use whichever works on your machine)

```powershell
python --version
```

If that errors, try:

```powershell
py --version
```

---

### 5. Install dependencies

**Preferred (uses the project’s requirements file):**

```powershell
python -m pip install -r requirements.txt
```

If you still get a `No module named …` error, install explicitly:

```powershell
python -m pip install beautifulsoup4 progress colored
```

---

### 6. Run the downloader to save to your Desktop

```powershell
python -m svgrepodl https://www.svgrepo.com/collection/role-playing-game/ --path C:\Users\user\Desktop
```

---

### ✅ Result

This creates a folder named after the collection (e.g., `role-playing-game`) on your **Desktop** with all the SVGs inside.


