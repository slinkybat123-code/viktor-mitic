package com.edgeclip

import android.content.Context
import android.net.Uri
import android.provider.DocumentsContract
import java.io.File

/** Keeps a copy of clips.json and the clip images in a folder the user picked (Storage Access Framework). */
object FolderMirror {
    private val IMAGE = Regex("^\\d+\\.(png|jpg|gif|webp)$")

    /** Call on a background thread. */
    fun sync(c: Context, json: String, imageDir: File, images: Set<String>) {
        val tree = Prefs.folder(c)?.let(Uri::parse) ?: return
        runCatching {
            val cr = c.contentResolver
            val rootId = DocumentsContract.getTreeDocumentId(tree)
            val dir = DocumentsContract.buildDocumentUriUsingTree(tree, rootId)
            val children = DocumentsContract.buildChildDocumentsUriUsingTree(tree, rootId)
            val existing = HashMap<String, Uri>()
            cr.query(children, arrayOf(DocumentsContract.Document.COLUMN_DOCUMENT_ID,
                DocumentsContract.Document.COLUMN_DISPLAY_NAME), null, null, null)?.use { q ->
                while (q.moveToNext()) existing[q.getString(1)] = DocumentsContract.buildDocumentUriUsingTree(tree, q.getString(0))
            }
            val jsonUri = existing["clips.json"]
                ?: DocumentsContract.createDocument(cr, dir, "application/json", "clips.json")
            jsonUri?.let { u -> cr.openOutputStream(u, "wt")?.use { it.write(json.toByteArray()) } }

            for (name in images) if (name !in existing) {
                val f = File(imageDir, name)
                if (!f.exists()) continue
                val mime = "image/" + name.substringAfterLast('.').replace("jpg", "jpeg")
                DocumentsContract.createDocument(cr, dir, mime, name)?.let { u ->
                    cr.openOutputStream(u, "wt")?.use { out -> f.inputStream().use { it.copyTo(out) } }
                }
            }
            for ((name, uri) in existing) if (IMAGE.matches(name) && name !in images) {
                DocumentsContract.deleteDocument(cr, uri)
            }
        }
    }
}
