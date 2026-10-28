# JJK Alarm: canonical project name

**JJK Alarm** is the sole current name of this BLARE project.

- Product name and default screen caption: **JJK Alarm**.
- Firmware sketch: `Firmware/JJK_Alarm/JJK_Alarm.ino`.
- Arduino application namespace: `jjk`; hardware-pin namespace: `jjkpin`.
- Configuration macros: `JJK_*`.
- Local phone-control address: `http://jjk-alarm.local/` (where mDNS works), or the local device IP.
- Persistent settings namespace: `jjk-alarm`.
- Default audio safety flags remain OFF until the real hardware has been inspected.
- Archival snapshots are intentionally unchanged, and do not establish the current project name.

**Settings when updating from older development firmware:** This naming update also changes the persistent settings namespace. Previously saved alarm settings will not be imported automatically. Re-enter time/alarm settings after flashing and verify them before relying on the alarm.

Apply this name consistently in future repository changes, documents and conversation handoffs.
