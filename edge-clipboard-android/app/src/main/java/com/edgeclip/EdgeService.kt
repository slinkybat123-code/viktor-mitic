package com.edgeclip

import android.annotation.SuppressLint
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.content.res.Configuration
import android.graphics.PixelFormat
import android.graphics.Point
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

class EdgeService : Service() {

    companion object {
        const val ACTION_REFRESH = "com.edgeclip.REFRESH"
        const val ACTION_GRAB = "com.edgeclip.GRAB"
        const val ACTION_OPEN = "com.edgeclip.OPEN"
        const val ACTION_STOP = "com.edgeclip.STOP"
        private const val CHANNEL = "edge"
        private const val NOTIF_ID = 1

        @Volatile var running = false
            private set

        fun start(ctx: Context, action: String? = null) {
            val i = Intent(ctx, EdgeService::class.java).setAction(action)
            ctx.startForegroundService(i)
        }

        fun stop(ctx: Context) {
            ctx.stopService(Intent(ctx, EdgeService::class.java))
        }
    }

    private lateinit var wm: WindowManager
    private lateinit var cm: ClipboardManager
    private val ui = Handler(Looper.getMainLooper())

    private var handleRoot: FrameLayout? = null
    private lateinit var pill: View
    private lateinit var hp: WindowManager.LayoutParams
    private var snapAnim: SpringAnimation? = null

    private var panel: View? = null
    private var panelListener: (() -> Unit)? = null
    private var grabView: View? = null

    private val clipListener = ClipboardManager.OnPrimaryClipChangedListener { readClipboard() }

    private fun dp(v: Float) = v * resources.displayMetrics.density
    private val overlayType = WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        wm = getSystemService(WINDOW_SERVICE) as WindowManager
        cm = getSystemService(CLIPBOARD_SERVICE) as ClipboardManager
        ClipStore.init(this)
        goForeground()
        running = true
        cm.addPrimaryClipChangedListener(clipListener)
        if (android.provider.Settings.canDrawOverlays(this)) addHandle() else stopSelf()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        goForeground()
        when (intent?.action) {
            ACTION_REFRESH -> applyHandleLayout()
            ACTION_GRAB -> grabClipboard()
            ACTION_OPEN -> openPanel()
            ACTION_STOP -> { Prefs.setEnabled(this, false); stopSelf() }
        }
        return START_STICKY
    }

    override fun onConfigurationChanged(newConfig: Configuration) {
        super.onConfigurationChanged(newConfig)
        closePanel(animate = false)
        ui.post { applyHandleLayout() }
    }

    override fun onDestroy() {
        running = false
        cm.removePrimaryClipChangedListener(clipListener)
        snapAnim?.cancel()
        closePanel(animate = false)
        listOfNotNull(handleRoot, grabView).forEach { runCatching { wm.removeView(it) } }
        handleRoot = null; grabView = null
        super.onDestroy()
    }

    // ---------- Foreground notification ----------

    private fun goForeground() {
        val nm = getSystemService(NotificationManager::class.java)
        if (nm.getNotificationChannel(CHANNEL) == null) {
            nm.createNotificationChannel(
                NotificationChannel(CHANNEL, getString(R.string.notif_channel), NotificationManager.IMPORTANCE_MIN)
            )
        }
        val flags = PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        val open = PendingIntent.getForegroundService(
            this, 1, Intent(this, EdgeService::class.java).setAction(ACTION_OPEN), flags
        )
        val stop = PendingIntent.getForegroundService(
            this, 2, Intent(this, EdgeService::class.java).setAction(ACTION_STOP), flags
        )
        val n = Notification.Builder(this, CHANNEL)
            .setSmallIcon(R.drawable.ic_clip)
            .setContentTitle(getString(R.string.notif_title))
            .setContentText(getString(R.string.notif_text))
            .setContentIntent(open)
            .setOngoing(true)
            .addAction(Notification.Action.Builder(null, getString(R.string.stop), stop).build())
            .build()
        if (Build.VERSION.SDK_INT >= 34) {
            startForeground(NOTIF_ID, n, ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE)
        } else {
            startForeground(NOTIF_ID, n)
        }
    }

    // ---------- Edge handle ----------

    private fun screen(): Point =
        if (Build.VERSION.SDK_INT >= 30) {
            val b = wm.currentWindowMetrics.bounds
            Point(b.width(), b.height())
        } else {
            Point().also { @Suppress("DEPRECATION") wm.defaultDisplay.getRealSize(it) }
        }

    private fun addHandle() {
        pill = View(this)
        val root = FrameLayout(this).apply {
            addView(pill)
            contentDescription = getString(R.string.handle_desc)
            isHapticFeedbackEnabled = true
        }
        hp = WindowManager.LayoutParams(
            0, 0, overlayType,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS,
            PixelFormat.TRANSLUCENT
        ).apply {
            gravity = Gravity.TOP or Gravity.START
            if (Build.VERSION.SDK_INT >= 30) {
                layoutInDisplayCutoutMode = WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_ALWAYS
            } else if (Build.VERSION.SDK_INT >= 28) {
                layoutInDisplayCutoutMode = WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES
            }
        }
        handleRoot = root
        applyHandleLayout(attach = false)
        root.setOnTouchListener(HandleTouch())
        wm.addView(root, hp)
        root.alpha = 0f
        root.animate().alpha(1f).setDuration(300).start()
    }

    /** Sets handle size, colour, side and position from Prefs. */
    private fun applyHandleLayout(attach: Boolean = true) {
        val root = handleRoot ?: return
        val right = Prefs.isRight(this)
        val w = dp(Prefs.widthDp(this).toFloat())
        val h = dp(Prefs.heightDp(this).toFloat())
        hp.width = max(w * 2.2f, dp(24f)).toInt()   // wider touch area than the visible pill
        hp.height = (h + dp(16f)).toInt()
        pill.layoutParams = FrameLayout.LayoutParams(w.toInt(), h.toInt()).apply {
            gravity = Gravity.CENTER_VERTICAL or if (right) Gravity.END else Gravity.START
            marginStart = dp(2f).toInt(); marginEnd = dp(2f).toInt()
        }
        pill.background = GradientDrawable().apply {
            cornerRadius = w / 2f
            setColor(getColor(R.color.handle))
        }
        pill.alpha = Prefs.alpha(this) / 100f
        val s = screen()
        hp.x = if (right) s.x - hp.width else 0
        val y = Prefs.y(this)
        hp.y = (if (y < 0) (s.y * 0.3f).toInt() else y).coerceIn(0, max(0, s.y - hp.height))
        if (attach && root.isAttachedToWindow) wm.updateViewLayout(root, hp)
    }

    private fun snapToEdge() {
        val root = handleRoot ?: return
        val s = screen()
        val right = hp.x + hp.width / 2 > s.x / 2
        Prefs.setRight(this, right)
        hp.y = hp.y.coerceIn(0, max(0, s.y - hp.height))
        Prefs.setY(this, hp.y)
        (pill.layoutParams as FrameLayout.LayoutParams).gravity =
            Gravity.CENTER_VERTICAL or if (right) Gravity.END else Gravity.START
        pill.requestLayout()
        val target = (if (right) s.x - hp.width else 0).toFloat()
        snapAnim?.cancel()
        snapAnim = SpringAnimation(FloatValueHolder(hp.x.toFloat())).apply {
            spring = SpringForce(target).setStiffness(SpringForce.STIFFNESS_MEDIUM).setDampingRatio(0.62f)
            addUpdateListener { _, v, _ ->
                hp.x = v.toInt()
                if (root.isAttachedToWindow) wm.updateViewLayout(root, hp)
            }
            start()
        }
    }

    /** Tap or swipe inward = open. Hold 0.4 s = drag mode, release snaps to nearest edge. */
    private inner class HandleTouch : View.OnTouchListener {
        private var downX = 0f; private var downY = 0f
        private var startX = 0; private var startY = 0
        private var dragging = false; private var moved = false; private var opened = false
        private val slop = ViewConfiguration.get(this@EdgeService).scaledTouchSlop
        private val longPress = Runnable {
            dragging = true
            handleRoot?.performHapticFeedback(HapticFeedbackConstants.LONG_PRESS)
            pill.animate().scaleX(1.7f).scaleY(1.1f).alpha(1f)
                .setInterpolator(OvershootInterpolator(2f)).setDuration(220).start()
        }

        @SuppressLint("ClickableViewAccessibility")
        override fun onTouch(v: View, e: MotionEvent): Boolean {
            when (e.actionMasked) {
                MotionEvent.ACTION_DOWN -> {
                    downX = e.rawX; downY = e.rawY; startX = hp.x; startY = hp.y
                    dragging = false; moved = false; opened = false
                    snapAnim?.cancel()
                    ui.postDelayed(longPress, 400)
                    pill.animate().scaleX(1.3f).alpha(1f).setDuration(120).start()
                }
                MotionEvent.ACTION_MOVE -> {
                    val dx = e.rawX - downX
                    val dy = e.rawY - downY
                    if (dragging) {
                        hp.x = (startX + dx).toInt()
                        hp.y = (startY + dy).toInt()
                        wm.updateViewLayout(v, hp)
                    } else if (abs(dx) > slop || abs(dy) > slop) {
                        moved = true
                        ui.removeCallbacks(longPress)
                        val inward = if (Prefs.isRight(this@EdgeService)) -dx else dx
                        if (!opened && inward > dp(18f) && abs(dx) > abs(dy)) {
                            opened = true
                            openPanel()
                        }
                    }
                }
                MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                    ui.removeCallbacks(longPress)
                    if (dragging) snapToEdge()
                    else if (!moved && e.actionMasked == MotionEvent.ACTION_UP) { v.performClick(); openPanel() }
                    pill.animate().scaleX(1f).scaleY(1f).alpha(Prefs.alpha(this@EdgeService) / 100f)
                        .setInterpolator(DecelerateInterpolator()).setDuration(240).start()
                }
            }
            return true
        }
    }

    // ---------- Clipboard panel ----------

    private fun openPanel() {
        if (panel != null || handleRoot == null) return
        val ctx = ContextThemeWrapper(this, R.style.Theme_EdgeClip)
        val root = LayoutInflater.from(ctx).inflate(R.layout.panel, null) as FrameLayout
        val scrim = root.findViewById<View>(R.id.scrim)
        val card = root.findViewById<View>(R.id.card)
        val list = root.findViewById<RecyclerView>(R.id.list)
        val empty = root.findViewById<View>(R.id.empty)
        val count = root.findViewById<TextView>(R.id.count)
        val right = Prefs.isRight(this)

        (card.layoutParams as FrameLayout.LayoutParams).apply {
            gravity = Gravity.CENTER_VERTICAL or if (right) Gravity.END else Gravity.START
            height = (screen().y * 0.72f).toInt()
        }

        val adapter = ClipAdapter(
            onCopy = { clip ->
                cm.setPrimaryClip(ClipData.newPlainText("EdgeClip", clip.text))
                if (Build.VERSION.SDK_INT < 33) Toast.makeText(this, R.string.copied, Toast.LENGTH_SHORT).show()
                closePanel()
            },
            onPin = { ClipStore.togglePin(it) },
            onDelete = { ClipStore.delete(it) },
        )
        list.layoutManager = LinearLayoutManager(ctx)
        list.adapter = adapter

        val render = {
            val items = ClipStore.all()
            adapter.submitList(items)
            empty.visibility = if (items.isEmpty()) View.VISIBLE else View.GONE
            count.text = getString(R.string.count, items.size, ClipStore.MAX)
        }
        render()
        panelListener = render
        ClipStore.addListener(render)

        root.findViewById<View>(R.id.clear).setOnClickListener { ClipStore.clearUnpinned() }
        scrim.setOnClickListener { closePanel() }
        root.isFocusableInTouchMode = true
        root.setOnKeyListener { _, key, ev ->
            if (key == KeyEvent.KEYCODE_BACK && ev.action == KeyEvent.ACTION_UP) { closePanel(); true } else false
        }
        // A focused window may read the clipboard: catch anything copied since the last check.
        root.viewTreeObserver.addOnWindowFocusChangeListener { has -> if (has) readClipboard() }

        val p = WindowManager.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT, overlayType,
            WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN, PixelFormat.TRANSLUCENT
        )
        wm.addView(root, p)
        panel = root
        root.requestFocus()

        scrim.alpha = 0f
        scrim.animate().alpha(1f).setDuration(240).start()
        card.alpha = 0f
        card.post {
            card.translationX = (card.width + dp(32f)) * if (right) 1f else -1f
            card.alpha = 1f
            SpringAnimation(card, DynamicAnimation.TRANSLATION_X, 0f).apply {
                spring.stiffness = 520f
                spring.dampingRatio = 0.78f
                start()
            }
            list.scheduleLayoutAnimation()
        }
        handleRoot?.animate()?.alpha(0f)?.setDuration(120)?.start()
    }

    private fun closePanel(animate: Boolean = true) {
        val root = panel ?: return
        panel = null
        panelListener?.let { ClipStore.removeListener(it) }
        panelListener = null
        handleRoot?.animate()?.alpha(1f)?.setDuration(220)?.start()
        val remove = { if (root.isAttachedToWindow) runCatching { wm.removeView(root) } }
        if (!animate) { remove(); return }
        val card = root.findViewById<View>(R.id.card)
        val right = Prefs.isRight(this)
        root.findViewById<View>(R.id.scrim).animate().alpha(0f).setDuration(200).start()
        card.animate()
            .translationX((card.width + dp(32f)) * if (right) 1f else -1f)
            .setInterpolator(AccelerateInterpolator(1.5f))
            .setDuration(200)
            .withEndAction { remove() }
            .start()
    }

    // ---------- Clipboard reading ----------

    private fun readClipboard() {
        runCatching {
            val clip = cm.primaryClip ?: return
            if (clip.itemCount == 0) return
            val sensitive = clip.description.extras?.getBoolean("android.content.extra.IS_SENSITIVE") == true
            if (sensitive) return // skip passwords and other private clips
            val text = clip.getItemAt(0).coerceToText(this)?.toString() ?: return
            ClipStore.add(text)
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
