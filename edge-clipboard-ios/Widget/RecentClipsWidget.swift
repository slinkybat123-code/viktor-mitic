import WidgetKit
import SwiftUI
import AppIntents

struct ClipsEntry: TimelineEntry {
    let date: Date
    let clips: [Clip]
}

struct ClipsProvider: TimelineProvider {
    func placeholder(in context: Context) -> ClipsEntry { ClipsEntry(date: .now, clips: [Clip.sample]) }

    func getSnapshot(in context: Context, completion: @escaping (ClipsEntry) -> Void) {
        completion(ClipsEntry(date: .now, clips: ClipStore.loadSnapshot()))
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<ClipsEntry>) -> Void) {
        // The app and extensions reload the widget when clips change.
        completion(Timeline(entries: [ClipsEntry(date: .now, clips: ClipStore.loadSnapshot())], policy: .never))
    }
}

struct RecentClipsView: View {
    @Environment(\.widgetFamily) private var family
    let entry: ClipsEntry

    private var count: Int {
        switch family {
        case .systemSmall: return 2
        case .systemMedium: return 3
        default: return 7
        }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(spacing: 6) {
                Image(systemName: "doc.on.clipboard.fill").foregroundStyle(.tint)
                Text("Clipboard").font(.subheadline.weight(.semibold))
                Spacer()
            }
            if entry.clips.isEmpty {
                Spacer()
                Text("No clips yet").font(.footnote).foregroundStyle(.secondary)
                Spacer()
            } else {
                ForEach(entry.clips.prefix(count)) { clip in
                    Button(intent: CopyClipIntent(clipID: clip.id.uuidString)) {
                        HStack(spacing: 6) {
                            if clip.isImage { Image(systemName: "photo").font(.caption) }
                            Text(clip.text ?? "Image")
                                .font(.footnote)
                                .lineLimit(1)
                            Spacer(minLength: 0)
                            Image(systemName: "doc.on.doc").font(.caption2).foregroundStyle(.secondary)
                        }
                        .padding(.horizontal, 10)
                        .padding(.vertical, 7)
                        .background(.fill.tertiary, in: RoundedRectangle(cornerRadius: 10, style: .continuous))
                    }
                    .buttonStyle(.plain)
                }
                Spacer(minLength: 0)
            }
        }
        .containerBackground(for: .widget) { Color(.systemBackground) }
    }
}

struct RecentClipsWidget: Widget {
    var body: some WidgetConfiguration {
        StaticConfiguration(kind: "RecentClips", provider: ClipsProvider()) { entry in
            RecentClipsView(entry: entry)
        }
        .configurationDisplayName("Recent Clips")
        .description("Tap a clip to copy it.")
        .supportedFamilies([.systemSmall, .systemMedium, .systemLarge])
    }
}

@main
struct EdgeClipboardWidgets: WidgetBundle {
    var body: some Widget {
        RecentClipsWidget()
    }
}
