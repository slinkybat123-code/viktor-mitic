package com.edgeclip

import android.app.job.JobInfo
import android.app.job.JobParameters
import android.app.job.JobScheduler
import android.app.job.JobService
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.provider.Settings

/** Keeps the handle running: after a phone restart, an app update, or if the system stops the app. */
object Autostart {
    private const val JOB_ID = 4711

    /** Starts the handle if the user turned it on and the overlay permission is granted. */
    fun ensureRunning(c: Context) {
        if (!Prefs.enabled(c) || !Settings.canDrawOverlays(c) || EdgeService.running) return
        // Apps with "Display over other apps" may start a foreground service from the background.
        runCatching { EdgeService.start(c) }
    }

    /** A persisted job (survives restarts) checks every 15 minutes that the handle still runs. */
    fun scheduleWatchdog(c: Context) {
        val js = c.getSystemService(JobScheduler::class.java)
        if (js.getPendingJob(JOB_ID) != null) return
        js.schedule(
            JobInfo.Builder(JOB_ID, ComponentName(c, WatchdogJob::class.java))
                .setPeriodic(15 * 60 * 1000L)
                .setPersisted(true)
                .build()
        )
    }

    fun cancelWatchdog(c: Context) = c.getSystemService(JobScheduler::class.java).cancel(JOB_ID)

    /** Opens the ColorOS / OxygenOS auto-launch list, or the app details page as a fallback. */
    fun openAutoLaunchSettings(c: Context) {
        val pages = listOf(
            "com.coloros.safecenter" to "com.coloros.safecenter.startupapp.StartupAppListActivity",
            "com.coloros.safecenter" to "com.coloros.safecenter.permission.startup.StartupAppListActivity",
            "com.oplus.safecenter" to "com.oplus.safecenter.startupapp.StartupAppListActivity",
            "com.oplus.safecenter" to "com.oplus.safecenter.permission.startup.StartupAppListActivity",
            "com.oppo.safe" to "com.oppo.safe.permission.startup.StartupAppListActivity",
        )
        for ((pkg, cls) in pages) {
            val ok = runCatching {
                c.startActivity(Intent().setComponent(ComponentName(pkg, cls)).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
            }.isSuccess
            if (ok) return
        }
        c.startActivity(
            Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS, Uri.parse("package:${c.packageName}"))
                .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        )
    }
}

class WatchdogJob : JobService() {
    override fun onStartJob(params: JobParameters?): Boolean {
        Autostart.ensureRunning(this)
        return false
    }

    override fun onStopJob(params: JobParameters?) = true
}
