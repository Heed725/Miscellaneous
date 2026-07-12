# Install or Repair WinGet on Windows

You are trying to use WinGet before installing it. Also, **`wingetcreate` is not WinGet**; it is a separate developer tool for creating package manifests.

Since PowerShell is already open as Administrator, run these official Microsoft repair/install commands:

```powershell
Install-PackageProvider -Name NuGet -Force | Out-Null

Install-Module -Name Microsoft.WinGet.Client -Force -Repository PSGallery | Out-Null

Import-Module Microsoft.WinGet.Client

Repair-WinGetPackageManager -Force -Latest
```

Microsoft recommends this process when WinGet is missing or incorrectly installed. WinGet is supplied through the Windows **App Installer** package.

After it finishes, completely close PowerShell and open a new Command Prompt. Test:

```cmd
winget --version
```

You can also check its location:

```cmd
where winget
```

## If PowerShell blocks the commands

Run this first:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
```

Then repeat the installation commands.

## Alternative through Microsoft Store

1. Open **Microsoft Store**.
2. Search for **App Installer**.
3. Make sure the publisher is **Microsoft Corporation**.
4. Install or update it.
5. Close and reopen Command Prompt.
6. Test:

```cmd
winget --version
```

WinGet is included with App Installer. WinGet requires Windows 10 version 1809/build 17763 or newer.

## Install the required media tools

Once `winget --version` works, install the tools you originally needed:

```cmd
winget install -e --id yt-dlp.yt-dlp
winget install -e --id Gyan.FFmpeg
winget install -e --id DenoLand.Deno
```

Do not run:

```cmd
winget install wingetcreate
```

unless you specifically need the WinGet manifest-development utility.
