# GGK Alarm power architectures

| Option | Parts beyond BLARE kit | Survives wall power loss | All sources unplugged | Status |
|---|---|---|---|---|
| A. Regulated USB-C wall adapter | Suitable certified 5 V adapter + cable | No | No | Supported as design; requires inspection + physical testing |
| B. External protected USB power bank | Qualified rechargeable USB power bank + cable | Yes, subject to full-runtime test, if bank has charge | No | Supported as USB source; only after bank/thermal tests |
| C. Internal 1-cell LiPo | Protected 1S pack, positive-locking correctly polarized connector, short protection, safe wiring, mechanical isolation; possibly battery monitoring, backlight switch and RTC | Could, once completely redesigned and approved | Yes | NOT IMPLEMENTED; not part of BLARE kit; no battery purchase/installation authorized |

**Recommend Option A for development and Option B for no-wall-use**. Don't buy a bare Li-ion pouch or attempt to solder one into the PCB. Do not confuse the ESP32-C3's *onboard charging circuitry* with a guaranteed miswire-proof rechargeable appliance. Additional parts and physical inspection are prerequisites for Option C.

The standard kit's TFT BL is hard-wired to GND (active-low ON). That is not a battery-friendly backlight control. A future C revision with deep-sleep operation would require a vetted transistor/current-safe BL driver and runtime alarm/RTC validation; a blank display alone does not remove its power draw.
