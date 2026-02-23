# campbell

Mac Mini running as a headless server. Hosts MCP server, OpenClaw, and other long-lived services.

## Initial Activation SOP

Step-by-step procedure from unboxing to fully headless. Keyboard, mouse, and display are required for this process and can be disconnected at the end.

### Phase 1: macOS Setup Assistant (requires keyboard + mouse + display)

Walk through the system setup wizard:
- Language, region, Wi-Fi (or Ethernet)
- Sign in with Apple ID
- Create user account — remember the username and password

### Phase 2: Establish remote access (still have keyboard + mouse)

Do these in order. SSH first — once SSH is up, you have a remote fallback.

**1. Enable Remote Login (SSH)**

```
sudo systemsetup -setremotelogin on
```

Note: `systemsetup` uses single-dash flags (`-setremotelogin`), not double-dash (`--setremotelogin`).

**2. Enable Screen Sharing**

System Settings → General → Sharing → Screen Sharing → enable.

Settings:
- "Anyone may request permission to control screen" → **off** (headless, no one watching the screen)
- "VNC viewers may control screen with password" → **on**, set a strong password (allows generic VNC clients)
- Remote Management → **do not enable** (conflicts with Screen Sharing, both use port 5900)

**3. Set hostname**
```
sudo scutil --set HostName campbell
sudo scutil --set LocalHostName campbell
sudo scutil --set ComputerName campbell
```

**4. Verify remote access from another machine**

From everest (on the same LAN at this point):
```
ssh blank@campbell.local
```

If this works, everything after this point can be done via SSH if needed.

### Phase 3: Headless prerequisites

**5. Enable auto login**

System Settings → Users & Groups → Automatic Login → select user.

**6. Disable automatic updates**

System Settings → General → Software Update → Automatic Updates → turn off all options.

Unattended updates on a headless server can trigger unexpected reboots or break running services.

**7. Configure power management**
```
sudo pmset -c sleep 0 displaysleep 0 disksleep 0
sudo pmset -c womp 1
sudo pmset -c autorestart 1
```

Verify with `pmset -g`.

| Setting | Value | Effect |
|---------|-------|--------|
| `sleep 0` | disabled | Never sleep on AC power |
| `displaysleep 0` | disabled | No display sleep timeout |
| `disksleep 0` | disabled | No disk sleep timeout |
| `womp 1` | enabled | Wake on LAN |
| `autorestart 1` | enabled | Automatically boot after power loss |

### Phase 4: Install base tools

**8. Install Homebrew**
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
eval "$(/opt/homebrew/bin/brew shellenv)"
```

Do NOT follow Homebrew's suggestion to write to `.zprofile`. The `eval` makes brew available in the current session only. Dotfiles will be managed by chezmoi later.

**9. Install Tailscale and log in**

Install the **cask** (GUI app), not the CLI formula. The GUI app has higher system permissions and auto-starts on boot. Do not install both — they conflict.

```
brew install --cask tailscale
```

Open Tailscale from Applications, sign in. Then set up the CLI alias:

```
alias tailscale="/Applications/Tailscale.app/Contents/MacOS/Tailscale"
```

Do not symlink — use alias only. This alias will be managed by chezmoi later.

Verify from everest:
```
ssh blank@campbell.<tailnet>.ts.net
```

**10. Install 1Password and configure**

```
brew install --cask 1password
brew install 1password-cli
```

Open 1Password desktop app, then:
- Sign in to account
- Settings → Developer → enable "Show 1Password Developer experience"
- Settings → Developer → enable SSH Agent
- Settings → Developer → CLI → enable "Connect with 1Password CLI"
- Edit `~/.config/1Password/ssh/agent.toml` to configure vault scope (will be managed by chezmoi later)

Verify:
```
op whoami
```

### Phase 5: Go headless

**11. Plug in HDMI dummy plug**

Mac Mini without a display drops to minimal resolution, making Screen Sharing unusable. An HDMI dummy plug (passive adapter) forces macOS to render at a normal resolution.

**12. Disconnect keyboard, mouse, display**

**13. Hard power test**

Pull the power cord, wait a few seconds, plug back in. Verify:
- campbell boots automatically (`autorestart 1`)
- Auto login succeeds (no keyboard prompt)
- Tailscale connects (GUI app auto-starts)
- SSH reachable from everest: `ssh blank@campbell.<tailnet>.ts.net`
- 1Password SSH agent working: `op whoami`

## Steady-State Operation

After the initial setup, campbell runs unattended. No physical interaction needed — `autorestart 1` handles power loss recovery, Tailscale GUI app auto-starts, auto login bypasses the lock screen.

### Boot Sequence

```
Power on (or auto-restart after power loss)
  → macOS boot
  → Auto login (no keyboard needed)
  → Tailscale GUI app connects automatically
  → launchd starts all agents (MCP server, etc.)
  → SSH reachable at campbell.<tailnet>.ts.net
```

### Service Auto-Start

Long-lived services run as launchd user agents under `~/Library/LaunchAgents/`. Each plist sets `RunAtLoad` and `KeepAlive` so services start on login and restart on crash.

### Headless Display

HDMI dummy plug stays plugged in permanently. This keeps Screen Sharing usable for the rare cases when a GUI is needed.

### Notes

- Tailscale: use cask (GUI app), not CLI formula. CLI access via alias, not symlink.
- Automatic updates are disabled. Run `softwareupdate` manually via SSH when needed.
- `agent.toml` and Tailscale alias are temporary manual config — both will be managed by chezmoi once deployed.
