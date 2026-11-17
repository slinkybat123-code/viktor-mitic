package com.edgeclip

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject
import java.io.File

data class Clip(val text: String, val time: Long, val pinned: Boolean)

/** Clipboard history saved to app storage. Keeps max [MAX] clips; oldest unpinned clips are deleted first. */
object ClipStore {
    const val MAX = 30

    private val clips = mutableListOf<Clip>() // newest first
    private val listeners = mutableSetOf<() -> Unit>()
    private var file: File? = null

    fun init(ctx: Context) {
        if (file != null) return
        val f = File(ctx.applicationContext.filesDir, "clips.json")
        file = f
        runCatching {
            if (f.exists()) {
                val arr = JSONArray(f.readText())
                for (i in 0 until arr.length()) {
                    val o = arr.getJSONObject(i)
                    clips += Clip(o.getString("t"), o.getLong("at"), o.optBoolean("p"))
                }
            }
        }
    }

    fun all(): List<Clip> =
        clips.sortedWith(compareByDescending<Clip> { it.pinned }.thenByDescending { it.time })

    fun add(raw: String) {
        val text = raw.trim()
        if (text.isEmpty()) return
        if (clips.maxByOrNull { it.time }?.text == text) return // same as latest clip
        val old = clips.firstOrNull { it.text == text }
        clips.removeAll { it.text == text }
        clips.add(0, Clip(text, System.currentTimeMillis(), old?.pinned ?: false))
        trim()
        commit()
    }

    fun togglePin(clip: Clip) = replace(clip) { it.copy(pinned = !it.pinned) }

    fun delete(clip: Clip) {
        clips.removeAll { it.text == clip.text }
        commit()
    }

    fun clearUnpinned() {
        clips.removeAll { !it.pinned }
        commit()
    }

    fun addListener(l: () -> Unit) { listeners += l }
    fun removeListener(l: () -> Unit) { listeners -= l }

    private fun replace(clip: Clip, f: (Clip) -> Clip) {
        val i = clips.indexOfFirst { it.text == clip.text }
        if (i >= 0) { clips[i] = f(clips[i]); commit() }
    }

    private fun trim() {
        while (clips.size > MAX) {
            val oldest = clips.filter { !it.pinned }.minByOrNull { it.time } ?: clips.minBy { it.time }
            clips.remove(oldest)
        }
    }

    private fun commit() {
        val arr = JSONArray()
        clips.forEach { arr.put(JSONObject().put("t", it.text).put("at", it.time).put("p", it.pinned)) }
        runCatching { file?.writeText(arr.toString()) }
        listeners.toList().forEach { it() }
    }
}
