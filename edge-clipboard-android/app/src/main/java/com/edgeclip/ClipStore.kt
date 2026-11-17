package com.edgeclip

import android.content.Context
import android.os.Handler
import android.os.Looper
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.security.MessageDigest
import java.util.concurrent.Executors

/** One clip: text OR image. [key] is a hash used to find duplicates. */
data class Clip(
    val id: Long,
    val key: String,
    val text: String?,
    val html: String?, // original formatting (colours), if the source app gave it
    val image: String?, // file name in files/images
    val time: Long,
    val pinned: Boolean,
) {
    val isImage get() = image != null
}

/**
 * Clipboard history saved to app storage. Max [MAX] clips; the oldest unpinned clip is
 * deleted first. Text length has no limit. Use from the main thread only.
 */
object ClipStore {
    const val MAX = 30

    private val clips = mutableListOf<Clip>()
    private val listeners = mutableSetOf<() -> Unit>()
    private var file: File? = null
    lateinit var imageDir: File
        private set
    val io = Executors.newSingleThreadExecutor()
    private val main = Handler(Looper.getMainLooper())

    fun init(ctx: Context) {
        if (file != null) return
        val dir = ctx.applicationContext.filesDir
        imageDir = File(dir, "images").apply { mkdirs() }
        val f = File(dir, "clips.json")
        file = f
        runCatching {
            if (f.exists()) {
                val arr = JSONArray(f.readText())
                for (i in 0 until arr.length()) {
                    val o = arr.getJSONObject(i)
                    val text = if (o.has("t")) o.getString("t") else null
                    val img = if (o.has("img")) o.getString("img") else null
                    if (text == null && img == null) continue
                    clips += Clip(
                        id = o.optLong("id", System.nanoTime() + i),
                        key = o.optString("k").ifEmpty { "t:" + sha1(text!!.toByteArray()) },
                        text = text, html = if (o.has("h")) o.getString("h") else null, image = img,
                        time = o.getLong("at"), pinned = o.optBoolean("p"),
                    )
                }
            }
        }
    }

    fun all(): List<Clip> =
        clips.sortedWith(compareByDescending<Clip> { it.pinned }.thenByDescending { it.time })

    fun imageFile(c: Clip) = File(imageDir, c.image!!)

    fun addText(raw: String, html: String? = null) {
        val text = raw.trim()
        if (text.isEmpty()) return
        insert(Clip(newId(), "t:" + sha1(text.toByteArray()), text, html, null, System.currentTimeMillis(), false))
    }

    /** Call from any thread. Saves the image file, then adds the clip on the main thread. */
    fun addImage(bytes: ByteArray, ext: String) {
        val key = "i:" + sha1(bytes)
        main.post {
            if (latest()?.key == key) return@post
            val existing = clips.firstOrNull { it.key == key }
            val name = existing?.image ?: "${newId()}.$ext"
            if (existing == null) runCatching { File(imageDir, name).writeBytes(bytes) }.onFailure { return@post }
            insert(Clip(newId(), key, null, null, name, System.currentTimeMillis(), false))
        }
    }

    fun togglePin(c: Clip) {
        val i = clips.indexOfFirst { it.key == c.key }
        if (i >= 0) { clips[i] = clips[i].copy(pinned = !clips[i].pinned); commit() }
    }

    fun delete(c: Clip) {
        clips.filter { it.key == c.key }.forEach { removeFiles(it) }
        clips.removeAll { it.key == c.key }
        commit()
    }

    fun clearUnpinned() {
        clips.filter { !it.pinned }.forEach { removeFiles(it) }
        clips.removeAll { !it.pinned }
        commit()
    }

    fun addListener(l: () -> Unit) { listeners += l }
    fun removeListener(l: () -> Unit) { listeners -= l }

    private fun latest() = clips.maxByOrNull { it.time }

    private fun insert(c: Clip) {
        if (latest()?.key == c.key) return // same as the latest clip
        val old = clips.firstOrNull { it.key == c.key }
        clips.removeAll { it.key == c.key }
        clips.add(0, c.copy(pinned = old?.pinned ?: false, image = old?.image ?: c.image))
        while (clips.size > MAX) {
            val oldest = clips.filter { !it.pinned }.minByOrNull { it.time } ?: clips.minBy { it.time }
            clips.remove(oldest)
            removeFiles(oldest)
        }
        commit()
    }

    private fun removeFiles(c: Clip) {
        if (c.image != null && clips.count { it.image == c.image } <= 1) File(imageDir, c.image).delete()
    }

    private var lastId = 0L
    private fun newId(): Long { lastId = maxOf(lastId + 1, System.currentTimeMillis()); return lastId }

    private fun commit() {
        val arr = JSONArray()
        clips.forEach {
            val o = JSONObject().put("id", it.id).put("k", it.key).put("at", it.time).put("p", it.pinned)
            if (it.text != null) o.put("t", it.text)
            if (it.html != null) o.put("h", it.html)
            if (it.image != null) o.put("img", it.image)
            arr.put(o)
        }
        val json = arr.toString()
        val f = file
        io.execute { runCatching { f?.writeText(json) } }
        listeners.toList().forEach { it() }
    }

    fun sha1(b: ByteArray): String =
        MessageDigest.getInstance("SHA-1").digest(b).joinToString("") { "%02x".format(it) }
}
