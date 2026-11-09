import 'package:flutter/material.dart';

import 'detector.dart';

const pathYellow = Color(0xFFFFD700);
const pathSurface = Color(0xFF121212);

ThemeData buildPathTheme() => ThemeData(
  useMaterial3: true,
  fontFamily: 'Inter',
  colorScheme: const ColorScheme.dark(
    primary: pathYellow,
    onPrimary: Colors.black,
    surface: pathSurface,
    onSurface: Colors.white,
  ),
  scaffoldBackgroundColor: Colors.black,
  filledButtonTheme: FilledButtonThemeData(
    style: FilledButton.styleFrom(
      minimumSize: const Size.fromHeight(64),
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 20),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      textStyle: const TextStyle(
        fontFamily: 'Inter',
        fontSize: 18,
        fontWeight: FontWeight.w700,
      ),
    ),
  ),
);

enum SessionPhase { idle, starting, live, stopping }

/// Presentation only. Camera resources and inference stay in SessionScreen.
class SessionView extends StatelessWidget {
  const SessionView({
    super.key,
    required this.phase,
    required this.onToggle,
    this.preview,
    this.detections = const [],
    this.processedFrames = 0,
    this.elapsedMs,
    this.error,
    this.onOpenSettings,
    this.onOpenLog,
  });

  final SessionPhase phase;
  final VoidCallback onToggle;
  final Widget? preview;
  final List<Detection> detections;
  final int processedFrames;
  final int? elapsedMs;
  final String? error;
  final VoidCallback? onOpenSettings;
  final VoidCallback? onOpenLog;

  @override
  Widget build(BuildContext context) {
    final active = phase == SessionPhase.live;
    final busy =
        phase == SessionPhase.starting || phase == SessionPhase.stopping;
    final label = switch (phase) {
      SessionPhase.idle => 'Start camera session',
      SessionPhase.starting => 'Starting camera…',
      SessionPhase.live => 'Stop session',
      SessionPhase.stopping => 'Stopping…',
    };
    return Scaffold(
      body: SafeArea(
        child: LayoutBuilder(
          builder: (context, constraints) {
            final scale = MediaQuery.textScalerOf(context).scale(18) / 18;
            final cameraHeight =
                (constraints.maxHeight -
                        (430 +
                                (onOpenSettings != null ? 44 : 0) +
                                (error != null ? 120 : 0)) *
                            scale)
                    .clamp(220.0, 640.0);
            return SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  _PathHeader(
                    active: active,
                    onOpenSettings: onOpenSettings,
                    onOpenLog: onOpenLog,
                  ),
                  const SizedBox(height: 24),
                  DecoratedBox(
                    decoration: BoxDecoration(
                      color: pathSurface,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(
                        color: const Color(0xFFFF3366),
                        width: 3,
                      ),
                    ),
                    child: ConstrainedBox(
                      constraints: const BoxConstraints(minHeight: 116),
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Row(
                          children: [
                            ExcludeSemantics(
                              child: Image.asset(
                                'assets/figma/audio-lines.png',
                                width: 28,
                                height: 28,
                                cacheWidth: 84,
                              ),
                            ),
                            const SizedBox(width: 16),
                            const Expanded(
                              child: Text(
                                'Alerts in development',
                                style: TextStyle(
                                  fontSize: 28,
                                  height: 1.15,
                                  fontWeight: FontWeight.w700,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  SizedBox(
                    height: cameraHeight,
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(12),
                      child: ColoredBox(
                        color: pathSurface,
                        child: Column(
                          children: [
                            Expanded(
                              child: Stack(
                                fit: StackFit.expand,
                                children: [
                                  if (active && preview != null)
                                    Semantics(
                                      container: true,
                                      label: detections.isEmpty
                                          ? 'No object detected in this frame. Path condition is unknown.'
                                          : detections
                                                .map(
                                                  (d) =>
                                                      '${d.label}, ${d.direction}, ${(d.score * 100).round()} percent confidence',
                                                )
                                                .join('; '),
                                      child: RepaintBoundary(child: preview!),
                                    )
                                  else
                                    Center(
                                      child: Column(
                                        mainAxisSize: MainAxisSize.min,
                                        children: [
                                          ExcludeSemantics(
                                            child: Icon(
                                              busy
                                                  ? Icons.hourglass_empty
                                                  : Icons.videocam_off_outlined,
                                              size: 48,
                                              color: const Color(0xFFBDBDBD),
                                            ),
                                          ),
                                          const SizedBox(height: 12),
                                          Text(
                                            switch (phase) {
                                              SessionPhase.idle =>
                                                'Camera is off',
                                              SessionPhase.starting =>
                                                'Preparing camera',
                                              SessionPhase.live =>
                                                'Detection is live',
                                              SessionPhase.stopping =>
                                                'Ending session',
                                            },
                                            style: const TextStyle(
                                              fontSize: 18,
                                              fontWeight: FontWeight.w700,
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                  Positioned(
                                    top: 12,
                                    left: 12,
                                    right: 12,
                                    child: ExcludeSemantics(
                                      child: Row(
                                        mainAxisAlignment:
                                            MainAxisAlignment.spaceBetween,
                                        children: [
                                          for (final zone in [
                                            'LEFT',
                                            'CENTER',
                                            'RIGHT',
                                          ])
                                            DecoratedBox(
                                              decoration: BoxDecoration(
                                                color: Colors.black,
                                                borderRadius:
                                                    BorderRadius.circular(4),
                                              ),
                                              child: Padding(
                                                padding:
                                                    const EdgeInsets.symmetric(
                                                      horizontal: 8,
                                                      vertical: 6,
                                                    ),
                                                child: Text(
                                                  zone,
                                                  textScaler:
                                                      TextScaler.noScaling,
                                                  style: const TextStyle(
                                                    fontSize: 14,
                                                  ),
                                                ),
                                              ),
                                            ),
                                        ],
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            TextButton.icon(
                              key: const ValueKey('session-toggle'),
                              onPressed: busy ? null : onToggle,
                              style: TextButton.styleFrom(
                                minimumSize: const Size.fromHeight(64),
                                foregroundColor: pathYellow,
                                textStyle: const TextStyle(
                                  fontFamily: 'Inter',
                                  fontSize: 16,
                                  fontWeight: FontWeight.w700,
                                ),
                              ),
                              icon: Icon(
                                active ? Icons.stop : Icons.play_arrow,
                              ),
                              label: Text(label, textAlign: TextAlign.center),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                  if (error != null) ...[
                    const SizedBox(height: 16),
                    Semantics(
                      liveRegion: true,
                      child: _InfoPanel(text: error!, error: true),
                    ),
                  ],
                  const SizedBox(height: 16),
                  const _FeedbackControls(),
                ],
              ),
            );
          },
        ),
      ),
    );
  }
}

class _FeedbackControls extends StatelessWidget {
  const _FeedbackControls();

  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.stretch,
    children: [
      LayoutBuilder(
        builder: (context, constraints) {
          const mute = _DevelopmentButton(
            label: 'Mute audio',
            description: 'Audio alerts and mute controls are in development.',
          );
          const haptics = _DevelopmentButton(
            label: 'Haptics on',
            description:
                'Haptic feedback and its on/off control are in development.',
          );
          if (MediaQuery.textScalerOf(context).scale(18) > 27) {
            return const Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [mute, SizedBox(height: 16), haptics],
            );
          }
          return const Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(child: mute),
              SizedBox(width: 16),
              Expanded(child: haptics),
            ],
          );
        },
      ),
      const SizedBox(height: 16),
      const _DevelopmentButton(
        label: 'Repeat last alert',
        description: 'Spoken alerts and repeat playback are in development.',
        repeat: true,
      ),
    ],
  );
}

class _DevelopmentButton extends StatelessWidget {
  const _DevelopmentButton({
    required this.label,
    required this.description,
    this.repeat = false,
  });

  final String label;
  final String description;
  final bool repeat;

  @override
  Widget build(BuildContext context) {
    final child = Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            if (repeat) ...[
              ExcludeSemantics(
                child: Image.asset(
                  'assets/figma/volume.png',
                  width: 24,
                  height: 24,
                  cacheWidth: 72,
                  color: Colors.black,
                ),
              ),
              const SizedBox(width: 8),
            ],
            Flexible(
              child: Text(
                label.toUpperCase(),
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontFamily: 'Inter',
                  fontSize: 16,
                  height: 1.15,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 4),
        Text(
          'In development',
          textAlign: TextAlign.center,
          style: TextStyle(
            fontFamily: 'Inter',
            fontSize: 12,
            color: repeat ? Colors.black : const Color(0xFFBDBDBD),
          ),
        ),
      ],
    );
    void showDevelopment() => showDialog<void>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('$label — In development'),
        content: Text(description),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            style: TextButton.styleFrom(minimumSize: const Size(64, 64)),
            child: const Text('Close'),
          ),
        ],
      ),
    );
    if (repeat) {
      return FilledButton(
        onPressed: showDevelopment,
        style: FilledButton.styleFrom(
          minimumSize: const Size.fromHeight(64),
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        ),
        child: child,
      );
    }
    return OutlinedButton(
      onPressed: showDevelopment,
      style: OutlinedButton.styleFrom(
        foregroundColor: Colors.white,
        minimumSize: const Size.fromHeight(64),
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
        side: const BorderSide(color: Color(0xFFB3B3B3), width: 2),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      ),
      child: child,
    );
  }
}

class _PathHeader extends StatelessWidget {
  const _PathHeader({
    required this.active,
    this.onOpenSettings,
    this.onOpenLog,
  });
  final bool active;
  final VoidCallback? onOpenSettings;
  final VoidCallback? onOpenLog;

  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.stretch,
    children: [
      Row(
        children: [
          ExcludeSemantics(
            child: Image.asset(
              'assets/figma/cpu.png',
              width: 20,
              height: 20,
              cacheWidth: 60,
              color: pathYellow,
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              active ? 'OFFLINE EDGE AI ACTIVE' : 'OFFLINE EDGE AI',
              style: const TextStyle(
                color: pathYellow,
                fontSize: 16,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
          if (onOpenSettings != null || onOpenLog != null)
            SizedBox(
              width: 64,
              height: 64,
              child: PopupMenuButton<String>(
                tooltip: 'Open navigation menu',
                icon: const Icon(Icons.more_vert, color: pathYellow),
                onSelected: (value) {
                  if (value == 'settings') onOpenSettings?.call();
                  if (value == 'log') onOpenLog?.call();
                },
                itemBuilder: (context) => [
                  if (onOpenSettings != null)
                    const PopupMenuItem(
                      height: 64,
                      value: 'settings',
                      child: Text('Settings & Accessibility'),
                    ),
                  if (onOpenLog != null)
                    const PopupMenuItem(
                      height: 64,
                      value: 'log',
                      child: Text('Hazard Log & GPS'),
                    ),
                ],
              ),
            ),
        ],
      ),
      const SizedBox(height: 12),
      Wrap(
        alignment: WrapAlignment.spaceBetween,
        spacing: 12,
        runSpacing: 8,
        children: [
          Text(
            active ? 'PATH / LIVE' : 'PATH / IDLE',
            style: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w700,
              letterSpacing: 1,
              color: Color(0xFFBDBDBD),
            ),
          ),
          const Text(
            'GPS · In development',
            style: TextStyle(fontSize: 12, color: Color(0xFFBDBDBD)),
          ),
        ],
      ),
    ],
  );
}

class _InfoPanel extends StatelessWidget {
  const _InfoPanel({required this.text, this.error = false});
  final String text;
  final bool error;

  @override
  Widget build(BuildContext context) => DecoratedBox(
    decoration: BoxDecoration(
      color: pathSurface,
      borderRadius: BorderRadius.circular(12),
      border: Border.all(color: error ? pathYellow : const Color(0xFF333333)),
    ),
    child: Padding(
      padding: const EdgeInsets.all(16),
      child: Text(
        error ? 'Session unavailable. $text' : text,
        style: const TextStyle(fontSize: 16, height: 1.4),
      ),
    ),
  );
}
