# Publish Edge Clipboard on Google Play

Claude prepared the app, the store texts, the graphics, the privacy policy and a build workflow. You do the steps that need your own key and your own Google account. Do the steps in this order.

| Item | Value |
|---|---|
| App name | Edge Clipboard |
| Package ID | `io.github.slinkybat123.edgeclip` (permanent after the first upload) |
| Contact email | slinkybat123@gmail.com |
| Store texts | `store/listing.md` |
| Icon 512 × 512 | `store/icon-512.png` |
| Feature graphic 1024 × 500 | `store/feature-graphic.png` |
| Privacy policy | `docs/privacy.html` (repository root) |
| Build and upload workflow | `.github/workflows/edge-clipboard-release.yml` |

---

## Step 1. Create a Google Play developer account
1. Go to https://play.google.com/console/signup.
2. Select **Yourself** (personal account).
3. Pay the one-time USD 25 fee and complete identity verification. Verification can take a few days.

## Step 2. Create the upload key (one time — keep it safe)
If you lose this key or its password, you cannot update the app without a reset request to Google.

On Windows, install a JDK first if you do not have one: Eclipse Temurin 17 from https://adoptium.net. Install it to `E:\CLAUDE\Java\jdk-17`.

Open **Command Prompt** and run:
```
mkdir E:\CLAUDE\keys
"E:\CLAUDE\Java\jdk-17\bin\keytool" -genkeypair -v -keystore E:\CLAUDE\keys\edge-clipboard-upload.jks -keyalg RSA -keysize 2048 -validity 10000 -alias upload
```
- Enter a strong password two times. Write it down in your password manager.
- For name and organisation questions, you can type your name and press Enter for the rest.
- Make a backup copy of `edge-clipboard-upload.jks` (for example on a USB stick).

Never upload the `.jks` file or the password to GitHub as a file.

## Step 3. Build the signed bundle (.aab)
Choose **one** method.

### Method A — GitHub builds it (no Android Studio)
1. Merge branch `ccr-5689f8ec-uzuypg` into `main` (GitHub > Pull requests > New pull request > Merge). The build button shows only for workflows on `main`.
2. Convert the key to text. In **PowerShell**:
   ```
   [Convert]::ToBase64String([IO.File]::ReadAllBytes("E:\CLAUDE\keys\edge-clipboard-upload.jks")) | Set-Clipboard
   ```
3. GitHub > repository **Settings > Secrets and variables > Actions > New repository secret**. Add 4 secrets:
   | Name | Value |
   |---|---|
   | `KEYSTORE_BASE64` | Paste (the text from step 2) |
   | `KEYSTORE_PASSWORD` | Your key store password |
   | `KEY_ALIAS` | `upload` |
   | `KEY_PASSWORD` | Your key password (the same as the store password if you did not set another) |
4. GitHub > **Actions > Edge Clipboard release bundle > Run workflow**.
5. When the run is green, open it and download **edge-clipboard-release-aab**. Unzip it: you get `app-release.aab`.

### Method B — Build on your PC
1. Install Android Studio to `E:\CLAUDE\Android Studio`, with the SDK in `E:\CLAUDE\Android\Sdk`.
2. Open the folder `edge-clipboard-android`.
3. Create `keystore.properties` next to `settings.gradle.kts`:
   ```
   storeFile=E:/CLAUDE/keys/edge-clipboard-upload.jks
   storePassword=YOUR_PASSWORD
   keyAlias=upload
   keyPassword=YOUR_PASSWORD
   ```
4. In the Android Studio terminal: `gradlew bundleRelease`
5. Output: `app\build\outputs\bundle\release\app-release.aab`.

Before you upload, install the release build on your phone once (`gradlew installRelease` with USB debugging on) and check that everything works.

## Step 4. Create the app in Play Console
1. Play Console > **Create app**.
2. App name: **Edge Clipboard**. Default language: English (United States). App. Free.
3. Accept the declarations, then select **Create app**.

## Step 5. Privacy policy URL
The repository is public, so this link works after the merge in step 3A:
```
https://github.com/slinkybat123-code/viktor-mitic/blob/main/docs/privacy.html
```
A cleaner link with GitHub Pages: repository **Settings > Pages > Source: Deploy from a branch > main / docs > Save**. After a few minutes the policy is at:
```
https://slinkybat123-code.github.io/viktor-mitic/privacy.html
```
Enter the URL in Play Console > **Policy and programs > App content > Privacy policy**.

## Step 6. Take screenshots on your phone
Google needs 2 to 8 phone screenshots (real screens, not mock-ups). Take these:
1. The panel open over the home screen, with some clips.
2. The full clip view (tap a preview).
3. A clip with an image.
4. The settings screen with the live preview.
5. The handle on the edge, with the panel half open (swipe slowly and take the screenshot with the other hand, or use the power + volume down keys).

## Step 7. Store listing
Play Console > **Grow users > Store presence > Main store listing**. Copy the texts from `store/listing.md`. Upload `store/icon-512.png`, `store/feature-graphic.png` and the screenshots.

## Step 8. App content forms
Play Console > **Policy and programs > App content**. Use these answers:

**Ads:** **Yes, the app contains ads** (AdMob banner on the settings screen only). Play shows "Contains ads" on the listing.

**App access:** All functionality is available without special access.

**Content rating:** Start the questionnaire. Category: **Utility, Productivity, Communication, or Other**. Answer **No** to all content questions. The expected result is "Everyone / PEGI 3".

**Target audience:** 18 and over (this avoids the extra rules for apps for children).

**Data safety:**
The AdMob SDK collects data, so the answers are **Yes**. Clips and settings stay on the device and are not declared.
- Does your app collect or share any of the required user data types? **Yes.**
- Is all of the user data collected by your app encrypted in transit? **Yes.**
- Do you provide a way for users to request that their data is deleted? **No** (the app has no account; users reset the advertising ID in Android settings).
- Data types — select these, each **Collected and Shared**, purpose **Advertising or marketing** and **Analytics**, **not required to be optional** (processing is ephemeral: **No**):
  - **Device or other IDs** (advertising ID)
  - **Location > Approximate location** (from the IP address)
  - **App activity > App interactions** (ad taps and views)
  - **App info and performance > Crash logs** and **Diagnostics** (purpose: Analytics)
- Google's own guide for these answers: https://developers.google.com/admob/android/privacy/play-data-disclosure
- **Advertising ID declaration** (App content): **Yes**, the app uses the advertising ID, for **Advertising or marketing**.

**Government app:** No. **Financial features:** None. **Health:** No.

**Foreground service permissions:** Declare **Special use**. Text:
> The app shows a small floating handle on the screen edge that opens a clipboard history panel. When the user does not enable the accessibility service, a foreground service keeps this handle visible. The user can stop it from the notification or the app.

Video: record the handle and panel in use (see the accessibility video below; the same video is fine).

**Accessibility API (important — most review problems are here):** Play Console asks for this when you upload the bundle. Answers:
- Is the app an accessibility tool? **No.**
- Description of use:
> Edge Clipboard uses the AccessibilityService API for its core function. It detects copy actions (a tap on "Copy" or a "Copied" message) so it can save the clipboard text at that moment, and it shows the edge handle and the clipboard panel as an accessibility overlay. The service does not read screen content (canRetrieveWindowContent is false), does not record keystrokes, and sends no data off the device. Before the user is sent to the accessibility settings, the app shows a prominent disclosure and asks for consent.
- Video (required): record your phone screen for about 30–60 seconds:
  1. Open the app and select **Turn on** for Copy detection.
  2. Show the disclosure dialog and select **Agree**.
  3. Turn on the service in Accessibility settings.
  4. Copy text in another app, swipe out the panel, and show the new clip.
  Upload it to YouTube as **Unlisted** and paste the link.

## Step 9. Closed test (required for new personal accounts)
New personal developer accounts must run a closed test with **at least 12 testers for at least 14 days** before they can publish to production.
1. Play Console > **Test and release > Testing > Closed testing > Create track**.
2. Add testers by email list (friends and family with Android phones).
3. **Create new release**, upload `app-release.aab`, and roll it out.
4. Send the opt-in link to the testers. They must install and keep the app for 14 days.
5. After 14 days, select **Apply for production** and answer the questions.

## Step 10. Production
After Google approves production access: **Production > Create new release**, upload the same or a newer bundle, and roll it out. The first review can take several days.

## Step 11 (optional). Upload from GitHub with one click
After the first release exists in Play Console (the first bundle must be uploaded by hand, step 9), GitHub can upload new versions for you.
1. Play Console > **Setup > API access**. Link a Google Cloud project (create one if asked).
2. Select **Create new service account** and follow the link to Google Cloud. Create the account, then **Keys > Add key > JSON**. A `.json` file downloads. Store it in `E:\CLAUDE\keys` and never put it in the repository.
3. Back in Play Console: **Users and permissions > Invite new users**. Paste the service account email. Under **App permissions**, add Edge Clipboard with **Release apps to testing tracks** (and **Release to production** if you want).
4. GitHub > **Settings > Secrets and variables > Actions > New repository secret**: name `PLAY_SERVICE_ACCOUNT_JSON`, value = the full text of the `.json` file.
5. To release: increase `versionCode`, push to `main`, then **Actions > Edge Clipboard release bundle > Run workflow**. Select the track (`internal`, `alpha` = closed test, `beta`, `production`) and the status (`draft` lets you check it in Play Console first; `completed` rolls it out at once).

## Step 12. Ads with AdMob (real ads)
The app shows Google's **test ads** until you add your own IDs. Do not tap your own real ads: AdMob can close your account for that.
1. Make an AdMob account: https://admob.google.com (sign in with the same Google account as Play Console). Add your payment and tax details.
2. **Apps > Add app > Android**. When asked if the app is on Google Play: select **No** first (you can link it after it is published). Name: Edge Clipboard.
3. Copy the **App ID** (`ca-app-pub-…~…`).
4. **Ad units > Add ad unit > Banner**. Name: Settings banner. Copy the **Ad unit ID** (`ca-app-pub-…/…`).
5. GitHub > **Settings > Secrets and variables > Actions**: add `ADMOB_APP_ID` and `ADMOB_BANNER_ID` with those values. The release workflow then builds with your real IDs. (For a PC build, add `admobAppId=…` and `admobBannerId=…` to `C:\Users\<you>\.gradle\gradle.properties`.)
6. **Privacy & messaging > GDPR**: create a consent message for the app and publish it. The app already shows it in the EEA, UK and Switzerland. Do the same for **US state regulations** if you want ads in those states.
7. **app-ads.txt** (AdMob asks for it to pay full rates): AdMob shows one line under **Apps > View all apps > app-ads.txt**. It must be at the root of the website in your Play listing.
   - Easiest: create a new public GitHub repository named `slinkybat123-code.github.io`, add a file `app-ads.txt` with that line, and turn on Pages for it. Then set the Play listing website to `https://slinkybat123-code.github.io`.
8. After Play publishes the app: AdMob > App settings > **Link to app store**.

## Step 13. Website and APK download
The website is `docs/index.html` (download page) and `docs/privacy.html`.
1. Merge pull request #1, then **Settings > Pages > Deploy from a branch > main / docs**. The site goes live at `https://slinkybat123-code.github.io/viktor-mitic/`.
2. To publish a signed APK for the **Download APK** button: after the 4 key secrets are in place (step 3), create a tag and push it, for example in GitHub > **Releases > Draft a new release > Choose a tag: `edge-clipboard-v1.8.0` > Create new tag > Publish release**. The workflow builds `EdgeClipboard.apk` and attaches it to that release.
   (If you publish the release by hand first, the workflow adds the APK to it.)
3. A phone with the test (debug) APK must uninstall it once before it can install the signed APK, because the signatures are different.

## Each update
1. Increase `versionCode` (for example 6 → 7) and `versionName` in `app/build.gradle.kts`.
2. Build a new bundle (step 3) and upload it to a new release.

## Common rejection reasons — and how this app avoids them
| Reason | Status |
|---|---|
| Trademark in name or icon | Fixed: neutral name "Edge Clipboard" and an original icon. Do not add other brand names to the texts. |
| Accessibility API without disclosure | The disclosure and consent dialog is built in. Show it in the video. |
| Missing privacy policy | `docs/privacy.html`, step 5. |
| Old target SDK | Targets API 36. |
