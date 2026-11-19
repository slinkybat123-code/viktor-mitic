package com.edgeclip

import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.os.Handler
import android.os.Looper
import android.text.Html
import android.util.LruCache
import android.view.HapticFeedbackConstants
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import java.io.File

/**
 * One UI style card: large preview, full-width "Copy" bar under it.
 * Tap the preview = open full clip. Touch and hold = show Pin / Delete.
 */
class ClipAdapter(
    private val look: Look,
    private val onOpen: (Clip) -> Unit,
    private val onCopy: (Clip) -> Unit,
    private val onPin: (Clip) -> Unit,
    private val onDelete: (Clip) -> Unit,
) : ListAdapter<Clip, ClipAdapter.VH>(DIFF) {

    private var expanded: String? = null

    class VH(v: View) : RecyclerView.ViewHolder(v) {
        val body: View = v.findViewById(R.id.clip_body)
        val text: TextView = v.findViewById(R.id.clip_text)
        val image: ImageView = v.findViewById(R.id.clip_image)
        val pinBadge: View = v.findViewById(R.id.clip_pin_badge)
        val actions: View = v.findViewById(R.id.clip_actions)
        val pin: TextView = v.findViewById(R.id.clip_pin)
        val del: TextView = v.findViewById(R.id.clip_delete)
        val copy: View = v.findViewById(R.id.clip_copy)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
        val v = LayoutInflater.from(parent.context).inflate(R.layout.item_clip, parent, false)
        Style.applyItem(v, look)
        return VH(v)
    }

    override fun onBindViewHolder(h: VH, position: Int) {
        val c = getItem(position)
        val ctx = h.itemView.context
        if (c.isImage) {
            h.text.visibility = View.GONE
            h.image.visibility = View.VISIBLE
            h.image.tag = c.key
            h.image.setImageDrawable(null)
            loadThumb(ClipStore.imageFile(c), c.key) { bmp -> if (h.image.tag == c.key) h.image.setImageBitmap(bmp) }
            h.body.contentDescription = ctx.getString(R.string.image_clip)
        } else {
            h.image.visibility = View.GONE
            h.text.visibility = View.VISIBLE
            h.text.text = styled(c, 400, look.sourceColors) // preview only; full text opens on tap
            h.body.contentDescription = null
        }
        h.pinBadge.visibility = if (c.pinned) View.VISIBLE else View.GONE
        h.pin.setText(if (c.pinned) R.string.unpin else R.string.pin)
        h.actions.visibility = if (expanded == c.key) View.VISIBLE else View.GONE

        h.body.setOnClickListener { onOpen(c) }
        h.body.setOnLongClickListener {
            it.performHapticFeedback(HapticFeedbackConstants.LONG_PRESS)
            val old = expanded
            expanded = if (old == c.key) null else c.key
            currentList.indexOfFirst { x -> x.key == old }.takeIf { i -> i >= 0 }?.let { i -> notifyItemChanged(i) }
            notifyItemChanged(h.bindingAdapterPosition)
            true
        }
        h.copy.setOnClickListener { onCopy(c) }
        h.pin.setOnClickListener { expanded = null; onPin(c) }
        h.del.setOnClickListener { expanded = null; onDelete(c) }
    }

    companion object {
        val DIFF = object : DiffUtil.ItemCallback<Clip>() {
            override fun areItemsTheSame(a: Clip, b: Clip) = a.key == b.key
            override fun areContentsTheSame(a: Clip, b: Clip) = a == b
        }

        /** Text with the source app's colours when available. */
        fun styled(c: Clip, maxChars: Int, colors: Boolean = true): CharSequence {
            val t = c.text ?: return ""
            val html = c.html
            if (colors && html != null && html.length < 60_000) {
                runCatching {
                    val sp = Html.fromHtml(html, Html.FROM_HTML_MODE_COMPACT)
                    var end = sp.length
                    while (end > 0 && sp[end - 1].isWhitespace()) end--
                    return sp.subSequence(0, minOf(end, maxChars))
                }
            }
            return if (t.length > maxChars) t.substring(0, maxChars) else t
        }

        private val cache = object : LruCache<String, Bitmap>(16 * 1024 * 1024) {
            override fun sizeOf(key: String, value: Bitmap) = value.byteCount
        }
        private val main = Handler(Looper.getMainLooper())

        /** Decodes a down-scaled bitmap off the main thread. */
        fun loadThumb(f: File, key: String, maxPx: Int = 480, done: (Bitmap) -> Unit) {
            val ck = "$key@$maxPx"
            cache.get(ck)?.let { done(it); return }
            ClipStore.io.execute {
                val bmp = decode(f, maxPx) ?: return@execute
                cache.put(ck, bmp)
                main.post { done(bmp) }
            }
        }

        fun decode(f: File, maxPx: Int): Bitmap? = runCatching {
            val o = BitmapFactory.Options().apply { inJustDecodeBounds = true }
            BitmapFactory.decodeFile(f.path, o)
            var s = 1
            while (o.outWidth / (s * 2) >= maxPx || o.outHeight / (s * 2) >= maxPx * 2) s *= 2
            BitmapFactory.decodeFile(f.path, BitmapFactory.Options().apply { inSampleSize = s })
        }.getOrNull()
    }
}
