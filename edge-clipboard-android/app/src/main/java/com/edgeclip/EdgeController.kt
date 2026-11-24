package com.edgeclip

import android.annotation.SuppressLint
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.ContextWrapper
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.content.res.Configuration
import android.graphics.PixelFormat
import android.graphics.Point
import android.graphics.Rect
import android.net.Uri
import android.view.VelocityTracker
import android.widget.ImageView
import android.widget.ScrollView
import androidx.core.content.FileProvider
import java.io.File
import android.graphics.drawable.GradientDrawable
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.view.ContextThemeWrapper
import android.view.Gravity
import android.view.HapticFeedbackConstants
import android.view.KeyEvent
import android.view.LayoutInflater
import android.view.MotionEvent
import android.view.View
import android.view.ViewConfiguration
import android.view.ViewGroup
import android.view.WindowManager
import android.view.animation.AccelerateInterpolator
import android.view.animation.DecelerateInterpolator
import android.view.animation.OvershootInterpolator
import android.widget.FrameLayout
import android.widget.TextView
import android.widget.Toast
import androidx.dynamicanimation.animation.DynamicAnimation
import androidx.dynamicanimation.animation.FloatValueHolder
import androidx.dynamicanimation.animation.SpringAnimation
import androidx.dynamicanimation.animation.SpringForce
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import kotlin.math.abs
import kotlin.math.max

/**
 * The edge handle and the clipboard panel. Hosted by the Copy detection accessibility service
 * (TYPE_ACCESSIBILITY_OVERLAY: no notification, restarted by Android after a reboot) or, as a
 * fallback, by EdgeService (TYPE_APPLICATION_OVERLAY with a foreground notification).
 */
class EdgeController(base: Context, private val overlayType: Int) : ContextWrapper(base) {

    fun start() {
        wm = getSystemService(WINDOW_SERVICE) as WindowManager
        cm = getSystemService(CLIPBOARD_SERVICE) as ClipboardManager
        ClipStore.init(this)
        cm.addPrimaryClipChangedListener(clipListener)
        addHandle()
        Edge.active = this
    }

    fun command(action: String?) {
        when (action) {
            Edge.ACTION_REFRESH -> applyHandleLayout()
            Edge.ACTION_GRAB -> grabClipboard()
            Edge.ACTION_OPEN -> openPanel()
        }
    }

    fun onConfigChanged() {
        closePanel(animate = false)
        ui.post { applyHandleLayout() }
    }

    fun destroy() {
        if (Edge.active === this) Edge.active = null
        if (!::wm.isInitialized) return // start() did not run
        cm.removePrimaryClipChangedListener(clipListener)
        snapAnim?.cancel()
        closePanel(animate = false)
        listOfNotNull(pillRoot, handleRoot, grabView).forEach { runCatching { wm.removeView(it) } }
        pillRoot = null; handleRoot = null; grabView = null
    }

    private lateinit var wm: WindowManager
    private lateinit var cm: ClipboardManager
    private val ui = Handler(Looper.getMainLooper())

    private var handleRoot: FrameLayout? = null   // touch box window
    private var pillRoot: FrameLayout? = null     // visible pill window
    private lateinit var pill: View
    private lateinit var hp: WindowManager.LayoutParams
    private lateinit var vp: WindowManager.LayoutParams
    private var snapAnim: SpringAnimation? = null

    private var panel: View? = null
    private var panelListener: (() -> Unit)? = null
    private var grabView: View? = null

    private val clipListener = ClipboardManager.OnPrimaryClipChangedListener { readClipboard() }

    private fun dp(v: Float) = v * resources.displayMetrics.density

    // ---------- Edge handle ----------

    private fun screen(): Point =
        if (Build.VERSION.SDK_INT >= 30) {
            val b = wm.currentWindowMetrics.bounds
            Point(b.width(), b.height())
        } else {
            Point().also { @Suppress("DEPRECATION") wm.defaultDisplay.getRealSize(it) }
        }

    private fun overlayParams(flags: Int) = WindowManager.LayoutParams(
        0, 0, overlayType, flags or WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS, PixelFormat.TRANSLUCENT
    ).apply {
        gravity = Gravity.TOP or Gravity.START
        if (Build.VERSION.SDK_INT >= 30) {
            layoutInDisplayCutoutMode = WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_ALWAYS
        } else if (Build.VERSION.SDK_INT >= 28) {
            layoutInDisplayCutoutMode = WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES
        }
    }

    /**
     * Two windows: the visible pill (does not take touches) and the touch box (invisible,
     * any size and position). The touch box shows as a green box while Settings is open.
     */
    private fun addHandle() {
        pill = View(this)
        val vis = FrameLayout(this).apply {
            addView(pill)
            importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_NO
        }
        vp = overlayParams(WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE)
        val root = FrameLayout(this).apply {
            contentDescription = getString(R.string.handle_desc)
            isHapticFeedbackEnabled = true
        }
        hp = overlayParams(WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE)
        pillRoot = vis
        handleRoot = root
        applyHandleLayout(attach = false)
        root.setOnTouchListener(HandleTouch())
        root.addOnLayoutChangeListener { v, _, _, _, _, _, _, _, _ -> excludeSystemGesture(v) }
        wm.addView(vis, vp)
        wm.addView(root, hp)
        setTouchDebug(Edge.showTouchArea)
        vis.alpha = 0f
        vis.animate().alpha(1f).setDuration(300).start()
    }

    /** Shows (true) or hides (false) the touch box as a green box. The touch box works either way. */
    fun setTouchDebug(on: Boolean) {
        val root = handleRoot ?: return
        root.background = if (!on) null else GradientDrawable().apply {
            setColor(0x5534C759)
            setStroke(dp(2f).toInt(), 0xFF34C759.toInt())
            cornerRadius = dp(6f)
        }
    }

    /** Window positions for a side and a pill height (vy = top of the pill window). */
    private data class Spot(val vx: Int, val vy: Int, val hx: Int, val hy: Int)

    private fun spot(right: Boolean, visY: Int): Spot {
        val s = screen()
        val vx = if (right) s.x - vp.width else 0
        val vy = visY.coerceIn(0, max(0, s.y - vp.height))
        val inset = dp(Prefs.get(this, K.T_EDGE).toFloat()).toInt()
        val hx = if (right) s.x - hp.width - inset else inset
        val hy = vy + vp.height / 2 - hp.height / 2 + dp(Prefs.get(this, K.T_YOFF).toFloat()).toInt()
        return Spot(vx, vy, hx, hy)
    }

    private fun place(p: Spot) {
        vp.x = p.vx; vp.y = p.vy; hp.x = p.hx; hp.y = p.hy
        pillRoot?.let { if (it.isAttachedToWindow) wm.updateViewLayout(it, vp) }
        handleRoot?.let { if (it.isAttachedToWindow) wm.updateViewLayout(it, hp) }
    }

    /** Sets pill size, colour, side and position, and the touch box, from Prefs. */
    private fun applyHandleLayout(attach: Boolean = true) {
        if (handleRoot == null) return
        val right = Prefs.isRight(this)
        val w = dp(Prefs.get(this, K.H_WIDTH).toFloat())
        val h = dp(Prefs.get(this, K.H_HEIGHT).toFloat())
        val gap = dp(Prefs.get(this, K.H_GAP).toFloat())
        // Pill window: room for the press and pull animations.
        vp.width = (w * 1.8f + gap + dp(20f)).toInt()
        vp.height = (h * 1.15f + dp(8f)).toInt()
        // Touch box: set by the user.
        hp.width = dp(Prefs.get(this, K.T_WIDTH).toFloat()).toInt()
        hp.height = dp(Prefs.get(this, K.T_HEIGHT).toFloat()).toInt()
        pill.layoutParams = FrameLayout.LayoutParams(w.toInt(), h.toInt()).apply {
            gravity = Gravity.CENTER_VERTICAL or if (right) Gravity.END else Gravity.START
            val m = (dp(2f) + gap).toInt()
            marginStart = m; marginEnd = m
        }
        pill.background = GradientDrawable().apply {
            cornerRadius = w / 2f
            setColor(Style.handleColor(this@EdgeController))
        }
        pill.alpha = Prefs.get(this, K.H_ALPHA) / 100f
        val y = Prefs.y(this)
        val p = spot(right, if (y < 0) (screen().y * 0.3f).toInt() else y)
        if (attach) place(p) else { vp.x = p.vx; vp.y = p.vy; hp.x = p.hx; hp.y = p.hy }
    }

    /** Asks the system not to use touches on the handle for the back gesture (Android 10+). */
    private fun excludeSystemGesture(v: View) {
        if (Build.VERSION.SDK_INT >= 29) v.systemGestureExclusionRects = listOf(Rect(0, 0, v.width, v.height))
    }

    private fun snapToEdge() {
        val s = screen()
        val right = vp.x + vp.width / 2 > s.x / 2
        Prefs.setRight(this, right)
        (pill.layoutParams as FrameLayout.LayoutParams).gravity =
            Gravity.CENTER_VERTICAL or if (right) Gravity.END else Gravity.START
        pill.requestLayout()
        val target = spot(right, vp.y)
        Prefs.setY(this, target.vy)
        vp.y = target.vy; hp.y = target.hy
        val offset = target.hx - target.vx
        snapAnim?.cancel()
        snapAnim = SpringAnimation(FloatValueHolder(vp.x.toFloat())).apply {
            spring = SpringForce(target.vx.toFloat()).setStiffness(SpringForce.STIFFNESS_MEDIUM).setDampingRatio(0.62f)
            addUpdateListener { _, v, _ ->
                place(Spot(v.toInt(), target.vy, v.toInt() + offset, target.hy))
            }
            addEndListener { _, _, _, _ -> place(target) }
            start()
        }
    }

    private fun springPillBack() {
        SpringAnimation(pill, DynamicAnimation.TRANSLATION_X, 0f).apply {
            spring.stiffness = 700f; spring.dampingRatio = 0.5f; start()
        }
        pill.animate().scaleX(1f).scaleY(1f).alpha(Prefs.get(this, K.H_ALPHA) / 100f)
            .setInterpolator(DecelerateInterpolator()).setDuration(240).start()
    }

    /** Tap = small hint bounce. */
    private fun nudge() {
        val dir = if (Prefs.isRight(this)) -1f else 1f
        pill.animate().translationX(dir * dp(8f)).setDuration(110).withEndAction { springPillBack() }.start()
    }

    /**
     * The panel follows the finger. Swipe out = it opens as far as you pull; swipe back = it closes.
     * On release a spring finishes the movement, starting at the finger's speed.
     * Touch and hold (no movement) = drag mode for the handle; release snaps to the nearest edge.
     */
    private inner class HandleTouch : View.OnTouchListener {
        private var downX = 0f; private var downY = 0f
        private var startX = 0; private var startY = 0; private var relX = 0; private var relY = 0
        private var dragging = false; private var moved = false
        private var pulling = false; private var pullBase = 0f; private var pullX = 0f; private var ticked = false
        private var vt: VelocityTracker? = null
        private val slop = ViewConfiguration.get(this@EdgeController).scaledTouchSlop
        private val longPress = Runnable {
            dragging = true
            haptic(HapticFeedbackConstants.LONG_PRESS)
            pill.animate().translationX(0f).scaleX(1.7f).scaleY(1.1f).alpha(1f)
                .setInterpolator(OvershootInterpolator(2f)).setDuration(220).start()
        }

        private fun inward(dx: Float) = if (Prefs.isRight(this@EdgeController)) -dx else dx

        @SuppressLint("ClickableViewAccessibility")
        override fun onTouch(v: View, e: MotionEvent): Boolean {
            vt?.addMovement(e.withRaw())
            when (e.actionMasked) {
                MotionEvent.ACTION_DOWN -> {
                    excludeSystemGesture(v)
                    vt?.recycle(); vt = VelocityTracker.obtain().also { it.addMovement(e.withRaw()) }
                    downX = e.rawX; downY = e.rawY; startX = vp.x; startY = vp.y
                    relX = hp.x - vp.x; relY = hp.y - vp.y
                    dragging = false; moved = false; pulling = false; ticked = false
                    snapAnim?.cancel()
                    if (!Prefs.on(this@EdgeController, K.LOCK_POS)) {
                        ui.postDelayed(longPress, Prefs.get(this@EdgeController, K.HOLD_MS).toLong())
                    }
                    pill.animate().scaleX(1.25f).alpha(1f).setDuration(100).start()
                }
                MotionEvent.ACTION_MOVE -> {
                    val dx = e.rawX - downX
                    val dy = e.rawY - downY
                    if (dragging) {
                        val nx = (startX + dx).toInt()
                        val ny = (startY + dy).toInt()
                        place(Spot(nx, ny, nx + relX, ny + relY))
                        return true
                    }
                    if (!moved && (abs(dx) > slop || abs(dy) > slop)) {
                        moved = true
                        ui.removeCallbacks(longPress)
                    }
                    val inw = inward(dx)
                    if (!pulling && inw > slop && abs(dx) > abs(dy)) {
                        // Start pulling the panel out with the finger.
                        pulling = true
                        pullX = e.rawX
                        createPanel()
                        progressAnim?.cancel()
                        pullBase = progress
                    }
                    if (pulling) {
                        setProgress(pullBase + inward(e.rawX - pullX) / travel)
                        if (!ticked && progress > 0.5f) { ticked = true; haptic(HapticFeedbackConstants.CLOCK_TICK) }
                        if (ticked && progress < 0.4f) ticked = false
                    } else {
                        // Rubber-band before the pull starts.
                        val dir = if (Prefs.isRight(this@EdgeController)) -1f else 1f
                        val r = inw.coerceAtLeast(0f)
                        pill.translationX = dir * dp(14f) * (1f - 1f / (1f + r / dp(40f)))
                    }
                }
                MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                    ui.removeCallbacks(longPress)
                    vt?.computeCurrentVelocity(1000)
                    val vel = inward(vt?.xVelocity ?: 0f)
                    vt?.recycle(); vt = null
                    when {
                        dragging -> snapToEdge()
                        pulling -> {
                            val pulled = progress * travel
                            val need = minOf(travel * 0.5f, dp(Prefs.get(this@EdgeController, K.SWIPE_DIST) * 2.5f))
                            val open = if (abs(vel) > dp(350f)) vel > 0 else pulled > need
                            settle(open, vel / travel)
                        }
                        !moved && e.actionMasked == MotionEvent.ACTION_UP -> {
                            v.performClick()
                            if (Prefs.on(this@EdgeController, K.TAP_OPEN)) openPanel() else { nudge(); return true }
                        }
                    }
                    springPillBack()
                }
            }
            return true
        }

        /** Velocity must use screen coordinates, because the window can move. */
        private fun MotionEvent.withRaw(): MotionEvent =
            MotionEvent.obtain(this).also { it.setLocation(rawX, rawY) }
    }

    // ---------- Clipboard panel ----------

    private var detailOpen = false
    private var animSpeed = 1f

    // Open state: 0 = hidden, 1 = fully open. Finger and springs both drive it.
    private var progress = 0f
    private var progressAnim: SpringAnimation? = null
    private var travel = 1f
    private var panelCard: View? = null
    private var panelScrim: View? = null
    private var panelParams: WindowManager.LayoutParams? = null
    private var blurMax = 0
    private var lastBlur = -1

    private fun haptic(type: Int) {
        if (Prefs.on(this, K.HAPTICS)) (panel ?: handleRoot)?.performHapticFeedback(type)
    }

    /** Places every moving part for open state [f] (0..1). */
    private fun setProgress(f: Float) {
        val root = panel ?: return
        progress = f.coerceIn(0f, 1f)
        val p = progress
        val sign = if (Prefs.isRight(this)) 1f else -1f
        panelCard?.translationX = travel * (1f - p) * sign
        panelScrim?.alpha = p
        pillRoot?.alpha = 1f - p
        handleRoot?.alpha = 1f - p
        val lp = panelParams
        if (Build.VERSION.SDK_INT >= 31 && blurMax > 0 && lp != null) {
            val b = (blurMax * p).toInt()
            if (abs(b - lastBlur) >= 2 || (b == 0 && lastBlur != 0) || (b == blurMax && lastBlur != blurMax)) {
                lastBlur = b
                lp.blurBehindRadius = b
                if (root.isAttachedToWindow) runCatching { wm.updateViewLayout(root, lp) }
            }
        }
    }

    /** Springs to open (true) or closed (false). [velocity] is in open-state units per second. */
    private fun settle(open: Boolean, velocity: Float = 0f) {
        val root = panel ?: return
        progressAnim?.cancel()
        // A closing panel must not catch touches: they pass through to the handle and other apps at once.
        setPanelTouchable(open)
        progressAnim = SpringAnimation(FloatValueHolder(progress)).apply {
            spring = SpringForce(if (open) 1f else 0f)
                .setStiffness(380f * animSpeed * animSpeed)
                .setDampingRatio(if (open) 0.85f else 1f)
            setMinimumVisibleChange(DynamicAnimation.MIN_VISIBLE_CHANGE_SCALE)
            setStartVelocity(velocity)
            addUpdateListener { anim, v, _ ->
                setProgress(v)
                // Remove the window when it is out of sight; do not wait for the spring's slow tail.
                if (!open && v <= 0.01f) {
                    ui.post { if (panel === root && progressAnim === anim) removePanel() }
                }
            }
            addEndListener { anim, canceled, _, _ ->
                if (!canceled && !open && panel === root && progressAnim === anim) removePanel()
            }
            start()
        }
    }

    private fun setPanelTouchable(touchable: Boolean) {
        val root = panel ?: return
        val lp = panelParams ?: return
        val off = WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE or WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE
        val flags = if (touchable) lp.flags and off.inv() else lp.flags or off
        if (flags == lp.flags) return
        lp.flags = flags
        if (root.isAttachedToWindow) runCatching { wm.updateViewLayout(root, lp) }
    }

    private fun openPanel() {
        if (handleRoot == null) return
        createPanel()
        settle(true)
    }

    private fun closePanel(animate: Boolean = true) {
        if (panel == null) return
        if (animate) settle(false) else removePanel()
    }

    /** Builds the panel window in the hidden state (progress 0). Does nothing if it exists. */
    private fun createPanel() {
        if (panel != null || handleRoot == null) return
        ClipStore.prune()
        val ctx = Style.themed(this)
        val root = LayoutInflater.from(ctx).inflate(R.layout.panel, null) as SwipeFrame
        animSpeed = Prefs.get(this, K.ANIM).coerceIn(25, 300) / 100f
        val scrim = root.findViewById<View>(R.id.scrim)
        val card = root.findViewById<View>(R.id.card)
        val listPage = root.findViewById<View>(R.id.list_page)
        val detailPage = root.findViewById<View>(R.id.detail_page)
        val list = root.findViewById<RecyclerView>(R.id.list)
        val empty = root.findViewById<View>(R.id.empty)
        val right = Prefs.isRight(this)
        detailOpen = false

        val cardW = dp(Prefs.get(this, K.P_WIDTH).toFloat())
        travel = cardW + dp(24f)
        (card.layoutParams as FrameLayout.LayoutParams).apply {
            gravity = if (right) Gravity.END else Gravity.START
            width = cardW.toInt()
            // Height and vertical position are adjustable; the panel does not need the full screen side.
            val sh = screen().y
            val h = (sh * Prefs.get(this@EdgeController, K.P_HEIGHT).coerceIn(20, 100) / 100f).toInt()
            height = h
            gravity = gravity or Gravity.TOP
            val free = sh - h
            topMargin = if (Prefs.on(this@EdgeController, K.P_FOLLOW)) {
                (vp.y + vp.height / 2 - h / 2).coerceIn(0, maxOf(0, free))
            } else {
                free * Prefs.get(this@EdgeController, K.P_VPOS).coerceIn(0, 100) / 100
            }
        }
        card.background = Style.panelBackground(ctx, right)
        card.setPadding(0, dp(Prefs.get(this, K.P_TOP).toFloat()).toInt(), 0, dp(16f).toInt())
        scrim.setBackgroundColor(Style.alpha(0xFF000000.toInt(), Prefs.get(this, K.DIM)))

        val adapter = ClipAdapter(
            Look.from(this),
            onOpen = { showDetail(root, it) },
            onCopy = { copyClip(it); if (Prefs.on(this, K.CLOSE_AFTER_COPY)) closePanel() },
            onPin = { ClipStore.togglePin(it) },
            onDelete = { ClipStore.delete(it) },
        )
        list.layoutManager = LinearLayoutManager(ctx)
        list.adapter = adapter
        val render = {
            val items = ClipStore.all()
            adapter.submitList(items)
            empty.visibility = if (items.isEmpty()) View.VISIBLE else View.GONE
        }
        render()
        Prefs.scroll(this).let { (pos, off) ->
            (list.layoutManager as LinearLayoutManager).scrollToPositionWithOffset(pos, off)
        }
        panelListener = render
        ClipStore.addListener(render)

        root.findViewById<View>(R.id.clear).setOnClickListener { ClipStore.clearUnpinned() }
        root.findViewById<View>(R.id.detail_back).setOnClickListener { hideDetail(root) }
        scrim.setOnClickListener { closePanel() }
        root.isFocusableInTouchMode = true
        root.setOnKeyListener { _, key, ev ->
            if (key == KeyEvent.KEYCODE_BACK && ev.action == KeyEvent.ACTION_UP) {
                if (detailOpen) hideDetail(root) else closePanel()
                true
            } else false
        }
        // A focused window may read the clipboard: catch anything copied since the last check.
        root.viewTreeObserver.addOnWindowFocusChangeListener { has -> if (has) readClipboard() }

        // Push the panel back toward the edge with a finger to close it.
        var dragBase = 0f
        root.edgeSign = if (right) 1f else -1f
        root.onDragStart = { progressAnim?.cancel(); dragBase = progress }
        root.onDrag = { out -> setProgress(dragBase - out / travel) }
        root.onDragEnd = { v ->
            val open = if (abs(v) > dp(350f)) v < 0 else progress > 0.5f
            settle(open, -v / travel)
        }

        val p = WindowManager.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT, overlayType,
            WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN or WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS,
            PixelFormat.TRANSLUCENT
        )
        if (Build.VERSION.SDK_INT >= 28) {
            p.layoutInDisplayCutoutMode = WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES
        }
        val blur = dp(Prefs.get(this, K.BLUR).toFloat()).toInt()
        blurMax = if (Build.VERSION.SDK_INT >= 31 && blur > 0 && wm.isCrossWindowBlurEnabled) blur else 0
        if (blurMax > 0) p.flags = p.flags or WindowManager.LayoutParams.FLAG_BLUR_BEHIND
        lastBlur = -1
        panelParams = p
        panelCard = card
        panelScrim = scrim
        listPage.visibility = View.VISIBLE
        detailPage.visibility = View.GONE

        panel = root
        progress = 0f
        setProgress(0f)
        wm.addView(root, p)
        root.requestFocus()
        list.scheduleLayoutAnimation()
    }

    private fun removePanel() {
        val root = panel ?: return
        progressAnim?.cancel()
        progressAnim = null
        panel = null
        root.findViewById<RecyclerView>(R.id.list)?.let { list ->
            val lm = list.layoutManager as? LinearLayoutManager
            val pos = lm?.findFirstVisibleItemPosition() ?: RecyclerView.NO_POSITION
            if (pos != RecyclerView.NO_POSITION) {
                Prefs.setScroll(this, pos, lm!!.findViewByPosition(pos)?.top?.minus(list.paddingTop) ?: 0)
            }
        }
        panelCard = null; panelScrim = null; panelParams = null
        panelListener?.let { ClipStore.removeListener(it) }
        panelListener = null
        progress = 0f
        pillRoot?.alpha = 1f
        handleRoot?.alpha = 1f
        if (root.isAttachedToWindow) runCatching { wm.removeView(root) }
    }

    /** Full clip view inside the panel. */
    private fun showDetail(root: View, c: Clip) {
        val listPage = root.findViewById<View>(R.id.list_page)
        val page = root.findViewById<View>(R.id.detail_page)
        val text = root.findViewById<TextView>(R.id.detail_text)
        val image = root.findViewById<ImageView>(R.id.detail_image)
        val info = root.findViewById<TextView>(R.id.detail_info)
        root.findViewById<TextView>(R.id.detail_time).text = android.text.format.DateUtils
            .getRelativeTimeSpanString(c.time, System.currentTimeMillis(), android.text.format.DateUtils.MINUTE_IN_MILLIS)
        root.findViewById<ScrollView>(R.id.detail_scroll).scrollTo(0, 0)
        if (c.isImage) {
            text.visibility = View.GONE
            image.visibility = View.VISIBLE
            image.setImageDrawable(null)
            ClipAdapter.loadThumb(ClipStore.imageFile(c), c.key, 1440) { image.setImageBitmap(it) }
            info.setText(R.string.image_clip)
        } else {
            val t = c.text!!
            image.visibility = View.GONE
            text.visibility = View.VISIBLE
            text.setTextIsSelectable(t.length < 200_000)
            text.text = ClipAdapter.styled(c, Int.MAX_VALUE)
            info.text = getString(R.string.chars, t.length)
        }
        root.findViewById<View>(R.id.detail_copy).setOnClickListener {
            copyClip(c)
            if (Prefs.on(this, K.CLOSE_AFTER_COPY)) closePanel()
        }
        detailOpen = true
        val w = root.findViewById<View>(R.id.card).width.toFloat()
        page.visibility = View.VISIBLE
        page.translationX = w * 0.35f
        page.alpha = 0f
        page.animate().translationX(0f).alpha(1f).setDuration(260).setInterpolator(DecelerateInterpolator(2f)).start()
        listPage.animate().translationX(-w * 0.2f).alpha(0f).setDuration(200)
            .withEndAction { listPage.visibility = View.INVISIBLE }.start()
    }

    private fun hideDetail(root: View) {
        val listPage = root.findViewById<View>(R.id.list_page)
        val page = root.findViewById<View>(R.id.detail_page)
        detailOpen = false
        val w = root.findViewById<View>(R.id.card).width.toFloat()
        listPage.visibility = View.VISIBLE
        listPage.animate().translationX(0f).alpha(1f).setDuration(260).setInterpolator(DecelerateInterpolator(2f)).start()
        page.animate().translationX(w * 0.35f).alpha(0f).setDuration(200)
            .withEndAction { page.visibility = View.GONE; root.findViewById<TextView>(R.id.detail_text).text = "" }.start()
    }

    /** Puts a clip back on the system clipboard. */
    private fun copyClip(c: Clip) {
        runCatching {
            val data = when {
                c.isImage -> {
                    val uri = FileProvider.getUriForFile(this, "$packageName.files", ClipStore.imageFile(c))
                    ClipData.newUri(contentResolver, "Image", uri)
                }
                // Android limits one clipboard transfer to about 1 MB. Larger text goes as a text file.
                c.text!!.length > 250_000 -> {
                    val f = File(cacheDir, "share").apply { mkdirs() }.let { File(it, "clip.txt") }
                    f.writeText(c.text)
                    val uri = FileProvider.getUriForFile(this, "$packageName.files", f)
                    ClipData("EdgeClip", arrayOf("text/plain"), ClipData.Item(uri))
                }
                c.html != null -> ClipData.newHtmlText("EdgeClip", c.text, c.html)
                else -> ClipData.newPlainText("EdgeClip", c.text)
            }
            cm.setPrimaryClip(data)
            haptic(HapticFeedbackConstants.CONFIRM)
            if (Build.VERSION.SDK_INT < 33) Toast.makeText(this, R.string.copied, Toast.LENGTH_SHORT).show()
        }.onFailure { Toast.makeText(this, R.string.copy_failed, Toast.LENGTH_SHORT).show() }
    }

    // ---------- Clipboard reading ----------

    private fun readClipboard() {
        runCatching {
            val clip = cm.primaryClip ?: return
            if (clip.itemCount == 0) return
            val desc = clip.description
            if (desc.extras?.getBoolean("android.content.extra.IS_SENSITIVE") == true) return // passwords etc.
            val item = clip.getItemAt(0)
            val uri: Uri? = item.uri
            if (uri != null) {
                val mime = runCatching { contentResolver.getType(uri) }.getOrNull() ?: desc.getMimeType(0)
                if (mime?.startsWith("image/") == true || desc.hasMimeType("image/*")) {
                    if (!Prefs.on(this, K.SAVE_IMAGES)) return
                    val ext = when {
                        mime?.contains("png") == true -> "png"
                        mime?.contains("gif") == true -> "gif"
                        mime?.contains("webp") == true -> "webp"
                        else -> "jpg"
                    }
                    // Read the bytes now, while the clipboard grant is valid; store a copy.
                    ClipStore.io.execute {
                        runCatching {
                            contentResolver.openInputStream(uri)?.use { it.readBytes() }
                        }.getOrNull()?.let { if (it.isNotEmpty()) ClipStore.addImage(it, ext) }
                    }
                    return
                }
            }
            val text = item.text?.toString() ?: item.coerceToText(this)?.toString() ?: return
            ClipStore.addText(text, item.htmlText)
        }
    }

    /** Briefly adds a 1×1 focusable window so the app may read the clipboard, then removes it. */
    private fun grabClipboard() {
        if (panel != null) { readClipboard(); return }
        if (grabView != null) return
        val v = View(this)
        val p = WindowManager.LayoutParams(
            1, 1, overlayType,
            WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL or
                WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE or
                WindowManager.LayoutParams.FLAG_ALT_FOCUSABLE_IM,
            PixelFormat.TRANSLUCENT
        ).apply { gravity = Gravity.TOP or Gravity.START }
        val remove = {
            if (grabView === v) {
                grabView = null
                runCatching { wm.removeView(v) }
            }
        }
        v.viewTreeObserver.addOnWindowFocusChangeListener { has ->
            if (has) { readClipboard(); ui.post { remove() } }
        }
        grabView = v
        runCatching { wm.addView(v, p) }.onFailure { grabView = null }
        ui.postDelayed({ remove() }, 800)
    }
}
