# Publishing to Google Play

I (Claude) did not sign or upload the app. You do the steps below yourself, because they need your signing key and your developer account.

## 0. App name and trademark — read first
"One UI" is a Samsung trademark. Google Play can reject or remove an app whose name or icon uses another company's trademark (Impersonation and Intellectual Property policies). Samsung can also send a takedown.
- Safe option: publish under a neutral name, for example "Edge Clip — Clipboard Panel", and describe it as "in the style of the Samsung edge panel" only in the description, not in the name or icon.
- To change the name: edit `app_name` in `app/src/main/res/values/strings.xml`.

## 1. Change the package name (recommended)
`com.edgeclip` can be taken. In `app/build.gradle.kts`, change `applicationId` to a name you own, for example `com.<yourname>.edgeclip`. You cannot change it after the first upload.

## 2. Create the upload key (one time — keep it safe)
```
keytool -genkeypair -v -keystore upload.jks -keyalg RSA -keysize 2048 -validity 10000 -alias upload
```
Put `upload.jks` in a safe place (not in Git). Create `keystore.properties` next to `settings.gradle.kts`:
```
storeFile=E:/CLAUDE/keys/upload.jks
storePassword=...
keyAlias=upload
keyPassword=...
```
`keystore.properties` and `*.jks` are in `.gitignore`.

## 3. Build the App Bundle
```
gradlew bundleRelease
```
Output: `app/build/outputs/bundle/release/app-release.aab`. Install the release on your phone once before upload (`gradlew installRelease`) to check that R8 shrinking did not break anything.

## 4. Play Console
1. Create the app. Pay the one-time $25 developer fee if you have no account.
2. **Privacy policy:** host `PRIVACY.md` on a public page (for example GitHub Pages) and enter the URL.
3. **Data safety:** "No data collected" and "No data shared" (all data stays on the device and the app has no internet permission).
4. **App access:** say that no login is necessary.
5. **Permissions declarations:**
   - **Accessibility API:** declare the use. Say it detects copy actions to save clipboard history, it is not an accessibility tool, and the app shows a disclosure and asks for consent first (already built in). Upload a short video of the disclosure and the feature.
   - **Foreground service (special use):** say it keeps the floating edge handle visible so the user can open clipboard history at any time.
   - **Display over other apps:** no form, but say it in the description.
6. **Store listing:** short description, full description, icon 512 × 512, feature graphic 1024 × 500, at least 2 phone screenshots.
7. **Testing:** new personal developer accounts must run a closed test with at least 12 testers for 14 days before production.
8. Upload the `.aab` to the testing track, then to production.

## 5. Each update
Increase `versionCode` (and `versionName`) in `app/build.gradle.kts`, then build and upload a new bundle.
