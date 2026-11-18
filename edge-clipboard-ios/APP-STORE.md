# Publish Edge Clipboard on the App Store

You need a **Mac with Xcode** and the **Apple Developer Program** (USD 99 per year). Claude cannot sign or upload the app for you.

| Item | Value |
|---|---|
| Name | Edge Clipboard |
| Bundle ID | `io.github.slinkybat123.edgeclip` (+ `.keyboard`, `.share`, `.widget`) |
| App Group | `group.io.github.slinkybat123.edgeclip` |
| Category | Productivity |
| Price | Free |
| Privacy policy | Same page as Android: `docs/privacy.html` (see the Android PUBLISHING.md, step 5) |
| Support / contact email | slinkybat123@gmail.com |

## Step 1. Join the Apple Developer Program
https://developer.apple.com/programs/enroll — enroll as an individual. Approval can take 1–2 days.

## Step 2. Build and test
Follow README.md ("Build on a Mac"). Test on your iPhone: keyboard, widget, share sheet, Back Tap.

## Step 3. Create the app in App Store Connect
1. https://appstoreconnect.apple.com > **Apps > + > New App**.
2. Platform iOS, name **Edge Clipboard**, language English (U.S.), bundle ID `io.github.slinkybat123.edgeclip`, SKU `edgeclip-ios`.

## Step 4. Upload the build
1. In Xcode, select **Any iOS Device (arm64)** as the destination.
2. **Product > Archive**. When the Organizer opens, select **Distribute App > App Store Connect > Upload**.
3. After processing (10–30 minutes), the build shows in App Store Connect under **TestFlight**. Test it with TestFlight on your iPhone first.

## Step 5. App information
- **Subtitle (30):** Your clipboard, one tap away
- **Promotional text (170):** Every copy saved. Paste it from the clipboard keyboard, copy it from the widget, or save anything from the share sheet.
- **Description:**
  Edge Clipboard keeps everything you copy. Find it again in a clean list, pin what you need, and paste it anywhere.
  • Clipboard keyboard: tap a clip to type it in any app.
  • Home Screen widget: tap a clip to copy it.
  • Share sheet: save text, links and images from any app.
  • Back Tap and Shortcuts: tap the back of your iPhone to save what you copied.
  • Search, pin, swipe to delete, full text view with selection.
  • Text and images, no size limit for a clip.
  • Adjustable text size, preview lines, clip limit and auto-delete.
  • Private: clips stay on your iPhone. No account, no tracking, no network access.
- **Keywords (100):** clipboard,paste,copy,history,keyboard,widget,clips,manager,notes,snippets
- **Screenshots:** 6.9-inch iPhone (1320 × 2868) — at least 3. Take them in the Simulator (iPhone 16 Pro Max, **File > Save Screen**) or on a large iPhone: the list, the full clip view, the keyboard, the widget.

## Step 6. App Privacy
**App Store Connect > App Privacy > Get Started:** "Do you or your third-party partners collect data from this app?" → **No**.

## Step 7. Review notes (important for keyboard apps)
In **App Review Information > Notes**, write:
> The keyboard extension asks for Full Access only to read the clip history that the user saved in the shared App Group container. The keyboard has no network access, does not log keystrokes, and does not send any data. The app reads the clipboard only when the user opens the app, taps Paste, uses the share sheet, or runs the "Save Clipboard" shortcut.

## Step 8. Submit
Select the build, set **Age rating** (all answers **None** → 4+), then **Add for Review > Submit**. Review usually takes 1–3 days.

## Each update
Increase `MARKETING_VERSION` and `CURRENT_PROJECT_VERSION` in `project.yml`, run `xcodegen generate`, then archive and upload again.
