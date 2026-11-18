import AppIntents
import UIKit

/// Used by the interactive widget: tap a clip to copy it.
struct CopyClipIntent: AppIntent {
    static var title: LocalizedStringResource = "Copy Clip"
    static var isDiscoverable: Bool = false

    @Parameter(title: "Clip ID")
    var clipID: String

    init() {}
    init(clipID: String) { self.clipID = clipID }

    func perform() async throws -> some IntentResult {
        if let clip = ClipStore.loadSnapshot().first(where: { $0.id.uuidString == clipID }) {
            await MainActor.run { Clipboard.copy(clip) }
        }
        return .result()
    }
}
