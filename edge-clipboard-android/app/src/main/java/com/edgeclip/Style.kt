package com.edgeclip

import android.content.Context
import android.content.res.ColorStateList
import android.content.res.Configuration
import android.graphics.Color
import android.graphics.drawable.GradientDrawable
import android.graphics.drawable.RippleDrawable
import android.util.TypedValue
import android.view.View
import android.view.ViewGroup
import android.widget.TextView

/** Snapshot of the card look, read from Prefs once per panel open. */
data class Look(
    val textSp: Int, val lines: Int, val cardAlpha: Int, val radius: Int, val gap: Int, val pad: Int,
    val copyH: Int, val copySp: Int, val showCopy: Boolean, val sourceColors: Boolean,
) {
    companion object {
        fun from(c: Context) = Look(
            Prefs.get(c, K.TEXT_SP), Prefs.get(c, K.LINES), Prefs.get(c, K.C_ALPHA), Prefs.get(c, K.C_RADIUS),
            Prefs.get(c, K.C_GAP), Prefs.get(c, K.C_PAD), Prefs.get(c, K.COPY_H), Prefs.get(c, K.COPY_SP),
            Prefs.on(c, K.SHOW_COPY), Prefs.on(c, K.SOURCE_COLORS),
        )
    }
}

object Style {
    val HANDLE_COLORS = intArrayOf(0, 0xFFFFFFFF.toInt(), 0xFF111111.toInt(), 0xFF3E91FF.toInt(),
        0xFFFF6B6B.toInt(), 0xFF4CC26B.toInt(), 0xFFB388FF.toInt(), 0xFFFFC94D.toInt())

    fun dp(c: Context, v: Number) = v.toFloat() * c.resources.displayMetrics.density

    fun alpha(color: Int, pct: Int) = (color and 0x00FFFFFF) or ((255 * pct.coerceIn(0, 100) / 100) shl 24)

    /** Context with the theme the user chose: 0 = system, 1 = light, 2 = dark. */
    fun themed(c: Context): Context {
        val mode = Prefs.get(c, K.THEME)
        val base = if (mode == 0) c else {
            val cfg = Configuration(c.resources.configuration)
            cfg.uiMode = (cfg.uiMode and Configuration.UI_MODE_NIGHT_MASK.inv()) or
                if (mode == 2) Configuration.UI_MODE_NIGHT_YES else Configuration.UI_MODE_NIGHT_NO
            c.createConfigurationContext(cfg)
        }
        return android.view.ContextThemeWrapper(base, R.style.Theme_EdgeClip)
    }

    fun handleColor(c: Context): Int {
        val i = Prefs.get(c, K.H_COLOR).coerceIn(0, HANDLE_COLORS.size - 1)
        return if (i == 0) c.getColor(R.color.handle) else HANDLE_COLORS[i]
    }

    fun panelBackground(c: Context, right: Boolean): GradientDrawable {
        val r = dp(c, Prefs.get(c, K.P_RADIUS))
        return GradientDrawable().apply {
            setColor(alpha(c.getColor(R.color.panel), Prefs.get(c, K.P_ALPHA)))
            cornerRadii = if (right) floatArrayOf(r, r, 0f, 0f, 0f, 0f, r, r) else floatArrayOf(0f, 0f, r, r, r, r, 0f, 0f)
        }
    }

    private fun radii(r: Float, top: Boolean, bottom: Boolean): FloatArray {
        val t = if (top) r else 0f
        val b = if (bottom) r else 0f
        return floatArrayOf(t, t, t, t, b, b, b, b)
    }

    private fun rounded(color: Int, radii: FloatArray) = GradientDrawable().apply { setColor(color); cornerRadii = radii }

    private fun ripple(c: Context, color: Int, radii: FloatArray) =
        RippleDrawable(ColorStateList.valueOf(0x33888888), rounded(color, radii), rounded(Color.WHITE, radii))

    /** Applies the Look to one inflated item_clip view. */
    fun applyItem(v: View, look: Look) {
        val c = v.context
        val r = dp(c, look.radius)
        val card = alpha(c.getColor(R.color.card), look.cardAlpha)
        val bar = alpha(c.getColor(R.color.copy_bar), (look.cardAlpha + 15).coerceAtMost(100))
        (v.layoutParams as? ViewGroup.MarginLayoutParams)?.bottomMargin = dp(c, look.gap).toInt()

        val body = v.findViewById<View>(R.id.clip_body)
        val bodyRadii = radii(r, true, !look.showCopy)
        body.background = rounded(card, bodyRadii)
        body.foreground = RippleDrawable(ColorStateList.valueOf(0x22888888), null, rounded(Color.WHITE, bodyRadii))
        val p = dp(c, look.pad).toInt()
        body.setPadding(p, p, p, p)
        body.minimumHeight = 0

        v.findViewById<TextView>(R.id.clip_text).apply {
            setTextSize(TypedValue.COMPLEX_UNIT_SP, look.textSp.toFloat())
            maxLines = look.lines
        }
        v.findViewById<View>(R.id.clip_image).let {
            (it as android.widget.ImageView).maxHeight = dp(c, look.textSp * look.lines * 1.6f + 24).toInt()
        }
        v.findViewById<View>(R.id.clip_actions).setBackgroundColor(card)

        v.findViewById<TextView>(R.id.clip_copy).apply {
            visibility = if (look.showCopy) View.VISIBLE else View.GONE
            layoutParams.height = dp(c, look.copyH).toInt()
            setTextSize(TypedValue.COMPLEX_UNIT_SP, look.copySp.toFloat())
            background = ripple(c, bar, radii(r, false, true))
        }
    }
}
