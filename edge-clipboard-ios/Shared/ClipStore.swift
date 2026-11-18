import Foundation
import CryptoKit
import UIKit
#if canImport(WidgetKit)
import WidgetKit
#endif

/// Clipboard history in the App Group container (clips.json + images/).
/// Text length has no limit. The oldest unpinned clip is deleted first.
final class ClipStore: ObservableObject {
    static let shared = ClipStore()

    @Published private(set) var clips: [Clip] = []

    private static var fileURL: URL { AppGroup.container.appendingPathComponent("clips.json") }
    static var imageDir: URL { AppGroup.container.appendingPathComponent("images", isDirectory: true) }
    private let cache = NSCache<NSString, UIImage>()

    init() {
        try? FileManager.default.createDirectory(at: Self.imageDir, withIntermediateDirectories: true)
        reload()
    }

    // MARK: Read

    /// Reads the clips from disk without an instance (for the widget and the keyboard).
    static func loadSnapshot() -> [Clip] {
        guard let data = try? Data(contentsOf: fileURL),
              let list = try? JSONDecoder().decode([Clip].self, from: data) else { return [] }
        return sorted(list)
    }

    func reload() { clips = Self.loadSnapshot() }

    private static func sorted(_ list: [Clip]) -> [Clip] {
        list.sorted { a, b in a.pinned != b.pinned ? a.pinned : a.date > b.date }
    }

    func image(for clip: Clip) -> UIImage? {
        guard let name = clip.imageFile else { return nil }
        if let hit = cache.object(forKey: name as NSString) { return hit }
        guard let img = UIImage(contentsOfFile: Self.imageDir.appendingPathComponent(name).path) else { return nil }
        cache.setObject(img, forKey: name as NSString)
        return img
    }

    // MARK: Write

    @discardableResult
    func addText(_ raw: String) -> Bool {
        let text = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty else { return false }
        return insert(Clip(id: UUID(), text: text, imageFile: nil, date: .now, pinned: false,
                           key: "t:" + Self.hash(Data(text.utf8))))
    }

    @discardableResult
    func addImage(_ image: UIImage) -> Bool {
        guard let data = image.pngData() else { return false }
        let key = "i:" + Self.hash(data)
        reload()
        let name = clips.first(where: { $0.key == key })?.imageFile ?? "\(UUID().uuidString).png"
        let url = Self.imageDir.appendingPathComponent(name)
        if !FileManager.default.fileExists(atPath: url.path) {
            guard (try? data.write(to: url, options: .atomic)) != nil else { return false }
        }
        return insert(Clip(id: UUID(), text: nil, imageFile: name, date: .now, pinned: false, key: key))
    }

    func togglePin(_ clip: Clip) {
        reload()
        guard let i = clips.firstIndex(where: { $0.key == clip.key }) else { return }
        var list = clips
        list[i].pinned.toggle()
        save(list)
    }

    func delete(_ clip: Clip) {
        reload()
        removeFiles(of: [clip], keeping: [])
        save(clips.filter { $0.key != clip.key })
    }

    func clearUnpinned() {
        reload()
        let keep = clips.filter(\.pinned)
        removeFiles(of: clips.filter { !$0.pinned }, keeping: keep)
        save(keep)
    }

    func clearAll() {
        reload()
        removeFiles(of: clips, keeping: [])
        save([])
    }

    /// Applies auto-delete and the maximum number of clips.
    func prune() {
        reload()
        var list = clips
        let age = Settings.autoDeleteSeconds
        if age > 0 {
            let limit = Date().addingTimeInterval(-age)
            list.removeAll { !$0.pinned && $0.date < limit }
        }
        list = trimmed(list)
        if list.count != clips.count {
            removeFiles(of: clips.filter { c in !list.contains { $0.key == c.key } }, keeping: list)
            save(list)
        }
    }

    // MARK: Private

    private func insert(_ clip: Clip) -> Bool {
        reload() // other processes (keyboard, share, widget) can have changed the file
        if let latest = clips.max(by: { $0.date < $1.date }), latest.key == clip.key { return false }
        var list = clips
        let old = list.first { $0.key == clip.key }
        list.removeAll { $0.key == clip.key }
        var new = clip
        new.pinned = old?.pinned ?? false
        list.insert(new, at: 0)
        let kept = trimmed(list)
        removeFiles(of: list.filter { c in !kept.contains { $0.key == c.key } }, keeping: kept)
        save(kept)
        return true
    }

    private func trimmed(_ list: [Clip]) -> [Clip] {
        let max = Settings.maxClips
        guard max > 0, list.count > max else { return list }
        var out = list
        while out.count > max {
            let unpinned = out.enumerated().filter { !$0.element.pinned }
            guard let oldest = unpinned.min(by: { $0.element.date < $1.element.date }) else { break }
            out.remove(at: oldest.offset)
        }
        return out
    }

    private func removeFiles(of removed: [Clip], keeping: [Clip]) {
        for c in removed {
            guard let name = c.imageFile, !keeping.contains(where: { $0.imageFile == name }) else { continue }
            try? FileManager.default.removeItem(at: Self.imageDir.appendingPathComponent(name))
            cache.removeObject(forKey: name as NSString)
        }
    }

    private func save(_ list: [Clip]) {
        let sorted = Self.sorted(list)
        if let data = try? JSONEncoder().encode(sorted) {
            try? data.write(to: Self.fileURL, options: .atomic)
        }
        let apply = { self.clips = sorted }
        if Thread.isMainThread { apply() } else { DispatchQueue.main.async(execute: apply) }
        #if canImport(WidgetKit)
        WidgetCenter.shared.reloadAllTimelines()
        #endif
    }

    private static func hash(_ data: Data) -> String {
        SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined()
    }
}

/// Puts a clip on the system pasteboard.
enum Clipboard {
    static func copy(_ clip: Clip) {
        if clip.isImage, let img = ClipStore.shared.image(for: clip) {
            UIPasteboard.general.image = img
        } else if let text = clip.text {
            UIPasteboard.general.string = text
        }
        // Do not save our own copy again as a "new" clip.
        AppGroup.defaults.set(UIPasteboard.general.changeCount, forKey: Settings.lastChangeKey)
    }
}
