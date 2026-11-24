import Foundation

/// Storage that the app and its extensions (keyboard, share, widget) all read and write.
enum AppGroup {
    static let id = "group.io.github.slinkybat123.edgeclip"

    static var container: URL {
        FileManager.default.containerURL(forSecurityApplicationGroupIdentifier: id)
            ?? FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
    }

    static var defaults: UserDefaults { UserDefaults(suiteName: id) ?? .standard }
}

/// All user settings. Views use @AppStorage with the same keys and `store: AppGroup.defaults`.
enum Settings {
    static let textSizeKey = "textSize"
    static let linesKey = "previewLines"
    static let maxKey = "maxClips"
    static let unlimitedKey = "unlimited"
    static let autoDeleteKey = "autoDelete"
    static let saveOnOpenKey = "saveOnOpen"
    static let lastChangeKey = "lastChangeCount"

    /// Maximum number of clips; 0 = no limit.
    static var maxClips: Int {
        let d = AppGroup.defaults
        if d.bool(forKey: unlimitedKey) { return 0 }
        return d.object(forKey: maxKey) as? Int ?? 30
    }

    /// Age after which unpinned clips are deleted; 0 = never.
    static var autoDeleteSeconds: TimeInterval {
        let values: [TimeInterval] = [0, 3_600, 86_400, 604_800, 2_592_000]
        let i = AppGroup.defaults.integer(forKey: autoDeleteKey)
        return values[min(max(i, 0), values.count - 1)]
    }

    static var saveOnOpen: Bool { AppGroup.defaults.object(forKey: saveOnOpenKey) as? Bool ?? true }
}
