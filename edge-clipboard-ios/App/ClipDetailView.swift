import SwiftUI

/// Full clip: selectable text or the full image.
struct ClipDetailView: View {
    @EnvironmentObject private var store: ClipStore
    let clip: Clip
    @State private var copied = 0

    private var current: Clip { store.clips.first { $0.key == clip.key } ?? clip }

    var body: some View {
        ScrollView {
            Group {
                if current.isImage, let img = store.image(for: current) {
                    Image(uiImage: img)
                        .resizable()
                        .scaledToFit()
                        .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
                } else {
                    Text(current.text ?? "")
                        .font(.body)
                        .textSelection(.enabled)
                        .frame(maxWidth: .infinity, alignment: .leading)
                }
            }
            .padding()
            .background(Color(.secondarySystemGroupedBackground), in: RoundedRectangle(cornerRadius: 16, style: .continuous))
            .padding()
        }
        .background(Color(.systemGroupedBackground))
        .navigationTitle(current.isImage ? "Image" : "\(current.text?.count ?? 0) characters")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItemGroup(placement: .bottomBar) {
                Button { store.togglePin(current) } label: {
                    Image(systemName: current.pinned ? "pin.fill" : "pin")
                }
                .accessibilityLabel(current.pinned ? "Unpin" : "Pin")
                Spacer()
                Button {
                    Clipboard.copy(current)
                    copied += 1
                } label: {
                    Label(copied > 0 ? "Copied" : "Copy", systemImage: copied > 0 ? "checkmark" : "doc.on.doc")
                        .labelStyle(.titleAndIcon)
                        .frame(minWidth: 110)
                }
                .buttonStyle(.borderedProminent)
                .buttonBorderShape(.capsule)
                Spacer()
                if let text = current.text {
                    ShareLink(item: text)
                } else if let img = store.image(for: current) {
                    let image = Image(uiImage: img)
                    ShareLink(item: image, preview: SharePreview("Image", image: image))
                }
            }
        }
        .sensoryFeedback(.success, trigger: copied)
    }
}
