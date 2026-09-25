<div align="center">
  <img src="logo.svg" alt="Roblox FastFlag Manager" width="600">
</div>

<div align="center">

![Version](https://img.shields.io/badge/version-v4.2.0-blue.svg)
[![Discord][shield-discord-server]][discord-invite]
![Platform](https://img.shields.io/badge/platform-Windows-white.svg)
![Modifiable FFlags](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2F4anti%2FRoblox-Fastflag-Manager%2Fmain%2Fbadges%2Ffflags.json)

</div>

<div align="center">
  <b>A lightweight, open-source, high-performance FastFlag Manager giving you complete control over Roblox FastFlags.</b><br>
  Optimized for everything from high-end to low-end hardware.
</div>

<br>

<div align="center">
  <img src="https://i.ibb.co/JRQF7LzY/Menu-Picture-Normal-just-the-starting.png" alt="Roblox FastFlag Manager Main Interface" width="800">
</div>

---

## Background mode (this fork)

Windows CMD, from the repository folder:

```bat
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
ffm gui
```

Configure your flags, hotkeys and Auto Apply in the GUI, then fully exit it.

```bat
ffm start
ffm status
ffm apply
ffm stop
ffm gui
```

`start` launches a detached background process: no visible window, taskbar
button, tray icon, or extra console. You may close CMD afterward. The existing
WebView and app workers still run, using saved settings; Auto Apply must already
be enabled if you want automatic application. This is not a reduced-memory
headless engine. The process remains visible in Task Manager.

`apply` requests the same action as the GUI Apply button in the running instance,
including resuming flags if paused. It reapplies the flags already loaded by the
app; it does not reload externally edited files or download offsets. The command
confirms the request was sent, not that flags successfully applied. Results are
logged in `%USERPROFILE%\.FFlagManager\logs\fflag_manager.log`. The existing apply
sound remains conditional on a successful apply and your sound settings. Apply
chimes use Windows audio directly, so hidden-browser autoplay restrictions do
not silence them. Playback errors are written to the same log.
After updating an already running copy, run `ffm stop` and `ffm start` once to
enable this command.

`status` returns exit code 0 when ready, 1 when starting/stopped. `stop` uses the
normal application shutdown/cleanup. Stop before reopening the GUI; restoring
an initially hidden WebView2 window is unreliable. These commands control only
instances launched by this fork, within the current Windows login session.
Duplicate launches are rejected. Close any separately installed upstream FFM
before using this fork.

Startup errors are recorded in `%USERPROFILE%\.FFlagManager\logs\background-startup.log`.
The fork shares the original application's saved configuration. Automatic app
update checks are disabled so an upstream installer cannot replace these changes;
flag-offset and Roblox-version functionality remains as before.

For console diagnostics: `ffm run --background` runs attached to the current CMD.
For a packaged build, `FFM.exe start`, `FFM.exe stop`, and `FFM.exe gui` also work,
but the upstream windowless EXE build does not print console output. Use `ffm.cmd`
for readable status and errors. The source launcher is now included in this fork.

## 📑 Table of Contents

- [✨ Showcase](#showcase)
- [✨ Key Features](#key-features)
- [🌿 Supported Bootstrappers](#variants)
- [📥 Installation](#installation)
- [🎮 How to Use](#how-to-use)
- [💬 Discord Server](#community--support)
- [⭐ Star History](#star-history)
- [⚖️ License](#license)

---

<div>

## <a name="showcase"></a>✨ Showcase

</div>

<details open>
  <summary><b>View Features in Action</b></summary>
  <br>
  <div>
    <table border="0">
      <tr>
        <td valign="top">
          <img src="https://i.ibb.co/CNKnS9b/Menu-pic-2-with-white-matrix-theme.png" alt="Matrix Theme" width="450"><br>
          <b>🎨 Dynamic Themes</b><br>
          <i>Personalize your experience with themes like White Matrix.</i>
        </td>
        <td valign="top">
          <img src="https://i.ibb.co/XkJtMs8r/right-click-menu-pic.png" alt="Context Menu" width="450"><br>
          <b>⚡ Advanced Controls</b><br>
          <i>Powerful right-click menus for rapid flag management and offsets.</i>
        </td>
      </tr>
    </table>
  </div>
</details>

---

<div>

## <a name="key-features"></a>✨ Key Features

| | Feature | Description |
|:---:|:---|:---|
| ⛑️ | **Bloxstrap & Variants Support** | Interfaces with multiple bootstrappers simultaneously |
| ⚡ | **Instant Indexing** | Search through thousands of FFlags in milliseconds |
| 🛠️ | **Smart Presets** | Create, merge, and toggle complex configurations instantly |
| 🧩 | **Bindable FastFlags** | Assign keybinds to toggle or cycle specific FastFlags |
| 🛰️ | **Update Proof** | Automated code and FFlag offset updates |
| ☘️ | **Manual / Auto Updates** | Switch between auto and manual update control |
| 🎨 | **Rich UI Themes** | Beautiful aesthetic themes for a seamless experience |
| 🔒 | **Secure & Undetectable** | Reliable, trace-free deployment pipeline with stealth |
| 📦 | **Standalone Installer** | Pre-compiled Windows executable, no Python required |

</div>

---

<div>

## <a name="variants"></a>🌿 Supported Bootstrappers

| Variant | Supported |
| :--- | :---: |
| **Bloxstrap** | ✅ |
| **Voidstrap** | ✅ |
| **Fishstrap** | ✅ |
| **Others** | ✅ |

</div>

---

<div>

## <a name="installation"></a>📥 Installation

### <a name="windows-installer"></a>Windows Installer (Recommended)

1. Navigate to the **[Releases](../../releases)** page of this repository.
2. Download the latest `FFM_Installer.exe`.
3. Run the executable and follow the setup instructions.
4. Launch the application from the Start menu.

</div>

<div>

### <a name="build-from-source"></a>Building from Source (For Developers)

**Prerequisites:** [Python 3.10+](https://www.python.org/downloads/) · [Git](https://git-scm.com/downloads) · [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) *(Desktop development with C++ workload)*

</div>

```bash
git clone https://github.com/4anti/Roblox-Fastflag-Manager.git
cd Roblox-Fastflag-Manager
pip install -r requirements.txt
python main.pyw
```

---

<div>

## <a name="how-to-use"></a>🎮 How to Use

| Step | Action | Description |
| :---: | :--- | :--- |
| 1 | **Search** | Use the search bar to find specific FFlags or browse by category |
| 2 | **Presets** | Drag and drop presets, reorder them, and share them |
| 3 | **Keybinds** | Assign hotkeys to toggle specific flags or presets instantly while in-game |
| 4 | **Apply** | Click the *Apply* button to inject settings into your Roblox client |

</div>

---

<div>

## <a name="community--support"></a>💬 Discord Community & Support

Join the official Discord for support, preset sharing, and community discussion.

[**Join the Discord Server →**](https://discord.gg/ECekjAkQu7)

</div>

---

<div>

## <a name="star-history"></a>⭐ Star History

<a href="https://www.star-history.com/?repos=4anti%2FRoblox-Fastflag-Manager&type=timeline&legend=bottom-right">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=4anti/Roblox-Fastflag-Manager&type=timeline&theme=dark&legend=bottom-right&sealed_token=xgPKRazom_r-a2oO6wMpovaLVDfDLRzznnKRijber25QM5NzfXkYf3pYCOA-m92NejtEHnjsxDz-ZNMbWpDqh9m2LSDjIPWI7V6pgFoeF0piPiXBliMQSznMHFjR85MitR4ELoY7UyYbXJlX9zFYICBjJoLnmNxiAGaHffNQKF-vy1Y3m8hExJePUx99" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=4anti/Roblox-Fastflag-Manager&type=timeline&legend=bottom-right&sealed_token=xgPKRazom_r-a2oO6wMpovaLVDfDLRzznnKRijber25QM5NzfXkYf3pYCOA-m92NejtEHnjsxDz-ZNMbWpDqh9m2LSDjIPWI7V6pgFoeF0piPiXBliMQSznMHFjR85MitR4ELoY7UyYbXJlX9zFYICBjJoLnmNxiAGaHffNQKF-vy1Y3m8hExJePUx99" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=4anti/Roblox-Fastflag-Manager&type=timeline&legend=bottom-right&sealed_token=xgPKRazom_r-a2oO6wMpovaLVDfDLRzznnKRijber25QM5NzfXkYf3pYCOA-m92NejtEHnjsxDz-ZNMbWpDqh9m2LSDjIPWI7V6pgFoeF0piPiXBliMQSznMHFjR85MitR4ELoY7UyYbXJlX9zFYICBjJoLnmNxiAGaHffNQKF-vy1Y3m8hExJePUx99" />
 </picture>
</a>

---

<div>

## <a name="license"></a>⚖️ License

This project is licensed under the **PolyForm Noncommercial License 1.0.0**. Noncommercial use only — see [`LICENSE`](LICENSE) for the full terms.

---

*Developed by **4anti** with ❤️ for the Roblox community.*

</div>

[shield-discord-server]: https://img.shields.io/discord/1487010055931953152?logo=discord&logoColor=white&label=discord&color=aaaaa
[discord-invite]:  https://discord.gg/HnqyxsAXhz
