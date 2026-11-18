import UIKit
import SwiftUI

/// Clipboard keyboard: shows your clips in any app. Tap a clip to type it in.
/// Needs "Allow Full Access" so it can read the shared clip storage.
final class KeyboardViewController: UIInputViewController {
    private var host: UIHostingController<KeyboardView>?

    override func viewDidLoad() {
        super.viewDidLoad()
        let root = makeView()
        let h = UIHostingController(rootView: root)
        h.view.backgroundColor = .clear
        h.view.translatesAutoresizingMaskIntoConstraints = false
        addChild(h)
        view.addSubview(h.view)
        NSLayoutConstraint.activate([
            h.view.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            h.view.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            h.view.topAnchor.constraint(equalTo: view.topAnchor),
            h.view.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            h.view.heightAnchor.constraint(equalToConstant: 280),
        ])
        h.didMove(toParent: self)
        host = h
    }

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        host?.rootView = makeView() // read the newest clips each time the keyboard shows
    }

    private func makeView() -> KeyboardView {
        KeyboardView(
            clips: ClipStore.loadSnapshot(),
            hasFullAccess: hasFullAccess,
            showGlobe: needsInputModeSwitchKey,
            insert: { [weak self] text in self?.textDocumentProxy.insertText(text) },
            deleteBackward: { [weak self] in self?.textDocumentProxy.deleteBackward() },
            nextKeyboard: { [weak self] in self?.advanceToNextInputMode() }
        )
    }
}

struct KeyboardView: View {
    let clips: [Clip]
    let hasFullAccess: Bool
    let showGlobe: Bool
    let insert: (String) -> Void
    let deleteBackward: () -> Void
    let nextKeyboard: () -> Void

    private var textClips: [Clip] { clips.filter { !$0.isImage } }

    var body: some View {
        VStack(spacing: 8) {
            HStack {
                Label("Clipboard", systemImage: "doc.on.clipboard")
                    .font(.subheadline.weight(.semibold))
                Spacer()
            }
            .padding(.horizontal, 14)
            .padding(.top, 10)

            if !hasFullAccess {
                message("Turn on Allow Full Access for Edge Clipboard in Settings \u{203A} General \u{203A} Keyboard \u{203A} Keyboards.")
            } else if textClips.isEmpty {
                message("No text clips yet. Copy something, then open Edge Clipboard.")
            } else {
                ScrollView {
                    LazyVStack(spacing: 6) {
                        ForEach(textClips) { clip in
                            Button { insert(clip.text ?? "") } label: {
                                HStack(spacing: 6) {
                                    if clip.pinned {
                                        Image(systemName: "pin.fill").font(.caption2).foregroundStyle(.orange)
                                    }
                                    Text(clip.text ?? "")
                                        .font(.system(size: 15))
                                        .lineLimit(2)
                                        .multilineTextAlignment(.leading)
                                        .frame(maxWidth: .infinity, alignment: .leading)
                                }
                                .padding(.horizontal, 12)
                                .padding(.vertical, 9)
                                .background(Color(.systemBackground), in: RoundedRectangle(cornerRadius: 10, style: .continuous))
                                .shadow(color: .black.opacity(0.08), radius: 0, y: 1)
                            }
                            .buttonStyle(.plain)
                        }
                    }
                    .padding(.horizontal, 8)
                }
            }

            HStack(spacing: 6) {
                if showGlobe { key(Image(systemName: "globe"), action: nextKeyboard) }
                key(Text("space"), wide: true) { insert(" ") }
                key(Image(systemName: "delete.left"), action: deleteBackward)
                key(Text("return")) { insert("\n") }
            }
            .padding(.horizontal, 6)
            .padding(.bottom, 6)
        }
    }

    private func message(_ text: String) -> some View {
        Text(text)
            .font(.footnote)
            .foregroundStyle(.secondary)
            .multilineTextAlignment(.center)
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .padding(.horizontal, 20)
    }

    private func key<L: View>(_ label: L, wide: Bool = false, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            label
                .font(.system(size: 16))
                .frame(minWidth: 44, maxWidth: wide ? .infinity : nil, minHeight: 42)
                .padding(.horizontal, wide ? 0 : 10)
                .background(Color(.systemBackground), in: RoundedRectangle(cornerRadius: 6, style: .continuous))
                .shadow(color: .black.opacity(0.15), radius: 0, y: 1)
        }
        .buttonStyle(.plain)
    }
}
