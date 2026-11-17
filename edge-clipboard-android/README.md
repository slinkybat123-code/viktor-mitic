# One UI Clipboard (Android)

A floating edge handle that opens a clipboard history panel, in the style of the One UI Edge Panel clipboard.

## Features
- Thin rounded handle on the screen edge. Default size 7 × 72 dp (about the size of the Find X9 Pro volume rocker). Width, height, opacity and distance from the edge are adjustable.
- Swipe out from the handle to open the panel. The handle follows your finger. A short swipe (20 dp) or a fast flick opens it. A tap only makes the handle bounce.
- The handle asks Android to exclude its area from the system back gesture (Android 10+). If ColorOS still takes the swipe, increase "Distance from edge".
- One UI style panel: a full-height column on the edge, large previews, a full-width **Copy** bar under each preview, and a **Clear** pill at the bottom.
- Tap a preview to see the full clip (scrollable, selectable text, or the full image), with a Copy bar.
- Touch and hold a preview to show Pin and Delete.
- Text keeps the colours and formatting of the source app when the app gives them.
- Images are saved too (a copy goes to `files/images`). Copy puts the image back on the clipboard.
- No size limit on one clip. Android limits one clipboard transfer to about 1 MB, so text longer than 250,000 characters is copied back as a text file.
- Touch and hold the handle (0.4 s, with vibration) to drag it. On release it springs to the nearest left or right edge. The position is saved.
- Panel with rounded corners, spring slide-in, fade scrim and staggered list animation. Dark mode follows the system.
- "Clear" deletes all clips that are not pinned.
- Clips are saved in app storage (`files/clips.json`). Maximum 30 clips. When a new clip arrives, the oldest clip that is not pinned is deleted.
- Clips marked as sensitive (for example passwords) are not saved.

## Settings (all adjustable in the app, with a live preview)
- **Handle:** screen side, colour, width, height, opacity, distance from edge, swipe distance, hold time, tap to open, lock position, vibration.
- **Panel:** theme (system, light, dark), width, opacity, background blur (Android 12+), background dim, corner radius, space at top, animation speed.
- **Clips:** text size, preview lines, clip opacity, corner radius, space between clips, padding, Copy bar on or off, Copy bar height and text size, keep original colours, close after copy.
- **Storage:** maximum clips (5–500) or no limit, auto-delete after 1 hour / 1 day / 7 days / 30 days, save images, storage location (app storage, plus an optional copy in a folder you choose), delete all clips, reset all settings.

See `PUBLISHING.md` to publish on Google Play and `PRIVACY.md` for the privacy policy.

## Install the APK
1. Copy `release/EdgeClip-debug.apk` to the phone and open it. Allow "Install unknown apps" if asked.
2. Open One UI Clipboard and turn on each permission row.
3. Turn on "Show edge handle".

## Build from source
1. Install Android Studio (on Windows, install to `E:\CLAUDE\Android Studio`, with the SDK in `E:\CLAUDE\Android\Sdk`).
2. File > Open > this folder. Let Gradle sync.
3. Run > Run 'app' with the phone connected by USB (USB debugging on).
   Command line: `gradlew assembleDebug` → `app/build/outputs/apk/debug/app-debug.apk`.

## How clipboard capture works
Android 10 and later block background apps from reading the clipboard. One UI Clipboard uses two methods:
1. **Copy detection (accessibility service, recommended):** When you tap "Copy", or a "Copied" message shows, the app adds a 1 × 1 px focusable window for less than one second, reads the clipboard, and removes the window. The service does not read screen content.
2. **Panel open:** Each time the panel opens, it reads the current clipboard.

Without copy detection, only the last item you copied before you opened the panel is saved.

## Oppo / ColorOS checks
- Settings > Apps > One UI Clipboard > Battery usage: allow background activity and auto launch.
- Lock the app in Recent apps.
- ColorOS can turn off accessibility services after an update. Turn on Copy detection again if clips stop saving.

## On-device test list
- [ ] Handle shows on the right edge with the correct size.
- [ ] Swipe out opens the panel. A tap does not. The system back gesture does not start.
- [ ] Back and tap outside close the panel. Back in the full clip view goes back to the list.
- [ ] Copy an image in Gallery or Chrome. It shows in the panel and pastes into a chat.
- [ ] Copy coloured text. The colours show in the preview.
- [ ] Copy a very long text. The full text shows when you tap the preview.
- [ ] Hold, then drag, moves the handle. Release snaps to the nearest edge. Position stays after a restart.
- [ ] Copy text in Chrome or WhatsApp. The clip shows in the panel.
- [ ] Copy 31 clips. Only 30 stay. Pinned clips stay.
- [ ] Rotation repositions the handle.
- [ ] Handle comes back after a phone restart.
