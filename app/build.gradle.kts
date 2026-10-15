plugins {
    id("com.android.application")
}

android {
    namespace = "com.rezz1dent.weatherbridge"
    compileSdk = 36

    defaultConfig {
        applicationId = "com.rezz1dent.weatherbridge"
        minSdk = 26
        targetSdk = 36
        versionCode = 14
        versionName = "2.2"
    }

    // Release signing key from the environment (GitHub secrets in CI); without it the release
    // build is signed with the debug key, so it still installs.
    val keystore = System.getenv("SIGNING_KEYSTORE")
    signingConfigs {
        if (keystore != null) {
            create("release") {
                storeFile = file(keystore)
                storePassword = System.getenv("SIGNING_STORE_PASSWORD")
                keyAlias = System.getenv("SIGNING_KEY_ALIAS")
                keyPassword = System.getenv("SIGNING_KEY_PASSWORD")
            }
        }
    }

    buildTypes {
        debug {
            versionNameSuffix = "-debug"
        }
        release {
            isMinifyEnabled = false
            signingConfig = signingConfigs.findByName("release") ?: signingConfigs.getByName("debug")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}
