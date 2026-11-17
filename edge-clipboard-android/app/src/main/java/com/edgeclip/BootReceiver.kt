package com.edgeclip

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent

/** Starts the handle after a phone restart or an app update. */
class BootReceiver : BroadcastReceiver() {
    private val actions = setOf(
        Intent.ACTION_BOOT_COMPLETED,
        Intent.ACTION_MY_PACKAGE_REPLACED,
        Intent.ACTION_USER_UNLOCKED,
        "android.intent.action.QUICKBOOT_POWERON", // fast boot on some OEM phones
    )

    override fun onReceive(c: Context, i: Intent) {
        if (i.action !in actions) return
        if (!Prefs.on(c, K.AUTOSTART)) return
        Autostart.scheduleWatchdog(c)
        Autostart.ensureRunning(c)
    }
}
