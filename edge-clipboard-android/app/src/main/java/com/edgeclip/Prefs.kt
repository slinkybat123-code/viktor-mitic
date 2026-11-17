package com.edgeclip

import android.content.Context

object Prefs {
    private fun sp(c: Context) = c.getSharedPreferences("edge", Context.MODE_PRIVATE)

    fun enabled(c: Context) = sp(c).getBoolean("enabled", false)
    fun setEnabled(c: Context, v: Boolean) = sp(c).edit().putBoolean("enabled", v).apply()

    fun isRight(c: Context) = sp(c).getBoolean("right", true)
    fun setRight(c: Context, v: Boolean) = sp(c).edit().putBoolean("right", v).apply()

    fun y(c: Context) = sp(c).getInt("y", -1)
    fun setY(c: Context, v: Int) = sp(c).edit().putInt("y", v).apply()

    /** Handle size in dp. Default ≈ volume rocker of a large phone. */
    fun widthDp(c: Context) = sp(c).getInt("w", 7)
    fun setWidthDp(c: Context, v: Int) = sp(c).edit().putInt("w", v).apply()

    fun heightDp(c: Context) = sp(c).getInt("h", 72)
    fun setHeightDp(c: Context, v: Int) = sp(c).edit().putInt("h", v).apply()

    /** Opacity in percent. */
    fun alpha(c: Context) = sp(c).getInt("a", 65)
    fun setAlpha(c: Context, v: Int) = sp(c).edit().putInt("a", v).apply()
}
