BCC950 Mute Indicator
A tiny Python utility that listens to the physical mute button on the Logitech BCC950 ConferenceCam and shows a floating, always-on-top overlay indicating whether the microphone is MUTED (red) or ACTIVE (green).

The BCC950's mute button works at the hardware level and doesn't expose any state to Windows, so this script reads the raw HID reports (usage 0x0B:0x2F) directly through pywinusb. No drivers, no admin rights, no system-wide audio hooks — just a lightweight overlay you can drag anywhere on screen.

Features

Detects physical mute button presses via raw HID

Floating overlay with live status (muted / active)

Draggable with left click, right click to close

Auto-reconnects if the camera is unplugged

Debounced press detection + rotating log (bcc950.log)

Single file, no install required beyond pywinusb
