# Syncthing

Syncthing handles Layer 3 (Data) — continuous synchronization of user data between machines. It runs over the Tailscale mesh network (Layer 0), so it works from any network without port forwarding or discovery servers.

## Synced Folders

| Folder | Content | Machines |
|--------|---------|----------|
| `workspace` | Code repositories, research knowledge base | everest ↔ campbell ↔ granite |
| `misc` | Personal documents, portraits, miscellaneous files | everest ↔ campbell ↔ granite |
| `archive` | Previous code, archived content | everest ↔ campbell ↔ granite |

## Why Syncthing

- Peer-to-peer, no cloud dependency
- Works over Tailscale IPs, no need for relay servers
- Selective sync per folder and per machine
- Conflict handling for concurrent edits
- Versioning and trash retention as safety net

## Relationship to Other Layers

Syncthing only syncs user-created data. It does not replace:
- chezmoi (Layer 2) for dotfiles — config files are templated per machine, not copied verbatim
- tectonic (Layer 1) for software — installed packages are declared, not synced
- Git for source code version control — Syncthing ensures code repos are present on each machine, Git manages their history
