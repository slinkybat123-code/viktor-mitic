package com.edgeclip

import android.app.Application
import java.io.File
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/** Saves the cause of a crash to files/last_error.txt, so the user can send it from Settings. */
class EdgeApp : Application() {
    override fun onCreate() {
        super.onCreate()
        val previous = Thread.getDefaultUncaughtExceptionHandler()
        Thread.setDefaultUncaughtExceptionHandler { thread, error ->
            runCatching { CrashLog.write(this, "Crash in thread ${thread.name}", error) }
            previous?.uncaughtException(thread, error)
        }
    }
}

object CrashLog {
    private fun file(c: android.content.Context) = File(c.filesDir, "last_error.txt")

    fun write(c: android.content.Context, title: String, error: Throwable) {
        val time = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.US).format(Date())
        val info = "Edge Clipboard ${runCatching { c.packageManager.getPackageInfo(c.packageName, 0).versionName }.getOrDefault("?")}" +
            " | Android ${android.os.Build.VERSION.RELEASE} (API ${android.os.Build.VERSION.SDK_INT})" +
            " | ${android.os.Build.MANUFACTURER} ${android.os.Build.MODEL}"
        file(c).writeText("$time\n$info\n$title\n\n${error.stackTraceToString()}")
    }

    /** For errors the app caught itself: saved, but the app keeps running. */
    fun caught(c: android.content.Context, where: String, error: Throwable) =
        runCatching { write(c, "Caught in $where", error) }

    fun read(c: android.content.Context): String? = file(c).takeIf { it.exists() }?.readText()

    fun clear(c: android.content.Context) { file(c).delete() }
}
