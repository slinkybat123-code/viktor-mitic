import UIKit
import SwiftUI
import UniformTypeIdentifiers

/// Share sheet target: saves shared text, links and images to Edge Clipboard.
final class ShareViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .clear
        Task { @MainActor in
            let count = await saveAttachments()
            showConfirmation(saved: count > 0)
            try? await Task.sleep(nanoseconds: 900_000_000)
            extensionContext?.completeRequest(returningItems: nil)
        }
    }

    @MainActor
    private func saveAttachments() async -> Int {
        var count = 0
        let items = extensionContext?.inputItems as? [NSExtensionItem] ?? []
        for item in items {
            for provider in item.attachments ?? [] {
                if provider.hasItemConformingToTypeIdentifier(UTType.image.identifier) {
                    if let img = await loadImage(provider), ClipStore.shared.addImage(img) { count += 1 }
                } else if provider.hasItemConformingToTypeIdentifier(UTType.url.identifier) {
                    if let url = try? await provider.loadItem(forTypeIdentifier: UTType.url.identifier) as? URL,
                       ClipStore.shared.addText(url.absoluteString) { count += 1 }
                } else if provider.hasItemConformingToTypeIdentifier(UTType.plainText.identifier) {
                    if let text = try? await provider.loadItem(forTypeIdentifier: UTType.plainText.identifier) as? String,
                       ClipStore.shared.addText(text) { count += 1 }
                }
            }
        }
        return count
    }

    private func loadImage(_ provider: NSItemProvider) async -> UIImage? {
        guard let item = try? await provider.loadItem(forTypeIdentifier: UTType.image.identifier) else { return nil }
        switch item {
        case let image as UIImage: return image
        case let url as URL: return UIImage(contentsOfFile: url.path)
        case let data as Data: return UIImage(data: data)
        default: return nil
        }
    }

    private func showConfirmation(saved: Bool) {
        let card = UIHostingController(rootView: SavedCard(saved: saved))
        card.view.backgroundColor = .clear
        card.view.translatesAutoresizingMaskIntoConstraints = false
        addChild(card)
        view.addSubview(card.view)
        NSLayoutConstraint.activate([
            card.view.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            card.view.centerYAnchor.constraint(equalTo: view.centerYAnchor),
        ])
        card.didMove(toParent: self)
        UINotificationFeedbackGenerator().notificationOccurred(saved ? .success : .warning)
    }
}

private struct SavedCard: View {
    let saved: Bool

    var body: some View {
        VStack(spacing: 10) {
            Image(systemName: saved ? "checkmark.circle.fill" : "exclamationmark.circle.fill")
                .font(.system(size: 44))
                .foregroundStyle(saved ? Color.green : Color.orange)
            Text(saved ? "Saved to Clipboard" : "Already saved")
                .font(.headline)
        }
        .padding(28)
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 24, style: .continuous))
    }
}
