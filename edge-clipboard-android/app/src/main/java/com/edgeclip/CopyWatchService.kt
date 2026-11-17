package com.edgeclip

import android.accessibilityservice.AccessibilityService
import android.os.Handler
import android.os.Looper
import android.view.accessibility.AccessibilityEvent

/**
 * Android 10+ blocks clipboard reads from background apps. This service only watches for
 * "copy" actions (Copy button taps, "Copied" toasts, the system clipboard overlay) and then
 * asks EdgeService to read the clipboard through a short focus grab. It reads no screen content.
 */
class CopyWatchService : AccessibilityService() {
    private val ui = Handler(Looper.getMainLooper())
    private var last = 0L
    private val words = listOf("copy", "copied", "clipboard", "kopieren", "kopiert", "copiar", "copier", "copia", "复制")

    override fun onAccessibilityEvent(e: AccessibilityEvent) {
        if (e.packageName == packageName) return
        val text = (e.text.joinToString(" ") + " " + (e.contentDescription ?: "")).lowercase()
        val hit = when (e.eventType) {
            AccessibilityEvent.TYPE_VIEW_CLICKED -> words.any { text.contains(it) }
            AccessibilityEvent.TYPE_NOTIFICATION_STATE_CHANGED -> words.any { text.contains(it) }
            AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED ->
                e.packageName == "com.android.systemui" &&
                    (text.contains("clipboard") || e.className?.toString()?.contains("Clipboard", true) == true)
            else -> false
        }
        if (!hit) return
        val now = System.currentTimeMillis()
        if (now - last < 500) return
        last = now
        ui.postDelayed({
            if (Prefs.enabled(this)) EdgeService.start(this, EdgeService.ACTION_GRAB)
        }, 200)
    }

    override fun onInterrupt() {}
}
