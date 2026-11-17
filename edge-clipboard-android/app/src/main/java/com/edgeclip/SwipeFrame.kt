package com.edgeclip

import android.annotation.SuppressLint
import android.content.Context
import android.util.AttributeSet
import android.view.MotionEvent
import android.view.VelocityTracker
import android.view.ViewConfiguration
import android.widget.FrameLayout
import kotlin.math.abs

/**
 * Panel root. Takes over a horizontal drag toward the screen edge so the user can push the
 * panel closed with a finger. Vertical scrolls and text selection stay with the children
 * (they call requestDisallowInterceptTouchEvent).
 */
class SwipeFrame @JvmOverloads constructor(ctx: Context, attrs: AttributeSet? = null) : FrameLayout(ctx, attrs) {
    /** +1 when the panel edge is on the right, -1 when it is on the left. */
    var edgeSign = 1f
    var onDragStart: (() -> Unit)? = null
    /** Distance moved toward the edge, in px (negative = back toward the centre). */
    var onDrag: ((Float) -> Unit)? = null
    /** Release speed toward the edge, in px/s. */
    var onDragEnd: ((Float) -> Unit)? = null

    private val slop = ViewConfiguration.get(ctx).scaledTouchSlop
    private var downX = 0f
    private var downY = 0f
    private var dragging = false
    private var vt: VelocityTracker? = null

    override fun onInterceptTouchEvent(e: MotionEvent): Boolean {
        when (e.actionMasked) {
            MotionEvent.ACTION_DOWN -> {
                downX = e.x; downY = e.y; dragging = false
                vt?.recycle(); vt = VelocityTracker.obtain().also { it.addMovement(e) }
            }
            MotionEvent.ACTION_MOVE -> {
                vt?.addMovement(e)
                val dx = (e.x - downX) * edgeSign
                val dy = e.y - downY
                if (dx > slop && dx > abs(dy) * 1.3f) {
                    dragging = true
                    downX = e.x
                    parent?.requestDisallowInterceptTouchEvent(true)
                    onDragStart?.invoke()
                    return true
                }
            }
            MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> if (!dragging) { vt?.recycle(); vt = null }
        }
        return false
    }

    @SuppressLint("ClickableViewAccessibility")
    override fun onTouchEvent(e: MotionEvent): Boolean {
        if (!dragging) return super.onTouchEvent(e)
        vt?.addMovement(e)
        when (e.actionMasked) {
            MotionEvent.ACTION_MOVE -> onDrag?.invoke((e.x - downX) * edgeSign)
            MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                vt?.computeCurrentVelocity(1000)
                onDragEnd?.invoke((vt?.xVelocity ?: 0f) * edgeSign)
                vt?.recycle(); vt = null
                dragging = false
            }
        }
        return true
    }
}
