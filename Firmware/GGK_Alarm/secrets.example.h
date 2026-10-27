#pragma once
// Copy to secrets.h and replace Wi-Fi name/password locally before flashing.
// NEVER put passwords or your portal PIN in a public GitHub repo.
#define GGK_WIFI_SSID ""
#define GGK_WIFI_PASSWORD ""
// Must be >=6 chars. Empty disables phone edit endpoints completely.
#define GGK_PORTAL_PIN ""
// Pacific time and automatic daylight-saving transitions.
#define GGK_TIMEZONE "PST8PDT,M3.2.0/2,M11.1.0/2"
// 0 until physical kit buzzer checked for direct-GPIO-safe passive piezo current.
#define GGK_BUZZER_VERIFIED 0
// Set to 1 only after physical wiring, correct polarity and safe supervised testing.
// This flag informs readiness UI; it does NOT magically make hardware safe.
#define GGK_HARDWARE_INSPECTED 0
// 1: print each debounced button event over Serial at 115200; 0: quiet.
#define GGK_DEBUG_KEY_SERIAL 1
