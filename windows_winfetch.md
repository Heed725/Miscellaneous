# Windows Screenfetch Alternatives

A guide to installing and using screenfetch-like system information tools on Windows.

## Overview

Screenfetch is a popular Linux command-line tool that displays system information alongside an ASCII logo. This guide covers the best Windows alternatives.

## Available Tools

### 1. Winfetch
A PowerShell-based port of neofetch/screenfetch for Windows.

### 2. Fastfetch
A faster, feature-rich alternative written in C with extensive customization options.

### 3. Neofetch
The original neofetch, also available on Windows.

---

## Installation Methods

### Option 1: Using Scoop (Recommended)

Scoop is a command-line package manager for Windows that makes installing and managing CLI tools easy.

#### Install Scoop

Open PowerShell (as regular user, not admin) and run:

```powershell
# Set execution policy for current user
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install Scoop
Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression
```

#### Install Winfetch

```powershell
scoop install winfetch
```

#### Install Fastfetch

```powershell
scoop install fastfetch
```

#### Install Neofetch

```powershell
scoop install neofetch
```

---

### Option 2: Manual Installation (Winfetch)

If you prefer not to use a package manager, you can download winfetch directly.

```powershell
# Download winfetch script
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/lptstr/winfetch/master/winfetch.ps1" -OutFile "$env:USERPROFILE\winfetch.ps1"

# Run winfetch
& "$env:USERPROFILE\winfetch.ps1"
```

To make it easier to run in the future, you can add it to your PowerShell profile:

```powershell
# Open your profile for editing
notepad $PROFILE

# Add this line to the file:
Set-Alias winfetch "$env:USERPROFILE\winfetch.ps1"
```

---

### Option 3: Standalone Executable (Fastfetch)

Download the latest release as a standalone executable.

#### Automatic Download via PowerShell

```powershell
# Download and extract fastfetch
Invoke-WebRequest -Uri "https://github.com/fastfetch-cli/fastfetch/releases/latest/download/fastfetch-windows-amd64.zip" -OutFile "$env:TEMP\fastfetch.zip"

# Extract to user directory
Expand-Archive -Path "$env:TEMP\fastfetch.zip" -DestinationPath "$env:USERPROFILE\fastfetch" -Force

# Run fastfetch
& "$env:USERPROFILE\fastfetch\fastfetch.exe"
```

#### Manual Download

1. Visit: https://github.com/fastfetch-cli/fastfetch/releases
2. Download `fastfetch-windows-amd64.zip`
3. Extract the ZIP file
4. Run `fastfetch.exe`

---

### Option 4: Using Chocolatey

If you already have Chocolatey installed:

```powershell
# Install Neofetch
choco install neofetch

# Install Fastfetch
choco install fastfetch
```

---

## Usage

After installation, simply run the tool in PowerShell:

```powershell
# Run winfetch
winfetch

# Run fastfetch
fastfetch

# Run neofetch
neofetch
```

---

## Built-in PowerShell Alternative

If you don't want to install anything, use this PowerShell command for basic system info:

```powershell
systeminfo | findstr /B /C:"OS Name" /C:"OS Version" /C:"System Type" /C:"Total Physical Memory"
```

Or for more detailed info:

```powershell
Get-ComputerInfo | Select-Object CsName, WindowsVersion, OsArchitecture, CsTotalPhysicalMemory
```

---

## Customization

### Winfetch Configuration

Create a config file at `$env:USERPROFILE\.config\winfetch\config.ps1`:

```powershell
# Example configuration
$image = "windows"
$noimage = $false
```

### Fastfetch Configuration

Create a config file at `$env:USERPROFILE\.config\fastfetch\config.jsonc`:

```json
{
  "logo": {
    "type": "auto"
  },
  "display": {
    "separator": ": "
  }
}
```

---

## Troubleshooting

### PowerShell Execution Policy Error

If you get an execution policy error, run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Scoop Not Found After Installation

Close and reopen PowerShell, or restart your terminal.

### Command Not Recognized

Make sure the tool's directory is in your PATH, or use the full path to the executable.

---

## Comparison

| Feature | Winfetch | Fastfetch | Neofetch |
|---------|----------|-----------|----------|
| Language | PowerShell | C | Bash |
| Speed | Fast | Very Fast | Slower |
| Customization | Good | Excellent | Excellent |
| Windows Native | Yes | Yes | Partial |
| Maintenance | Active | Active | Less Active |

---

## Recommendations

- **Best for Windows**: Winfetch (native PowerShell, well-maintained)
- **Fastest**: Fastfetch (written in C, very fast)
- **Most Features**: Fastfetch (extensive customization options)
- **Cross-platform**: Neofetch (if you use Linux too)

---

## Additional Resources

- [Winfetch GitHub](https://github.com/lptstr/winfetch)
- [Fastfetch GitHub](https://github.com/fastfetch-cli/fastfetch)
- [Neofetch GitHub](https://github.com/dylanaraps/neofetch)
- [Scoop Website](https://scoop.sh)

---

## License

This guide is provided as-is. Each tool has its own license. Please refer to their respective repositories for licensing information.
