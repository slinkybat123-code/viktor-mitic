package com.edgeclip

import android.text.format.DateUtils
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageButton
import android.widget.TextView
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView

class ClipAdapter(
    private val onCopy: (Clip) -> Unit,
    private val onPin: (Clip) -> Unit,
    private val onDelete: (Clip) -> Unit,
) : ListAdapter<Clip, ClipAdapter.VH>(DIFF) {

    class VH(v: View) : RecyclerView.ViewHolder(v) {
        val text: TextView = v.findViewById(R.id.clip_text)
        val time: TextView = v.findViewById(R.id.clip_time)
        val pin: ImageButton = v.findViewById(R.id.clip_pin)
        val del: ImageButton = v.findViewById(R.id.clip_delete)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int) =
        VH(LayoutInflater.from(parent.context).inflate(R.layout.item_clip, parent, false))

    override fun onBindViewHolder(h: VH, position: Int) {
        val c = getItem(position)
        h.text.text = c.text
        h.time.text = DateUtils.getRelativeTimeSpanString(
            c.time, System.currentTimeMillis(), DateUtils.MINUTE_IN_MILLIS
        )
        h.pin.isSelected = c.pinned
        h.pin.alpha = if (c.pinned) 1f else 0.45f
        h.pin.contentDescription = h.itemView.context.getString(if (c.pinned) R.string.unpin else R.string.pin)
        h.itemView.isActivated = c.pinned
        h.itemView.setOnClickListener {
            it.animate().scaleX(0.96f).scaleY(0.96f).setDuration(80).withEndAction {
                it.animate().scaleX(1f).scaleY(1f).setDuration(140).start()
                onCopy(c)
            }.start()
        }
        h.pin.setOnClickListener { onPin(c) }
        h.del.setOnClickListener { onDelete(c) }
    }

    companion object {
        val DIFF = object : DiffUtil.ItemCallback<Clip>() {
            override fun areItemsTheSame(a: Clip, b: Clip) = a.text == b.text
            override fun areContentsTheSame(a: Clip, b: Clip) = a == b
        }
    }
}
