To run **PC Globe 5** in DOSBox from the folder `C:\pcglobe-5`, follow these steps:

---

## ✅ **Method 1 — Run it directly with commands inside DOSBox**

### 1. Open **DOSBox**

You'll get a command prompt like:

```
Z:\
```

### 2. Mount the folder

Type:

```
mount c c:\pcglobe-5
```

Press **Enter**.

### 3. Switch to the mounted drive:

```
c:
```

Press **Enter**.

### 4. Launch the program

Common executable names for PC Globe 5 include:

* `PCGLOBE.EXE`
* `GLOBE.EXE`
* `START.EXE`
* `INSTALL.EXE` (for first-time setup)

Try:

```
pcglobe.exe
```

If it fails:

```
dir
```

This shows all files. Look for any `.EXE` files and run them, for example:

```
start.exe
globe.exe
```

---

## ✅ **Method 2 — Create a DOSBox config entry (auto-run)**

If you want to make DOSBox automatically start PC Globe every time:

1. Open DOSBox config
   Run:

```
DOSBox Options
```

2. Scroll down to the bottom, find the `[autoexec]` section.

3. Add:

```
mount c c:\pcglobe-5
c:
pcglobe.exe
```

Save and close.

---

## ⚠️ If the program does not start

Tell me what you see when you run:

```
dir
```

inside DOSBox.
Paste the list of files here and I will tell you the exact .exe to run.
