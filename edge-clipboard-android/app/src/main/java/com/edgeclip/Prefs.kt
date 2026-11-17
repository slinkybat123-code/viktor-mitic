package com.edgeclip

import android.content.Context

/** Every adjustable setting, with its storage key and default value. */
enum class K(val key: String, val def: Int) {
    // Handle
    H_WIDTH("w", 7), H_HEIGHT("h", 72), H_ALPHA("a", 65), H_GAP("gap", 0), H_COLOR("hcol", 0),
    TAP_OPEN("tap", 0), SWIPE_DIST("swipe", 20), HOLD_MS("hold", 450), LOCK_POS("lock", 0), HAPTICS("hap", 1),
    // Panel
    THEME("theme", 0), P_WIDTH("pw", 184), P_ALPHA("pa", 72), BLUR("blur", 28), DIM("dim", 20),
    P_RADIUS("pr", 28), P_TOP("ptop", 36), ANIM("anim", 100),
    // Cards
    TEXT_SP("tsp", 15), LINES("lines", 3), C_ALPHA("ca", 70), C_RADIUS("cr", 16), C_GAP("cg", 4),
    C_PAD("cp", 10), COPY_H("ch", 38), COPY_SP("csp", 14), SHOW_COPY("showcopy", 1),
    SOURCE_COLORS("srccol", 1), CLOSE_AFTER_COPY("close", 1),
    // Storage
    MAX_CLIPS("max", 30), UNLIMITED("unl", 0), AUTO_DELETE("autodel", 0), SAVE_IMAGES("img", 1),
}

object Prefs {
    private fun sp(c: Context) = c.getSharedPreferences("edge", Context.MODE_PRIVATE)

    fun get(c: Context, k: K) = sp(c).getInt(k.key, k.def)
    fun set(c: Context, k: K, v: Int) = sp(c).edit().putInt(k.key, v).apply()
    fun on(c: Context, k: K) = get(c, k) != 0

    fun enabled(c: Context) = sp(c).getBoolean("enabled", false)
    fun setEnabled(c: Context, v: Boolean) = sp(c).edit().putBoolean("enabled", v).apply()

    fun isRight(c: Context) = sp(c).getBoolean("right", true)
    fun setRight(c: Context, v: Boolean) = sp(c).edit().putBoolean("right", v).apply()

    fun y(c: Context) = sp(c).getInt("y", -1)
    fun setY(c: Context, v: Int) = sp(c).edit().putInt("y", v).apply()

    /** Folder (SAF tree URI) that receives a copy of all clips, or null for app storage only. */
    fun folder(c: Context): String? = sp(c).getString("folder", null)
    fun setFolder(c: Context, v: String?) = sp(c).edit().putString("folder", v).apply()

    /** Max clips; 0 = no limit. */
    fun maxClips(c: Context) = if (on(c, K.UNLIMITED)) 0 else get(c, K.MAX_CLIPS)

    /** Auto-delete age in ms for unpinned clips; 0 = never. */
    fun autoDeleteMs(c: Context): Long = when (get(c, K.AUTO_DELETE)) {
        1 -> 3_600_000L
        2 -> 86_400_000L
        3 -> 7 * 86_400_000L
        4 -> 30 * 86_400_000L
        else -> 0L
    }

    /** Resets the look and behaviour. Keeps on/off, handle position and folder. */
    fun resetAll(c: Context) {
        val e = sp(c).edit()
        K.entries.forEach { e.remove(it.key) }
        e.apply()
    }
}
