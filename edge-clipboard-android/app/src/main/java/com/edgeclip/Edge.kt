package com.edgeclip

import android.content.Context
import android.provider.Settings

/** Chooses the host for the handle and sends commands to the running one. */
object Edge {
    const val ACTION_REFRESH = "com.edgeclip.REFRESH"
    const val ACTION_GRAB = "com.edgeclip.GRAB"
    const val ACTION_OPEN = "com.edgeclip.OPEN"
    const val ACTION_STOP = "com.edgeclip.STOP"

    /** The controller that shows the handle now, or null. */
    var active: EdgeController? = null

    val running get() = active != null

    /** Shows the handle. Uses the accessibility host (no notification) when Copy detection is on. */
    fun start(c: Context, action: String? = null) {
        val a11y = CopyWatchService.instance
        if (a11y != null) {
            EdgeService.stop(c)
            a11y.showHandle()
            active?.command(action)
        } else if (Settings.canDrawOverlays(c)) {
            val ctl = active
            if (ctl != null && action != null) ctl.command(action) else EdgeService.start(c, action)
        }
    }

    fun stop(c: Context) {
        CopyWatchService.instance?.hideHandle()
        EdgeService.stop(c)
    }

    fun command(c: Context, action: String) {
        val ctl = active
        if (ctl != null) ctl.command(action) else if (Prefs.enabled(c)) start(c, action)
    }
}
