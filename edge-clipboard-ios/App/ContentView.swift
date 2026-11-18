import SwiftUI

struct ContentView: View {
    @EnvironmentObject private var store: ClipStore
    @AppStorage(Settings.textSizeKey, store: AppGroup.defaults) private var textSize = 16.0
    @AppStorage(Settings.linesKey, store: AppGroup.defaults) private var lines = 3

    @State private var query = ""
    @State private var showSettings = false
    @State private var toast = false
    @State private var copiedCount = 0

    private var filtered: [Clip] {
        guard !query.isEmpty else { return store.clips }
        return store.clips.filter { ($0.text ?? "").localizedCaseInsensitiveContains(query) }
    }

    var body: some View {
        NavigationStack {
            Group {
                if store.clips.isEmpty {
                    ContentUnavailableView {
                        Label("No Clips Yet", systemImage: "doc.on.clipboard")
                    } description: {
                        Text("Copy something in any app, then come back, or tap Paste below.")
                    }
                } else {
                    list
                }
            }
            .navigationTitle("Clipboard")
            .searchable(text: $query, prompt: "Search clips")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button { showSettings = true } label: { Image(systemName: "gearshape") }
                        .accessibilityLabel("Settings")
                }
                ToolbarItem(placement: .bottomBar) {
                    PasteButton(payloadType: String.self) { strings in
                        Task { @MainActor in strings.forEach { store.addText($0) } }
                    }
                    .buttonBorderShape(.capsule)
                    .labelStyle(.titleAndIcon)
                }
            }
            .navigationDestination(for: Clip.self) { ClipDetailView(clip: $0) }
            .sheet(isPresented: $showSettings) { SettingsView() }
            .overlay(alignment: .bottom) { CopiedToast(visible: toast) }
            .sensoryFeedback(.success, trigger: copiedCount)
        }
    }

    private var list: some View {
        let pinned = filtered.filter(\.pinned)
        let recent = filtered.filter { !$0.pinned }
        return List {
            if !pinned.isEmpty {
                Section("Pinned") { rows(pinned) }
            }
            Section(pinned.isEmpty ? "" : "Recent") { rows(recent) }
        }
        .listStyle(.insetGrouped)
        .animation(.snappy, value: store.clips)
    }

    @ViewBuilder
    private func rows(_ clips: [Clip]) -> some View {
        ForEach(clips) { clip in
            NavigationLink(value: clip) {
                ClipRow(clip: clip, textSize: textSize, lines: lines) { copy(clip) }
            }
            .swipeActions(edge: .leading) {
                Button { store.togglePin(clip) } label: {
                    Label(clip.pinned ? "Unpin" : "Pin", systemImage: clip.pinned ? "pin.slash.fill" : "pin.fill")
                }
                .tint(.orange)
            }
            .swipeActions(edge: .trailing) {
                Button(role: .destructive) { store.delete(clip) } label: { Label("Delete", systemImage: "trash") }
            }
            .contextMenu {
                Button { copy(clip) } label: { Label("Copy", systemImage: "doc.on.doc") }
                Button { store.togglePin(clip) } label: {
                    Label(clip.pinned ? "Unpin" : "Pin", systemImage: clip.pinned ? "pin.slash" : "pin")
                }
                if let text = clip.text { ShareLink(item: text) }
                Divider()
                Button(role: .destructive) { store.delete(clip) } label: { Label("Delete", systemImage: "trash") }
            }
        }
    }

    private func copy(_ clip: Clip) {
        Clipboard.copy(clip)
        copiedCount += 1
        withAnimation(.spring(duration: 0.3)) { toast = true }
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.2) {
            withAnimation(.easeOut(duration: 0.25)) { toast = false }
        }
    }
}

struct ClipRow: View {
    let clip: Clip
    let textSize: Double
    let lines: Int
    let onCopy: () -> Void

    var body: some View {
        HStack(alignment: .center, spacing: 12) {
            VStack(alignment: .leading, spacing: 6) {
                if clip.isImage, let img = ClipStore.shared.image(for: clip) {
                    Image(uiImage: img)
                        .resizable()
                        .scaledToFill()
                        .frame(maxWidth: .infinity, maxHeight: 120)
                        .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
                } else {
                    Text(clip.text ?? "")
                        .font(.system(size: textSize))
                        .lineLimit(lines)
                }
                HStack(spacing: 4) {
                    if clip.pinned { Image(systemName: "pin.fill").foregroundStyle(.orange) }
                    Text(clip.date, format: .relative(presentation: .named))
                }
                .font(.caption)
                .foregroundStyle(.secondary)
            }
            Spacer(minLength: 0)
            Button(action: onCopy) {
                Text("Copy")
                    .font(.subheadline.weight(.semibold))
                    .padding(.horizontal, 14)
                    .padding(.vertical, 6)
                    .background(Color.accentColor.opacity(0.15), in: Capsule())
            }
            .buttonStyle(.borderless)
            .accessibilityLabel("Copy clip")
        }
        .padding(.vertical, 4)
    }
}

struct CopiedToast: View {
    let visible: Bool

    var body: some View {
        if visible {
            Label("Copied", systemImage: "checkmark.circle.fill")
                .font(.subheadline.weight(.semibold))
                .padding(.horizontal, 18)
                .padding(.vertical, 10)
                .background(.ultraThinMaterial, in: Capsule())
                .shadow(color: .black.opacity(0.12), radius: 12, y: 4)
                .padding(.bottom, 70)
                .transition(.move(edge: .bottom).combined(with: .opacity))
        }
    }
}
