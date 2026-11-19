package com.edgeclip

import android.content.Context
import org.json.JSONObject

/**
 * Named snapshots of all settings (every K value, plus handle side and height).
 * Clips and the storage folder are not part of a profile.
 */
object Profiles {
    private const val KEY = "profiles"
    private fun sp(c: Context) = c.getSharedPreferences("profiles", Context.MODE_PRIVATE)

    private fun all(c: Context): JSONObject =
        runCatching { JSONObject(sp(c).getString(KEY, "{}") ?: "{}") }.getOrDefault(JSONObject())

    private fun write(c: Context, o: JSONObject) = sp(c).edit().putString(KEY, o.toString()).apply()

    fun names(c: Context): List<String> = all(c).keys().asSequence().toList().sortedBy { it.lowercase() }

    /** The current settings as JSON. */
    fun snapshot(c: Context): JSONObject {
        val o = JSONObject()
        K.entries.forEach { o.put(it.key, Prefs.get(c, it)) }
        o.put("_right", Prefs.isRight(c))
        o.put("_y", Prefs.y(c))
        return o
    }

    fun save(c: Context, name: String) {
        val o = all(c)
        o.put(name, snapshot(c))
        write(c, o)
    }

    /** Applies a profile. Values missing from an older profile keep their current value. */
    fun apply(c: Context, name: String): Boolean {
        val p = all(c).optJSONObject(name) ?: return false
        K.entries.forEach { k -> if (p.has(k.key)) Prefs.set(c, k, p.optInt(k.key, k.def)) }
        if (p.has("_right")) Prefs.setRight(c, p.optBoolean("_right", true))
        if (p.has("_y")) Prefs.setY(c, p.optInt("_y", -1))
        return true
    }

    fun delete(c: Context, name: String) {
        val o = all(c)
        o.remove(name)
        write(c, o)
    }

    fun rename(c: Context, from: String, to: String) {
        val o = all(c)
        val p = o.optJSONObject(from) ?: return
        o.remove(from)
        o.put(to, p)
        write(c, o)
    }

    fun exists(c: Context, name: String) = all(c).has(name)

    /** File format for export / import. */
    fun exportJson(c: Context): String =
        JSONObject().put("app", "edge-clipboard").put("version", 1).put("profiles", all(c)).toString(2)

    /** Adds the profiles from a file. Returns how many were imported. Same names are replaced. */
    fun importJson(c: Context, text: String): Int {
        val src = JSONObject(text).optJSONObject("profiles") ?: return 0
        val o = all(c)
        var n = 0
        src.keys().forEach { name -> src.optJSONObject(name)?.let { o.put(name, it); n++ } }
        write(c, o)
        return n
    }
}
