import AppIntents
import UIKit

/// "Save Clipboard": for Shortcuts, Siri, Back Tap and the Action button.
struct SaveClipboardIntent: AppIntent {
    static var title: LocalizedStringResource = "Save Clipboard"
    static var description = IntentDescription("Saves what you copied to Edge Clipboard.")
    static var openAppWhenRun: Bool = false

    @MainActor
    func perform() async throws -> some IntentResult & ProvidesDialog {
        let pb = UIPasteboard.general
        var saved = false
        if pb.hasImages, let img = pb.image {
            saved = ClipStore.shared.addImage(img)
        } else if let s = pb.string {
            saved = ClipStore.shared.addText(s)
        } else if let u = pb.url {
            saved = ClipStore.shared.addText(u.absoluteString)
        }
        AppGroup.defaults.set(pb.changeCount, forKey: Settings.lastChangeKey)
        if saved {
            return .result(dialog: "Saved to Edge Clipboard")
        }
        return .result(dialog: "Nothing new to save")
    }
}

struct OpenClipboardIntent: AppIntent {
    static var title: LocalizedStringResource = "Open Clipboard"
    static var openAppWhenRun: Bool = true

    func perform() async throws -> some IntentResult { .result() }
}

struct EdgeClipboardShortcuts: AppShortcutsProvider {
    static var appShortcuts: [AppShortcut] {
        AppShortcut(intent: SaveClipboardIntent(),
                    phrases: ["Save clipboard in \(.applicationName)", "Save to \(.applicationName)"],
                    shortTitle: "Save Clipboard",
                    systemImageName: "doc.on.clipboard")
        AppShortcut(intent: OpenClipboardIntent(),
                    phrases: ["Open \(.applicationName)"],
                    shortTitle: "Open Clipboard",
                    systemImageName: "list.clipboard")
    }
}
