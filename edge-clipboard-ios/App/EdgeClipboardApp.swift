import SwiftUI
import UIKit

@main
struct EdgeClipboardApp: App {
    @StateObject private var store = ClipStore.shared
    @Environment(\.scenePhase) private var phase

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(store)
                .onChange(of: phase) { _, newPhase in
                    guard newPhase == .active else { return }
                    store.prune()
                    PasteboardWatcher.saveIfChanged(store)
                }
        }
    }
}

/// iOS only lets an app read the clipboard while it is open. When the app opens, it saves
/// a new clipboard item once (iOS can ask "Allow Paste"; choose "Allow" in Settings to stop that).
enum PasteboardWatcher {
    static func saveIfChanged(_ store: ClipStore) {
        guard Settings.saveOnOpen else { return }
        let pb = UIPasteboard.general
        let d = AppGroup.defaults
        guard pb.changeCount != d.integer(forKey: Settings.lastChangeKey) else { return }
        d.set(pb.changeCount, forKey: Settings.lastChangeKey)
        if pb.hasImages, let img = pb.image {
            store.addImage(img)
        } else if pb.hasStrings, let s = pb.string {
            store.addText(s)
        } else if pb.hasURLs, let u = pb.url {
            store.addText(u.absoluteString)
        }
    }
}
