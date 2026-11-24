package com.edgeclip

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.content.res.Configuration
import android.os.Build
import android.os.IBinder
import android.provider.Settings
import android.view.WindowManager

/**
 * Fallback host for the handle when Copy detection (accessibility) is off.
 * Android requires a notification for this kind of service.
 */
class EdgeService : Service() {

    companion object {
        private const val CHANNEL = "edge"
        private const val NOTIF_ID = 1

        fun start(ctx: Context, action: String? = null) {
            ctx.startForegroundService(Intent(ctx, EdgeService::class.java).setAction(action))
        }

        fun stop(ctx: Context) {
            ctx.stopService(Intent(ctx, EdgeService::class.java))
        }
    }

    private var controller: EdgeController? = null

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        try {
            goForeground()
        } catch (t: Throwable) {
            // Android can refuse a foreground start from the background. Do not crash: stop quietly.
            CrashLog.caught(this, "EdgeService.goForeground", t)
            stopSelf()
            return
        }
        // The accessibility host has priority: it needs no notification.
        if (CopyWatchService.instance != null || !Settings.canDrawOverlays(this)) { stopSelf(); return }
        if (Prefs.on(this, K.AUTOSTART)) Autostart.scheduleWatchdog(this)
        val ctl = EdgeController(this, WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY)
        try {
            ctl.start(); controller = ctl
        } catch (t: Throwable) {
            CrashLog.caught(this, "EdgeService.start", t)
            runCatching { ctl.destroy() }
            stopSelf()
        }
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        runCatching { goForeground() }
        if (intent?.action == Edge.ACTION_STOP) {
            Prefs.setEnabled(this, false); Autostart.cancelWatchdog(this); stopSelf()
        } else controller?.command(intent?.action)
        return START_STICKY
    }

    override fun onConfigurationChanged(newConfig: Configuration) {
        super.onConfigurationChanged(newConfig)
        controller?.onConfigChanged()
    }

    override fun onDestroy() {
        controller?.destroy()
        controller = null
        super.onDestroy()
    }

    private fun goForeground() {
        val nm = getSystemService(NotificationManager::class.java)
        if (nm.getNotificationChannel(CHANNEL) == null) {
            nm.createNotificationChannel(
                NotificationChannel(CHANNEL, getString(R.string.notif_channel), NotificationManager.IMPORTANCE_MIN)
            )
        }
        val flags = PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        val open = PendingIntent.getForegroundService(
            this, 1, Intent(this, EdgeService::class.java).setAction(Edge.ACTION_OPEN), flags
        )
        val stop = PendingIntent.getForegroundService(
            this, 2, Intent(this, EdgeService::class.java).setAction(Edge.ACTION_STOP), flags
        )
        val n = Notification.Builder(this, CHANNEL)
            .setSmallIcon(R.drawable.ic_clip)
            .setContentTitle(getString(R.string.notif_title))
            .setContentText(getString(R.string.notif_text))
            .setContentIntent(open)
            .setOngoing(true)
            .addAction(Notification.Action.Builder(null, getString(R.string.stop), stop).build())
            .build()
        if (Build.VERSION.SDK_INT >= 34) {
            startForeground(NOTIF_ID, n, ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE)
        } else {
            startForeground(NOTIF_ID, n)
        }
    }
}
