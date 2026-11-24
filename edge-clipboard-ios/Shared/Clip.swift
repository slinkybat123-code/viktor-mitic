import Foundation

/// One clipboard item: text or an image file.
struct Clip: Codable, Identifiable, Hashable {
    var id: UUID
    var text: String?
    var imageFile: String?
    var date: Date
    var pinned: Bool
    /// Hash of the content, used to find duplicates.
    var key: String

    var isImage: Bool { imageFile != nil }

    static let sample = Clip(id: UUID(), text: "Meet at 7 pm", imageFile: nil, date: .now, pinned: false, key: "sample")
}
