# Bluetooth Proximity Lock for Linux

A Python script to automatically lock/unlock a Linux desktop based on the proximity of your phone.

---
## 🚀 Quick Setup

### 1. Install Dependencies
```bash
sudo pacman -S python bluez-utils slock xdotool playerctl libnotify
```

### 2. Configure Permissions
This only needs to be done once.
```bash
sudo setcap 'cap_net_raw,cap_net_admin+eip' /usr/bin/l2ping
```

### 3. Create `config.ini`
Create this file in the same directory as your script. It is pre-filled with your settings.

```ini
[settings]
phone_mac = 00:11:22:AA:BB:CC
lock_command = slock
poll_interval = 5
rssi_threshold = -65
enable_logging = true
enable_media_control = true
# set password
password = your_password_here
```

### 4. Enable Autostart
Add the following line to `~/.fluxbox/startup` before the `exec fluxbox` line. **Use the full path to your script.**

```bash
/path/to/your/proximity_lock.py &
```

---
## ▶️ Usage

The script runs automatically on login. To test or debug, run it directly in your terminal:
```bash
python proximity_lock.py
```