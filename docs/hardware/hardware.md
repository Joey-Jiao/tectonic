# Hardware

## Fleet

| Host | OS | Role | Preset | Notes |
|------|----|------|--------|-------|
| everest | macOS | workstation | workstation | Primary development machine |
| campbell | macOS | server | server + dev-node | Runs MCP server, OpenClaw, and other long-lived services |
| granite | Linux | workstation | workstation + apps-docker | Linux development environment |

## Roles

**workstation** — Daily driver for development. Gets the full toolchain: compilers, language runtimes, editor configs, desktop utilities.

**server** — Runs long-lived services. Gets base tools and specific runtimes needed by its services, nothing more.

## Network

All machines are connected via a Tailscale mesh network, reachable from any network without relying on LAN discovery (mDNS).

| Host | Tailscale Hostname |
|------|--------------------|
| everest | `everest.<tailnet>.ts.net` |
| campbell | `campbell.<tailnet>.ts.net` |
| granite | `granite.<tailnet>.ts.net` |

SSH between machines uses traditional SSH over Tailscale (not Tailscale SSH), authenticated through the 1Password SSH agent.
