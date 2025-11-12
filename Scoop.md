# Essential Apps to Install with Scoop

A curated list of useful applications you can install using Scoop on Windows.

## What is Scoop?

Scoop is a command-line installer for Windows that makes it easy to install and manage applications without dealing with installers, UAC prompts, or GUI wizards.

---

## Development Tools

### Programming Languages & Runtimes

```powershell
# Python
scoop install python

# Node.js
scoop install nodejs

# Go
scoop install go

# Rust
scoop install rustup

# Java (OpenJDK)
scoop install openjdk

# PHP
scoop install php

# Ruby
scoop install ruby
```

### Version Control

```powershell
# Git
scoop install git

# GitHub CLI
scoop install gh

# GitKraken (visual Git client)
scoop install gitkraken
```

### Code Editors & IDEs

```powershell
# Visual Studio Code
scoop install vscode

# Sublime Text
scoop install sublime-text

# Notepad++
scoop install notepadplusplus

# Vim
scoop install vim

# Neovim
scoop install neovim
```

### Build Tools & Package Managers

```powershell
# CMake
scoop install cmake

# Make
scoop install make

# Yarn (JavaScript)
scoop install yarn

# Composer (PHP)
scoop install composer

# Maven (Java)
scoop install maven

# Gradle (Java)
scoop install gradle
```

---

## Command Line Tools

### Modern CLI Replacements

```powershell
# bat (better cat)
scoop install bat

# exa (better ls)
scoop install exa

# ripgrep (better grep)
scoop install ripgrep

# fd (better find)
scoop install fd

# fzf (fuzzy finder)
scoop install fzf

# zoxide (smarter cd)
scoop install zoxide

# tldr (simplified man pages)
scoop install tldr
```

### System Information & Monitoring

```powershell
# Winfetch (system info)
scoop install winfetch

# Fastfetch (system info)
scoop install fastfetch

# btop (system monitor)
scoop install btop

# htop (process viewer)
scoop install htop
```

### File Management

```powershell
# 7zip (compression)
scoop install 7zip

# Everything (file search)
scoop install everything

# FFmpeg (media conversion)
scoop install ffmpeg

# ImageMagick (image manipulation)
scoop install imagemagick
```

---

## Networking & Internet

### Network Tools

```powershell
# curl
scoop install curl

# wget
scoop install wget

# httpie (user-friendly HTTP client)
scoop install httpie

# nmap (network scanner)
scoop install nmap

# Wireshark (packet analyzer)
scoop install wireshark
```

### Download Managers

```powershell
# aria2 (download accelerator)
scoop install aria2

# youtube-dl (video downloader)
scoop install youtube-dl

# yt-dlp (youtube-dl fork)
scoop install yt-dlp
```

### Browsers

```powershell
# Firefox
scoop install firefox

# Google Chrome
scoop install googlechrome

# Brave
scoop install brave

# Chromium
scoop install chromium
```

---

## Productivity Tools

### Terminal Emulators

```powershell
# Windows Terminal
scoop install windows-terminal

# Alacritty (GPU-accelerated)
scoop install alacritty

# WezTerm
scoop install wezterm
```

### Text Processing

```powershell
# jq (JSON processor)
scoop install jq

# yq (YAML processor)
scoop install yq

# pandoc (document converter)
scoop install pandoc
```

### Password Managers

```powershell
# KeePassXC
scoop install keepassxc

# Bitwarden CLI
scoop install bitwarden-cli
```

---

## Database Tools

```powershell
# PostgreSQL
scoop install postgresql

# MySQL
scoop install mysql

# MongoDB
scoop install mongodb

# Redis
scoop install redis

# SQLite
scoop install sqlite

# DBeaver (database GUI)
scoop install dbeaver
```

---

## DevOps & Cloud

### Containerization

```powershell
# Docker
scoop install docker

# Kubernetes CLI (kubectl)
scoop install kubectl

# Helm
scoop install helm

# k9s (Kubernetes TUI)
scoop install k9s
```

### Cloud CLI Tools

```powershell
# AWS CLI
scoop install aws

# Azure CLI
scoop install azure-cli

# Google Cloud SDK
scoop install gcloud

# Terraform
scoop install terraform

# Ansible
scoop install ansible
```

---

## Media & Graphics

### Media Players

```powershell
# VLC
scoop install vlc

# MPV
scoop install mpv
```

### Image Tools

```powershell
# GIMP (image editor)
scoop install gimp

# Inkscape (vector graphics)
scoop install inkscape

# ImageMagick (CLI image tool)
scoop install imagemagick
```

---

## Communication

```powershell
# Discord
scoop install discord

# Slack
scoop install slack

# Zoom
scoop install zoom

# Microsoft Teams
scoop install microsoft-teams
```

---

## Utilities

### System Utilities

```powershell
# PowerToys (Windows utilities)
scoop install powertoys

# AutoHotkey (automation)
scoop install autohotkey

# Sysinternals Suite
scoop install sysinternals
```

### Security

```powershell
# OpenSSL
scoop install openssl

# GnuPG (encryption)
scoop install gpg

# WireGuard (VPN)
scoop install wireguard
```

---

## Adding Extra Buckets

Scoop organizes apps into "buckets" (repositories). Add these for more apps:

```powershell
# Extras bucket (GUI apps)
scoop bucket add extras

# Java bucket
scoop bucket add java

# Games bucket
scoop bucket add games

# Nerd Fonts
scoop bucket add nerd-fonts

# Non-portable apps
scoop bucket add nonportable

# Versions (different versions of apps)
scoop bucket add versions
```

---

## Useful Scoop Commands

```powershell
# Search for an app
scoop search <app-name>

# List installed apps
scoop list

# Update all apps
scoop update *

# Uninstall an app
scoop uninstall <app-name>

# Show app information
scoop info <app-name>

# Check for updates
scoop status

# Cleanup old versions
scoop cleanup *

# Show which bucket an app is in
scoop search <app-name>
```

---

## Quick Install Scripts

### Developer Setup

```powershell
# Essential dev tools
scoop install git vscode nodejs python go

# Add extras bucket
scoop bucket add extras

# Install more tools
scoop install docker kubectl terraform postman
```

### Power User Setup

```powershell
# Modern CLI tools
scoop install bat exa ripgrep fd fzf zoxide

# System tools
scoop install 7zip everything winfetch powertoys

# Terminal
scoop install windows-terminal
```

### Media Creator Setup

```powershell
# Add extras bucket
scoop bucket add extras

# Install media tools
scoop install gimp inkscape vlc ffmpeg obs-studio
```

---

## Tips

1. **Always update Scoop first**: `scoop update` before installing new apps
2. **Use extras bucket**: Most GUI apps are in the extras bucket
3. **Cleanup regularly**: `scoop cleanup *` removes old versions
4. **Check app info**: `scoop info <app>` shows details before installing
5. **Portable by default**: Scoop installs apps portably in `~/scoop/apps`

---

## Additional Resources

- [Scoop Official Website](https://scoop.sh)
- [Scoop Directory](https://scoop.sh/#/apps) - Browse all available apps
- [Scoop GitHub](https://github.com/ScoopInstaller/Scoop)
- [Awesome Scoop](https://github.com/ScoopInstaller/Awesome) - Community resources

---

## Why Use Scoop?

- ✅ No admin rights required for most apps
- ✅ No UAC prompts or installers
- ✅ Easy updates: `scoop update *`
- ✅ Clean uninstalls with no leftovers
- ✅ Portable installations
- ✅ Multiple versions of the same app
- ✅ Command-line simplicity
