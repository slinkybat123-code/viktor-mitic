package com.edgeclip

import android.app.Activity
import android.widget.FrameLayout
import com.google.android.gms.ads.AdRequest
import com.google.android.gms.ads.AdSize
import com.google.android.gms.ads.AdView
import com.google.android.gms.ads.MobileAds
import com.google.android.ump.ConsentInformation
import com.google.android.ump.ConsentRequestParameters
import com.google.android.ump.UserMessagingPlatform
import java.util.concurrent.atomic.AtomicBoolean

/**
 * One adaptive banner at the bottom of the Settings screen only. No ads in the edge handle or
 * the clipboard panel (AdMob does not allow ads in overlays over other apps).
 * Asks for consent first where the law requires it (EEA, UK, Switzerland, some US states).
 */
object Ads {
    private val started = AtomicBoolean(false)

    fun consent(a: Activity): ConsentInformation = UserMessagingPlatform.getConsentInformation(a)

    /** Requests consent if needed, then shows the banner in [container]. Returns the AdView, or null. */
    fun setup(a: Activity, container: FrameLayout, onReady: (AdView?) -> Unit) {
        val info = consent(a)
        info.requestConsentInfoUpdate(a, ConsentRequestParameters.Builder().build(), {
            UserMessagingPlatform.loadAndShowConsentFormIfRequired(a) {
                if (info.canRequestAds()) onReady(load(a, container))
            }
        }, {
            // Consent server not reachable: use the last answer, if there is one.
            if (info.canRequestAds()) onReady(load(a, container))
        })
        if (info.canRequestAds()) onReady(load(a, container))
    }

    private fun load(a: Activity, container: FrameLayout): AdView? {
        if (a.isFinishing || a.isDestroyed) return null
        if (container.childCount > 0) return container.getChildAt(0) as? AdView
        if (started.compareAndSet(false, true)) MobileAds.initialize(a.applicationContext) {}
        val widthDp = (a.resources.displayMetrics.widthPixels / a.resources.displayMetrics.density).toInt()
        val ad = AdView(a).apply {
            adUnitId = BuildConfig.ADMOB_BANNER_ID
            setAdSize(AdSize.getCurrentOrientationAnchoredAdaptiveBannerAdSize(a, widthDp))
        }
        container.addView(ad)
        ad.loadAd(AdRequest.Builder().build())
        return ad
    }

    fun privacyOptionsRequired(a: Activity) =
        consent(a).privacyOptionsRequirementStatus == ConsentInformation.PrivacyOptionsRequirementStatus.REQUIRED

    fun showPrivacyOptions(a: Activity) = UserMessagingPlatform.showPrivacyOptionsForm(a) {}
}
