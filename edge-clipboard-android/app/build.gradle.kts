import java.util.Properties

plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
}

// AdMob IDs: put admobAppId / admobBannerId in gradle.properties (user home) or as
// ORG_GRADLE_PROJECT_admobAppId / ORG_GRADLE_PROJECT_admobBannerId. Without them, Google's test IDs are used.
val admobAppId = (findProperty("admobAppId") as String?)?.takeIf { it.isNotBlank() }
    ?: "ca-app-pub-3940256099942544~3347511713"
val admobBannerId = (findProperty("admobBannerId") as String?)?.takeIf { it.isNotBlank() }
    ?: "ca-app-pub-3940256099942544/9214589741"

// Release signing: create keystore.properties next to settings.gradle.kts (never commit it).
val keystoreProps = Properties().apply {
    val f = rootProject.file("keystore.properties")
    if (f.exists()) f.inputStream().use { load(it) }
}

android {
    namespace = "com.edgeclip"
    compileSdk = 36

    defaultConfig {
        applicationId = "io.github.slinkybat123.edgeclip"
        minSdk = 26
        targetSdk = 36
        versionCode = 14
        versionName = "1.8.0"
        manifestPlaceholders["admobAppId"] = admobAppId
        buildConfigField("String", "ADMOB_BANNER_ID", "\"$admobBannerId\"")
    }

    signingConfigs {
        if (keystoreProps.isNotEmpty()) {
            create("release") {
                storeFile = rootProject.file(keystoreProps.getProperty("storeFile"))
                storePassword = keystoreProps.getProperty("storePassword")
                keyAlias = keystoreProps.getProperty("keyAlias")
                keyPassword = keystoreProps.getProperty("keyPassword")
            }
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
            if (keystoreProps.isNotEmpty()) signingConfig = signingConfigs.getByName("release")
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    buildFeatures { buildConfig = true }
}

kotlin {
    compilerOptions { jvmTarget.set(org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17) }
}

dependencies {
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.recyclerview)
    implementation(libs.androidx.dynamicanimation)
    implementation(libs.play.services.ads)
    implementation(libs.ump)
}
