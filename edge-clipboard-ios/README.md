# Edge Clipboard for iPhone

A clipboard history app with an iOS look: large titles, inset grouped lists, swipe actions, context menus, materials and haptics. iOS 17 or later.

## What is different from Android
iOS does not let apps show a handle over other apps or read the clipboard in the background. The iPhone version uses the iOS ways to reach your clips from anywhere:

| Android | iPhone |
|---|---|
| Edge handle + panel | **Clipboard keyboard** (tap a clip to type it in any app) and **Home Screen widget** (tap a clip to copy it) |
| Saves each copy at once | Saves when you open the app, with **Paste**, from the **Share sheet**, or with **Back Tap** (tap the back of the iPhone twice) |

## Features
- Clip list with search, Pinned and Recent sections, and a capsule **Copy** button on each clip.
- Tap a clip: full text (selectable) or full image, with Copy, Pin and Share.
- Swipe right to pin, swipe left to delete, or touch and hold for a menu.
- Text and images. No size limit for one clip.
- Settings: text size, preview lines, maximum clips (5–500 or no limit), auto-delete, save when the app opens.
- Keyboard extension, share extension, interactive widget (small, medium, large).
- Shortcuts / Siri: "Save Clipboard" and "Open Clipboard". Use "Save Clipboard" with Back Tap or the Action button.

## Build on a Mac
1. Install Xcode 16 or later from the App Store.
2. Install XcodeGen: `brew install xcodegen` (Homebrew: https://brew.sh).
3. In this folder: `xcodegen generate`, then open `EdgeClipboard.xcodeproj`.
4. Select the **EdgeClipboard** target > **Signing & Capabilities** > select your **Team**. Do the same for the 3 extension targets (**EdgeClipboardKeyboard**, **EdgeClipboardShare**, **EdgeClipboardWidget**). Xcode creates the App Group `group.io.github.slinkybat123.edgeclip`.
5. Connect your iPhone and select **Run**.

A free Apple ID can run the app on your own iPhone for 7 days. To publish, you need the paid Apple Developer Program (see APP-STORE.md).

The GitHub workflow **Edge Clipboard iOS build check** compiles the app for the Simulator on every change.
