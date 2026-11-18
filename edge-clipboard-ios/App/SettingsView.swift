import SwiftUI

struct SettingsView: View {
    @EnvironmentObject private var store: ClipStore
    @Environment(\.dismiss) private var dismiss

    @AppStorage(Settings.textSizeKey, store: AppGroup.defaults) private var textSize = 16.0
    @AppStorage(Settings.linesKey, store: AppGroup.defaults) private var lines = 3
    @AppStorage(Settings.maxKey, store: AppGroup.defaults) private var maxClips = 30
    @AppStorage(Settings.unlimitedKey, store: AppGroup.defaults) private var unlimited = false
    @AppStorage(Settings.autoDeleteKey, store: AppGroup.defaults) private var autoDelete = 0
    @AppStorage(Settings.saveOnOpenKey, store: AppGroup.defaults) private var saveOnOpen = true

    @State private var confirmDelete = false

    var body: some View {
        NavigationStack {
            Form {
                Section {
                    VStack(alignment: .leading) {
                        LabeledContent("Text Size", value: "\(Int(textSize)) pt")
                        Slider(value: $textSize, in: 11...28, step: 1)
                    }
                    Stepper("Preview Lines: \(lines)", value: $lines, in: 1...10)
                    Text("The quick brown fox jumps over the lazy dog. Your clips look like this.")
                        .font(.system(size: textSize))
                        .lineLimit(lines)
                        .foregroundStyle(.secondary)
                } header: { Text("Appearance") }

                Section {
                    Toggle("Save Clipboard When App Opens", isOn: $saveOnOpen)
                    Toggle("No Clip Limit", isOn: $unlimited)
                    if !unlimited {
                        Stepper("Maximum Clips: \(maxClips)", value: $maxClips, in: 5...500, step: 5)
                    }
                    Picker("Delete Unpinned After", selection: $autoDelete) {
                        Text("Never").tag(0)
                        Text("1 Hour").tag(1)
                        Text("1 Day").tag(2)
                        Text("7 Days").tag(3)
                        Text("30 Days").tag(4)
                    }
                } header: { Text("Saving") } footer: {
                    Text("To stop the \u{201C}Allow Paste\u{201D} question, open Settings \u{203A} Apps \u{203A} Edge Clipboard \u{203A} Paste from Other Apps \u{203A} Allow.")
                }

                Section {
                    HowTo(icon: "keyboard", title: "Clipboard Keyboard",
                          text: "Settings \u{203A} General \u{203A} Keyboard \u{203A} Keyboards \u{203A} Add New Keyboard \u{203A} Edge Clipboard. Turn on Allow Full Access so the keyboard can read your clips. In any app, hold the globe key and select Edge Clipboard.")
                    HowTo(icon: "square.grid.2x2", title: "Home Screen Widget",
                          text: "Touch and hold the Home Screen, tap Edit \u{203A} Add Widget, and search for Edge Clipboard. Tap a clip in the widget to copy it.")
                    HowTo(icon: "square.and.arrow.up", title: "Share Sheet",
                          text: "In any app, tap Share and select Edge Clipboard to save text, links or images.")
                    HowTo(icon: "hand.tap", title: "Back Tap",
                          text: "Settings \u{203A} Accessibility \u{203A} Touch \u{203A} Back Tap \u{203A} Double Tap \u{203A} Save Clipboard. Then tap the back of the iPhone twice after you copy something.")
                } header: { Text("Use Everywhere") }

                Section {
                    Button("Delete All Clips", role: .destructive) { confirmDelete = true }
                } footer: {
                    Text("Clips stay on this iPhone. Edge Clipboard has no account and sends no data.")
                }

                Section {
                    LabeledContent("Version", value: Bundle.main.object(forInfoDictionaryKey: "CFBundleShortVersionString") as? String ?? "")
                }
            }
            .navigationTitle("Settings")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) { Button("Done") { dismiss() } }
            }
            .confirmationDialog("Delete all clips?", isPresented: $confirmDelete, titleVisibility: .visible) {
                Button("Delete All \(store.clips.count) Clips", role: .destructive) { store.clearAll() }
            } message: {
                Text("This also deletes pinned clips. You cannot undo this.")
            }
            .onChange(of: maxClips) { _, _ in store.prune() }
            .onChange(of: unlimited) { _, _ in store.prune() }
            .onChange(of: autoDelete) { _, _ in store.prune() }
        }
    }
}

private struct HowTo: View {
    let icon: String
    let title: String
    let text: String

    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            Image(systemName: icon)
                .font(.body.weight(.semibold))
                .foregroundStyle(.white)
                .frame(width: 30, height: 30)
                .background(Color.accentColor, in: RoundedRectangle(cornerRadius: 7, style: .continuous))
            VStack(alignment: .leading, spacing: 2) {
                Text(title).font(.body.weight(.semibold))
                Text(text).font(.footnote).foregroundStyle(.secondary)
            }
        }
        .padding(.vertical, 2)
    }
}
