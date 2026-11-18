package com.example.thesis_navigation

import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel
import android.app.Activity
import android.content.Intent
import android.content.Context
import android.media.AudioAttributes
import android.os.Build
import android.os.VibrationEffect
import android.os.VibrationAttributes
import android.os.Vibrator
import android.os.VibratorManager

class MainActivity : FlutterActivity() {
    private data class PendingExport(val csv: String, val reply: MethodChannel.Result)
    private var pendingExport: PendingExport? = null
    private val exportRequest = 4487

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        if (requestCode != exportRequest) {
            super.onActivityResult(requestCode, resultCode, data)
            return
        }
        val export = pendingExport ?: return
        pendingExport = null
        if (resultCode != Activity.RESULT_OK) {
            export.reply.success(false)
            return
        }
        val uri = data?.data
        if (uri == null) {
            export.reply.error("NO_DESTINATION", "Missing document destination", null)
            return
        }
        Thread {
            try {
                val stream = contentResolver.openOutputStream(uri, "wt")
                    ?: throw java.io.IOException("Cannot open document")
                stream.bufferedWriter(Charsets.UTF_8).use { it.write(export.csv) }
                runOnUiThread { export.reply.success(true) }
            } catch (error: Exception) {
                runOnUiThread { export.reply.error("WRITE_FAILED", "Could not write CSV", null) }
            }
        }.start()
    }

    @Suppress("DEPRECATION")
    private fun pulseDetectionUpdate(vibrator: Vibrator) {
        // Detection cues assist awareness; they are not touch/button feedback.
        // Explicit usage respects accessibility vibration settings. Do not set
        // bypass flags or change system-wide touch/DND preferences.
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            vibrator.vibrate(
                VibrationEffect.createOneShot(120L, VibrationEffect.DEFAULT_AMPLITUDE),
                VibrationAttributes.Builder().setUsage(VibrationAttributes.USAGE_ACCESSIBILITY).build()
            )
        } else {
            val attributes = AudioAttributes.Builder()
                .setUsage(AudioAttributes.USAGE_ASSISTANCE_ACCESSIBILITY)
                .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                .build()
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                vibrator.vibrate(VibrationEffect.createOneShot(120L, VibrationEffect.DEFAULT_AMPLITUDE), attributes)
            } else {
                vibrator.vibrate(120L, attributes)
            }
        }
    }

    @Suppress("DEPRECATION")
    private fun deviceVibrator(): Vibrator? =
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            (getSystemService(Context.VIBRATOR_MANAGER_SERVICE) as? VibratorManager)?.defaultVibrator
        } else {
            getSystemService(Context.VIBRATOR_SERVICE) as? Vibrator
        }

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, "path/hazard_export")
            .setMethodCallHandler { call, result ->
                val csv = call.argument<String>("csv")
                when {
                    call.method != "saveCsv" -> result.notImplemented()
                    pendingExport != null -> result.error("BUSY", "Export already open", null)
                    csv == null -> result.error("NO_DATA", "Missing CSV content", null)
                    else -> {
                        pendingExport = PendingExport(csv, result)
                        try {
                            val intent = Intent(Intent.ACTION_CREATE_DOCUMENT).apply {
                                addCategory(Intent.CATEGORY_OPENABLE)
                                type = "text/csv"
                                putExtra(Intent.EXTRA_TITLE, call.argument<String>("name"))
                            }
                            startActivityForResult(intent, exportRequest)
                        } catch (error: Exception) {
                            pendingExport = null
                            result.error("NO_PICKER", "Could not open document picker", null)
                        }
                    }
                }
            }
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, "path/haptics")
            .setMethodCallHandler { call, result ->
                try {
                    val vibrator = deviceVibrator()
                    when (call.method) {
                        "hasVibrator" -> result.success(vibrator?.hasVibrator() == true)
                        "pulse" -> {
                            if (vibrator?.hasVibrator() != true) {
                                result.success(false)
                            } else {
                                // One neutral 120 ms pulse; never repeating or severity-coded.
                                pulseDetectionUpdate(vibrator)
                                result.success(true)
                            }
                        }
                        "cancel" -> { vibrator?.cancel(); result.success(null) }
                        else -> result.notImplemented()
                    }
                } catch (error: Exception) {
                    result.error("HAPTICS_UNAVAILABLE", "Vibration could not be used", null)
                }
            }
    }

    override fun onPause() {
        runCatching { deviceVibrator()?.cancel() }
        super.onPause()
    }

    override fun onDestroy() {
        pendingExport?.reply?.success(false)
        pendingExport = null
        runCatching { deviceVibrator()?.cancel() }
        super.onDestroy()
    }
}
