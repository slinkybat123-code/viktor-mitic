package com.edgeclip

import android.accessibilityservice.AccessibilityService
import android.content.Intent
import android.content.res.Configuration
import android.view.WindowManager
import android.os.Handler
import android.os.Looper
import android.view.accessibility.AccessibilityEvent

/**
 * Android 10+ blocks clipboard reads from background apps. This service only watches for
 * "copy" actions (Copy button taps, "Copied" toasts, the system clipboard overlay) and then
 * asks EdgeService to read the clipboard through a short focus grab. It reads no screen content.
 */
class CopyWatchService : AccessibilityService() {
    companion object {
        /** Set while the service is connected. */
        var instance: CopyWatchService? = null
            private set
    }

    private var controller: EdgeController? = null

    /** Shows the handle as an accessibility overlay: no notification, no "display over apps" needed. */
    fun showHandle() {
        if (controller != null) return
        EdgeService.stop(this) // the fallback host (with notification) is no longer needed
        val ctl = EdgeController(this, WindowManager.LayoutParams.TYPE_ACCESSIBILITY_OVERLAY)
        try {
            ctl.start()
            controller = ctl
        } catch (t: Throwable) {
            // Never let a window error stop the accessibility service ("malfunctioning").
            CrashLog.caught(this, "showHandle", t)
            runCatching { ctl.destroy() }
        }
    }

    fun hideHandle() {
        controller?.destroy()
        controller = null
    }

    override fun onConfigurationChanged(newConfig: Configuration) {
        super.onConfigurationChanged(newConfig)
        controller?.onConfigChanged()
    }

    override fun onUnbind(intent: Intent?): Boolean {
        teardown()
        return super.onUnbind(intent)
    }

    override fun onDestroy() {
        teardown()
        super.onDestroy()
    }

    /** Copy detection was turned off: move the handle to the fallback host. */
    private fun teardown() {
        if (instance !== this) return
        instance = null
        val had = controller != null
        hideHandle()
        if (had && Prefs.enabled(this)) Autostart.ensureRunning(this)
    }
    private val ui = Handler(Looper.getMainLooper())
    private var last = 0L
    private val words = listOf("copy", "copied", "clipboard", "kopieren", "kopiert", "copiar", "copier", "copia", "复制")

    override fun onAccessibilityEvent(e: AccessibilityEvent) {
        try { handleEvent(e) } catch (t: Throwable) { CrashLog.caught(this, "onAccessibilityEvent", t) }
    }

    private fun handleEvent(e: AccessibilityEvent) {
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
            if (Prefs.enabled(this)) Edge.command(this, Edge.ACTION_GRAB)
        }, 200)
    }

    /** The system restarts enabled accessibility services after a reboot: use that to start the handle too. */
    override fun onServiceConnected() {
        super.onServiceConnected()
        instance = this
        // Android starts this service after every reboot, so the handle comes back without auto launch.
        if (Prefs.enabled(this)) showHandle()
    }

    override fun onInterrupt() {}
}
