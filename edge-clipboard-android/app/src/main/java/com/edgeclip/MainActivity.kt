package com.edgeclip

import android.Manifest
import android.accessibilityservice.AccessibilityServiceInfo
import android.app.Activity
import android.app.AlertDialog
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.drawable.GradientDrawable
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.PowerManager
import android.provider.DocumentsContract
import android.provider.Settings
import android.view.Gravity
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.view.accessibility.AccessibilityManager
import android.widget.Button
import android.widget.FrameLayout
import android.widget.HorizontalScrollView
import android.widget.LinearLayout
import android.widget.SeekBar
import android.widget.Switch
import android.widget.TextView

/** Settings screen. Every setting has a control; the preview at the top updates live. */
class MainActivity : Activity() {

    private lateinit var root: LinearLayout
    private lateinit var permCard: LinearLayout
    private lateinit var preview: FrameLayout
    private lateinit var folderLabel: TextView
    private lateinit var mainToggle: Switch
    private val rebuilders = mutableListOf<() -> Unit>()

    private fun dp(v: Number) = Style.dp(this, v).toInt()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        ClipStore.init(this)
        root = findViewById(R.id.root)
        build()
    }

    override fun onResume() {
        super.onResume()
        mainToggle.isChecked = Prefs.enabled(this) && Settings.canDrawOverlays(this)
        if (mainToggle.isChecked && !EdgeService.running) EdgeService.start(this)
        buildPermissions()
        updatePreview()
    }

    // ---------------- Layout ----------------

    private fun build() {
        root.removeAllViews()
        rebuilders.clear()

        text(getString(R.string.app_name), 32f, R.color.text).apply { setPadding(dp(8), dp(28), dp(8), 0) }
        text(getString(R.string.main_intro), 14f, R.color.sub).apply { setPadding(dp(8), dp(6), dp(8), dp(12)) }

        val top = card()
        mainToggle = Switch(this).apply {
            text = getString(R.string.toggle); textSize = 17f; setTextColor(getColor(R.color.text))
            minHeight = dp(56); setPadding(dp(16), 0, dp(16), 0)
            setOnCheckedChangeListener { _, on ->
                if (on && !Settings.canDrawOverlays(this@MainActivity)) {
                    isChecked = false; openOverlaySettings(); return@setOnCheckedChangeListener
                }
                Prefs.setEnabled(this@MainActivity, on)
                if (on) EdgeService.start(this@MainActivity) else EdgeService.stop(this@MainActivity)
            }
        }
        top.addView(mainToggle)
        top.addView(pillButton(getString(R.string.open_panel)) {
            if (Settings.canDrawOverlays(this)) {
                Prefs.setEnabled(this, true)
                EdgeService.start(this, EdgeService.ACTION_OPEN)
                moveTaskToBack(true)
            } else openOverlaySettings()
        })

        section(R.string.sec_preview)
        preview = FrameLayout(this).apply {
            background = GradientDrawable(GradientDrawable.Orientation.TL_BR,
                intArrayOf(0xFFFF8A65.toInt(), 0xFF7E57C2.toInt(), 0xFF26C6DA.toInt())).apply { cornerRadius = Style.dp(this@MainActivity, 24) }
            clipToOutline = true
            layoutParams = LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(300))
        }
        root.addView(preview)

        section(R.string.permissions)
        permCard = card()

        // Handle
        section(R.string.sec_handle)
        var c = card()
        chips(c, R.string.side, listOf(R.string.left, R.string.right),
            { if (Prefs.isRight(this)) 1 else 0 }) { Prefs.setRight(this, it == 1); handleChanged() }
        swatches(c)
        slider(c, R.string.width, K.H_WIDTH, 2, 20, "dp") { handleChanged() }
        slider(c, R.string.height, K.H_HEIGHT, 30, 200, "dp") { handleChanged() }
        slider(c, R.string.opacity, K.H_ALPHA, 10, 100, "%") { handleChanged() }
        slider(c, R.string.gap, K.H_GAP, 0, 32, "dp") { handleChanged() }
        slider(c, R.string.swipe_dist, K.SWIPE_DIST, 8, 80, "dp")
        slider(c, R.string.hold_time, K.HOLD_MS, 200, 1500, "ms", step = 50)
        toggle(c, R.string.tap_open, R.string.tap_open_desc, K.TAP_OPEN)
        toggle(c, R.string.lock_pos, R.string.lock_pos_desc, K.LOCK_POS)
        toggle(c, R.string.haptics, 0, K.HAPTICS)

        // Panel
        section(R.string.sec_panel)
        c = card()
        chips(c, R.string.theme, listOf(R.string.theme_system, R.string.theme_light, R.string.theme_dark),
            { Prefs.get(this, K.THEME) }) { Prefs.set(this, K.THEME, it); updatePreview() }
        slider(c, R.string.panel_width, K.P_WIDTH, 120, 360, "dp") { updatePreview() }
        slider(c, R.string.panel_opacity, K.P_ALPHA, 0, 100, "%") { updatePreview() }
        slider(c, R.string.blur, K.BLUR, 0, 80, "dp", desc = if (Build.VERSION.SDK_INT >= 31) 0 else R.string.blur_unsupported)
        slider(c, R.string.dim, K.DIM, 0, 90, "%")
        slider(c, R.string.panel_radius, K.P_RADIUS, 0, 48, "dp") { updatePreview() }
        slider(c, R.string.panel_top, K.P_TOP, 0, 160, "dp")
        slider(c, R.string.anim_speed, K.ANIM, 25, 300, "%", step = 5)

        // Cards
        section(R.string.sec_cards)
        c = card()
        slider(c, R.string.text_size, K.TEXT_SP, 9, 32, "sp") { updatePreview() }
        slider(c, R.string.preview_lines, K.LINES, 1, 12, "") { updatePreview() }
        slider(c, R.string.card_opacity, K.C_ALPHA, 0, 100, "%") { updatePreview() }
        slider(c, R.string.card_radius, K.C_RADIUS, 0, 32, "dp") { updatePreview() }
        slider(c, R.string.card_gap, K.C_GAP, 0, 24, "dp") { updatePreview() }
        slider(c, R.string.card_pad, K.C_PAD, 2, 28, "dp") { updatePreview() }
        toggle(c, R.string.show_copy, 0, K.SHOW_COPY) { updatePreview() }
        slider(c, R.string.copy_h, K.COPY_H, 24, 72, "dp") { updatePreview() }
        slider(c, R.string.copy_sp, K.COPY_SP, 9, 24, "sp") { updatePreview() }
        toggle(c, R.string.source_colors, R.string.source_colors_desc, K.SOURCE_COLORS) { updatePreview() }
        toggle(c, R.string.close_after_copy, 0, K.CLOSE_AFTER_COPY)

        // Storage
        section(R.string.sec_storage)
        c = card()
        toggle(c, R.string.unlimited, R.string.unlimited_desc, K.UNLIMITED) { ClipStore.prune() }
        slider(c, R.string.max_clips, K.MAX_CLIPS, 5, 500, "", step = 5) { ClipStore.prune() }
        chips(c, R.string.auto_delete, listOf(R.string.never, R.string.h1, R.string.d1, R.string.d7, R.string.d30),
            { Prefs.get(this, K.AUTO_DELETE) }) { Prefs.set(this, K.AUTO_DELETE, it); ClipStore.prune() }
        toggle(c, R.string.save_images, 0, K.SAVE_IMAGES)
        val loc = row(c, R.string.location, R.string.location_desc)
        folderLabel = TextView(this).apply { textSize = 14f; setTextColor(getColor(R.color.accent)); setPadding(dp(16), 0, dp(16), dp(4)) }
        c.addView(folderLabel)
        updateFolderLabel()
        val btns = LinearLayout(this).apply { setPadding(dp(8), 0, dp(8), dp(8)) }
        btns.addView(textButton(getString(R.string.choose_folder)) {
            @Suppress("DEPRECATION")
            startActivityForResult(Intent(Intent.ACTION_OPEN_DOCUMENT_TREE).addFlags(
                Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION or Intent.FLAG_GRANT_READ_URI_PERMISSION or
                    Intent.FLAG_GRANT_WRITE_URI_PERMISSION), REQ_FOLDER)
        })
        btns.addView(textButton(getString(R.string.use_app_storage)) {
            Prefs.folder(this)?.let { u ->
                runCatching { contentResolver.releasePersistableUriPermission(Uri.parse(u),
                    Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_GRANT_WRITE_URI_PERMISSION) }
            }
            Prefs.setFolder(this, null); updateFolderLabel()
        })
        c.addView(btns)
        loc.hashCode()
        c.addView(textButton(getString(R.string.clear_all), danger = true) {
            AlertDialog.Builder(this)
                .setTitle(R.string.clear_all)
                .setMessage(getString(R.string.clear_all_msg, ClipStore.count()))
                .setPositiveButton(R.string.delete) { _, _ -> ClipStore.clearAll() }
                .setNegativeButton(android.R.string.cancel, null)
                .show()
        })

        // ColorOS + reset
        section(R.string.coloros_title)
        card().addView(text(getString(R.string.coloros_tips), 14f, R.color.text, add = false).apply {
            setPadding(dp(16), dp(14), dp(16), dp(14)); setLineSpacing(dp(4).toFloat(), 1f)
        })
        root.addView(textButton(getString(R.string.reset_all)) {
            AlertDialog.Builder(this)
                .setTitle(R.string.reset_all)
                .setMessage(R.string.reset_all_msg)
                .setPositiveButton(R.string.reset) { _, _ ->
                    Prefs.resetAll(this); build(); onResume(); handleChanged()
                }
                .setNegativeButton(android.R.string.cancel, null)
                .show()
        }.apply { (layoutParams as LinearLayout.LayoutParams).topMargin = dp(16) })
        text(getString(R.string.version, packageManager.getPackageInfo(packageName, 0).versionName), 12f, R.color.sub)
            .apply { gravity = Gravity.CENTER; setPadding(0, dp(8), 0, dp(32)) }
    }

    // ---------------- Preview ----------------

    private fun updatePreview() {
        if (!::preview.isInitialized) return
        preview.removeAllViews()
        val ctx = Style.themed(this)
        val col = LinearLayout(ctx).apply {
            orientation = LinearLayout.VERTICAL
            background = Style.panelBackground(ctx, true)
            setPadding(dp(6), dp(14), dp(6), 0)
        }
        val w = dp(Prefs.get(this, K.P_WIDTH)).coerceAtMost(resources.displayMetrics.widthPixels - dp(48))
        preview.addView(col, FrameLayout.LayoutParams(w, ViewGroup.LayoutParams.MATCH_PARENT, Gravity.END))
        val look = Look.from(this)
        val samples = listOf(
            "<span style=\"color:#FF6B6B\">\$Sample-tag 123</span>",
            "Hello,<br><br>I am writing about my order. It has not arrived yet and I would like an update.",
            "#4815162342",
        )
        val inflater = LayoutInflater.from(ctx)
        for (html in samples) {
            val v = inflater.inflate(R.layout.item_clip, col, false)
            col.addView(v)
            Style.applyItem(v, look)
            val clip = Clip(0, html, android.text.Html.fromHtml(html, 0).toString(), html, null, 0, false)
            v.findViewById<TextView>(R.id.clip_text).text = ClipAdapter.styled(clip, 400, look.sourceColors)
        }
    }

    private fun handleChanged() {
        if (EdgeService.running) EdgeService.start(this, EdgeService.ACTION_REFRESH)
    }

    // ---------------- Permissions ----------------

    private fun buildPermissions() {
        permCard.removeAllViews()
        perm(R.string.perm_overlay, R.string.perm_overlay_desc, Settings.canDrawOverlays(this)) { openOverlaySettings() }
        perm(R.string.perm_a11y, R.string.perm_a11y_desc, a11yOn()) {
            // Google Play requires a prominent disclosure and consent before this step.
            AlertDialog.Builder(this)
                .setTitle(R.string.a11y_disclosure_title)
                .setMessage(R.string.a11y_disclosure)
                .setPositiveButton(R.string.agree) { _, _ -> startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)) }
                .setNegativeButton(R.string.no_thanks, null)
                .show()
        }
        if (Build.VERSION.SDK_INT >= 33) {
            val ok = checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED
            perm(R.string.perm_notif, R.string.perm_notif_desc, ok) {
                requestPermissions(arrayOf(Manifest.permission.POST_NOTIFICATIONS), 1)
            }
        }
        val pm = getSystemService(PowerManager::class.java)
        perm(R.string.perm_battery, R.string.perm_battery_desc, pm.isIgnoringBatteryOptimizations(packageName)) {
            @Suppress("BatteryLife")
            startActivity(Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS, Uri.parse("package:$packageName")))
        }
    }

    private fun perm(title: Int, desc: Int, ok: Boolean, action: () -> Unit) {
        val v = LayoutInflater.from(this).inflate(R.layout.row_permission, permCard, false)
        v.findViewById<TextView>(R.id.row_title).setText(title)
        v.findViewById<TextView>(R.id.row_desc).setText(desc)
        val b = v.findViewById<Button>(R.id.row_button)
        if (ok) { b.visibility = View.GONE; v.findViewById<View>(R.id.row_status).visibility = View.VISIBLE }
        else b.setOnClickListener { action() }
        permCard.addView(v)
    }

    private fun a11yOn() = getSystemService(AccessibilityManager::class.java)
        .getEnabledAccessibilityServiceList(AccessibilityServiceInfo.FEEDBACK_ALL_MASK)
        .any { it.resolveInfo.serviceInfo.packageName == packageName }

    private fun openOverlaySettings() =
        startActivity(Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse("package:$packageName")))

    @Deprecated("Deprecated in Java")
    override fun onRequestPermissionsResult(code: Int, perms: Array<out String>, results: IntArray) {
        super.onRequestPermissionsResult(code, perms, results)
        buildPermissions()
    }

    // ---------------- Storage folder ----------------

    @Deprecated("Deprecated in Java")
    override fun onActivityResult(req: Int, res: Int, data: Intent?) {
        super.onActivityResult(req, res, data)
        val uri = data?.data
        if (req != REQ_FOLDER || res != RESULT_OK || uri == null) return
        runCatching {
            contentResolver.takePersistableUriPermission(uri,
                Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_GRANT_WRITE_URI_PERMISSION)
        }
        Prefs.setFolder(this, uri.toString())
        updateFolderLabel()
        ClipStore.syncFolder()
    }

    private fun updateFolderLabel() {
        val f = Prefs.folder(this)
        folderLabel.text = if (f == null) getString(R.string.app_storage) else {
            val id = runCatching { DocumentsContract.getTreeDocumentId(Uri.parse(f)) }.getOrDefault(f)
            getString(R.string.folder_named, id.substringAfter(':').ifEmpty { id })
        }
    }

    // ---------------- Small UI helpers ----------------

    private fun text(s: String, size: Float, color: Int, add: Boolean = true) = TextView(this).apply {
        text = s; textSize = size; setTextColor(getColor(color))
        if (add) root.addView(this)
    }

    private fun section(title: Int) {
        text(getString(title), 13f, R.color.sub).apply { setPadding(dp(16), dp(24), dp(16), dp(8)) }
    }

    private fun card() = LinearLayout(this).apply {
        orientation = LinearLayout.VERTICAL
        setBackgroundResource(R.drawable.bg_card)
        setPadding(0, dp(6), 0, dp(6))
        root.addView(this)
    }

    private fun row(parent: LinearLayout, title: Int, desc: Int): LinearLayout {
        val r = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; setPadding(dp(16), dp(10), dp(16), dp(4)) }
        r.addView(TextView(this).apply { setText(title); textSize = 16f; setTextColor(getColor(R.color.text)) })
        if (desc != 0) r.addView(TextView(this).apply { setText(desc); textSize = 13f; setTextColor(getColor(R.color.sub)) })
        parent.addView(r)
        return r
    }

    private fun slider(
        parent: LinearLayout, label: Int, k: K, min: Int, max: Int, unit: String,
        step: Int = 1, desc: Int = 0, onChange: (() -> Unit)? = null,
    ) {
        val head = LinearLayout(this).apply { setPadding(dp(16), dp(10), dp(16), 0); gravity = Gravity.CENTER_VERTICAL }
        head.addView(TextView(this).apply { setText(label); textSize = 16f; setTextColor(getColor(R.color.text)) },
            LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f))
        val value = TextView(this).apply { textSize = 14f; setTextColor(getColor(R.color.accent)) }
        head.addView(value)
        parent.addView(head)
        if (desc != 0) parent.addView(TextView(this).apply {
            setText(desc); textSize = 12f; setTextColor(getColor(R.color.sub)); setPadding(dp(16), 0, dp(16), 0)
        })
        val bar = SeekBar(this).apply { minimumHeight = dp(44); setPadding(dp(20), dp(8), dp(20), dp(8)) }
        parent.addView(bar)
        val show = { v: Int -> value.text = if (unit.isEmpty()) "$v" else "$v $unit" }
        val load = {
            val cur = Prefs.get(this, k).coerceIn(min, max)
            bar.max = (max - min) / step
            bar.progress = (cur - min) / step
            show(cur)
        }
        load()
        rebuilders += load
        bar.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(s: SeekBar, p: Int, fromUser: Boolean) {
                val v = min + p * step
                show(v)
                if (fromUser) { Prefs.set(this@MainActivity, k, v); onChange?.invoke() }
            }
            override fun onStartTrackingTouch(s: SeekBar) {}
            override fun onStopTrackingTouch(s: SeekBar) {}
        })
    }

    private fun toggle(parent: LinearLayout, label: Int, desc: Int, k: K, onChange: (() -> Unit)? = null) {
        val r = LinearLayout(this).apply { gravity = Gravity.CENTER_VERTICAL; setPadding(dp(16), dp(8), dp(12), dp(8)); minimumHeight = dp(56) }
        val texts = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
        texts.addView(TextView(this).apply { setText(label); textSize = 16f; setTextColor(getColor(R.color.text)) })
        if (desc != 0) texts.addView(TextView(this).apply { setText(desc); textSize = 13f; setTextColor(getColor(R.color.sub)) })
        r.addView(texts, LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f))
        val sw = Switch(this).apply {
            isChecked = Prefs.on(this@MainActivity, k)
            contentDescription = getString(label)
            setOnCheckedChangeListener { _, on -> Prefs.set(this@MainActivity, k, if (on) 1 else 0); onChange?.invoke() }
        }
        r.addView(sw)
        r.setOnClickListener { sw.toggle() }
        parent.addView(r)
    }

    private fun chips(parent: LinearLayout, label: Int, options: List<Int>, get: () -> Int, set: (Int) -> Unit) {
        row(parent, label, 0)
        val scroll = HorizontalScrollView(this).apply { isHorizontalScrollBarEnabled = false }
        val line = LinearLayout(this).apply { setPadding(dp(12), dp(4), dp(12), dp(10)) }
        scroll.addView(line)
        val views = options.mapIndexed { i, o ->
            TextView(this).apply {
                setText(o); textSize = 14f; gravity = Gravity.CENTER
                setBackgroundResource(R.drawable.bg_chip)
                setTextColor(getColorStateList(R.color.chip_text))
                minHeight = dp(40); setPadding(dp(16), 0, dp(16), 0)
                line.addView(this, LinearLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, dp(40)).apply { marginEnd = dp(8) })
                setOnClickListener { set(i); refreshChips(line, i) }
            }
        }
        refreshChips(line, get())
        views.size
        parent.addView(scroll)
    }

    private fun refreshChips(line: LinearLayout, sel: Int) {
        for (i in 0 until line.childCount) line.getChildAt(i).isSelected = i == sel
    }

    private fun swatches(parent: LinearLayout) {
        row(parent, R.string.handle_color, 0)
        val line = LinearLayout(this).apply { setPadding(dp(12), dp(4), dp(12), dp(10)) }
        val scroll = HorizontalScrollView(this).apply { isHorizontalScrollBarEnabled = false; addView(line) }
        Style.HANDLE_COLORS.forEachIndexed { i, col ->
            val v = View(this).apply {
                val fill = if (i == 0) getColor(R.color.handle) else col
                background = GradientDrawable().apply {
                    shape = GradientDrawable.OVAL; setColor(fill)
                    setStroke(dp(2), getColor(R.color.sub))
                }
                contentDescription = getString(R.string.color_n, i + 1)
                setOnClickListener {
                    Prefs.set(this@MainActivity, K.H_COLOR, i)
                    for (j in 0 until line.childCount) line.getChildAt(j).apply { scaleX = 1f; scaleY = 1f; alpha = 0.6f }
                    animate().scaleX(1.25f).scaleY(1.25f).alpha(1f).setDuration(150).start()
                    handleChanged()
                }
                val selected = i == Prefs.get(this@MainActivity, K.H_COLOR)
                scaleX = if (selected) 1.25f else 1f; scaleY = scaleX; alpha = if (selected) 1f else 0.6f
            }
            line.addView(v, LinearLayout.LayoutParams(dp(36), dp(36)).apply { marginEnd = dp(14); topMargin = dp(4); bottomMargin = dp(4) })
        }
        parent.addView(scroll)
    }

    private fun pillButton(label: String, onClick: () -> Unit) = Button(this, null, 0, R.style.PillButton).apply {
        text = label
        layoutParams = LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(48)).apply { setMargins(dp(12), dp(4), dp(12), dp(8)) }
        setOnClickListener { onClick() }
    }

    private fun textButton(label: String, danger: Boolean = false, onClick: () -> Unit) =
        Button(this, null, 0, android.R.style.Widget_Material_Button_Borderless).apply {
            text = label; isAllCaps = false; textSize = 15f
            setTextColor(getColor(if (danger) R.color.danger else R.color.accent))
            layoutParams = LinearLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, dp(48))
            setOnClickListener { onClick() }
        }

    companion object { private const val REQ_FOLDER = 7 }
}
