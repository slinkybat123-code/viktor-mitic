package com.edgeclip

import android.Manifest
import android.accessibilityservice.AccessibilityServiceInfo
import android.app.Activity
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.PowerManager
import android.provider.Settings
import android.view.LayoutInflater
import android.view.View
import android.view.accessibility.AccessibilityManager
import android.widget.Button
import android.widget.LinearLayout
import android.widget.SeekBar
import android.widget.Switch
import android.widget.TextView

class MainActivity : Activity() {

    private lateinit var rows: LinearLayout
    private lateinit var toggle: Switch

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        ClipStore.init(this)
        rows = findViewById(R.id.permission_rows)
        toggle = findViewById(R.id.toggle)

        toggle.setOnCheckedChangeListener { _, on ->
            if (on && !Settings.canDrawOverlays(this)) {
                toggle.isChecked = false
                openOverlaySettings()
                return@setOnCheckedChangeListener
            }
            Prefs.setEnabled(this, on)
            if (on) EdgeService.start(this) else EdgeService.stop(this)
        }

        slider(R.id.width_bar, R.id.width_value, 3, 16, Prefs.widthDp(this), "dp") { Prefs.setWidthDp(this, it) }
        slider(R.id.height_bar, R.id.height_value, 40, 160, Prefs.heightDp(this), "dp") { Prefs.setHeightDp(this, it) }
        slider(R.id.alpha_bar, R.id.alpha_value, 20, 100, Prefs.alpha(this), "%") { Prefs.setAlpha(this, it) }

        findViewById<Button>(R.id.open_panel).setOnClickListener {
            if (Settings.canDrawOverlays(this)) {
                Prefs.setEnabled(this, true)
                EdgeService.start(this, EdgeService.ACTION_OPEN)
                moveTaskToBack(true)
            } else openOverlaySettings()
        }
        findViewById<Button>(R.id.reset_size).setOnClickListener {
            Prefs.setWidthDp(this, 7); Prefs.setHeightDp(this, 72); Prefs.setAlpha(this, 65)
            recreate()
            refreshHandle()
        }
    }

    override fun onResume() {
        super.onResume()
        toggle.isChecked = Prefs.enabled(this) && Settings.canDrawOverlays(this)
        if (toggle.isChecked && !EdgeService.running) EdgeService.start(this)
        buildRows()
    }

    private fun slider(barId: Int, valueId: Int, min: Int, maxV: Int, cur: Int, unit: String, save: (Int) -> Unit) {
        val bar = findViewById<SeekBar>(barId)
        val label = findViewById<TextView>(valueId)
        bar.max = maxV - min
        bar.progress = cur - min
        label.text = "$cur $unit"
        bar.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(s: SeekBar, p: Int, fromUser: Boolean) {
                label.text = "${p + min} $unit"
                if (fromUser) { save(p + min); refreshHandle() }
            }
            override fun onStartTrackingTouch(s: SeekBar) {}
            override fun onStopTrackingTouch(s: SeekBar) {}
        })
    }

    private fun refreshHandle() {
        if (EdgeService.running) EdgeService.start(this, EdgeService.ACTION_REFRESH)
    }

    private fun buildRows() {
        rows.removeAllViews()
        row(R.string.perm_overlay, R.string.perm_overlay_desc, Settings.canDrawOverlays(this)) { openOverlaySettings() }
        row(R.string.perm_a11y, R.string.perm_a11y_desc, a11yOn()) {
            startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS))
        }
        if (Build.VERSION.SDK_INT >= 33) {
            val granted = checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED
            row(R.string.perm_notif, R.string.perm_notif_desc, granted) {
                requestPermissions(arrayOf(Manifest.permission.POST_NOTIFICATIONS), 1)
            }
        }
        val pm = getSystemService(PowerManager::class.java)
        row(R.string.perm_battery, R.string.perm_battery_desc, pm.isIgnoringBatteryOptimizations(packageName)) {
            @Suppress("BatteryLife")
            startActivity(
                Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS, Uri.parse("package:$packageName"))
            )
        }
    }

    private fun row(title: Int, desc: Int, ok: Boolean, action: () -> Unit) {
        val v = LayoutInflater.from(this).inflate(R.layout.row_permission, rows, false)
        v.findViewById<TextView>(R.id.row_title).setText(title)
        v.findViewById<TextView>(R.id.row_desc).setText(desc)
        val b = v.findViewById<Button>(R.id.row_button)
        val s = v.findViewById<TextView>(R.id.row_status)
        if (ok) {
            b.visibility = View.GONE
            s.visibility = View.VISIBLE
        } else {
            b.setOnClickListener { action() }
        }
        rows.addView(v)
    }

    private fun a11yOn(): Boolean {
        val am = getSystemService(AccessibilityManager::class.java)
        return am.getEnabledAccessibilityServiceList(AccessibilityServiceInfo.FEEDBACK_ALL_MASK)
            .any { it.resolveInfo.serviceInfo.packageName == packageName }
    }

    private fun openOverlaySettings() {
        startActivity(Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse("package:$packageName")))
    }

    @Deprecated("Deprecated in Java")
    override fun onRequestPermissionsResult(code: Int, perms: Array<out String>, results: IntArray) {
        super.onRequestPermissionsResult(code, perms, results)
        buildRows()
    }
}
