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
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      textStyle: const TextStyle(
        fontFamily: 'Inter',
        fontSize: 18,
        fontWeight: FontWeight.w700,
      ),
    ),
  ),
);

enum SessionPhase { idle, starting, live, stopping }

/// Camera and speech ownership stay in SessionScreen. No camera cropping here.
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
    this.voiceStatus,
    this.audioMuted = false,
    this.onToggleAudio,
    this.onRepeat,
    this.onDescribeScene,
    this.onMoreDetails,
    this.hasMoreDetails = false,
    this.hapticsOn = false,
    this.hapticStatus,
    this.onToggleHaptics,
  });
  final SessionPhase phase;
  final VoidCallback onToggle;
  final Widget? preview;
  final List<Detection> detections;
  final int processedFrames;
  final int? elapsedMs;
  final String? error, voiceStatus;
  final bool audioMuted, hasMoreDetails;
  final bool hapticsOn;
  final String? hapticStatus;
  final VoidCallback? onToggleHaptics;
  final VoidCallback? onOpenSettings,
      onOpenLog,
      onToggleAudio,
      onRepeat,
      onDescribeScene,
      onMoreDetails;

  @override
  Widget build(BuildContext context) => Scaffold(
    body: SafeArea(
      child: LayoutBuilder(
        builder: (context, constraints) {
          final expandedText =
              MediaQuery.textScalerOf(context).scale(18) > 23.4;
          final scroll = expandedText || constraints.maxHeight < 580;
          final status =
              voiceStatus ?? 'Start a session for object announcements';
          final camera = _CameraPanel(
            phase: phase,
            preview: preview,
            detections: detections,
            voiceStatus: scroll ? null : status,
          );
          final header = _PathHeader(
            phase: phase,
            onOpenSettings: onOpenSettings,
            onOpenLog: onOpenLog,
            onDescribeScene: onDescribeScene,
            expandedText: expandedText,
            hapticsOn: hapticsOn,
            hapticStatus: hapticStatus,
            onToggleHaptics: onToggleHaptics,
          );
          final dock = _ActionDock(
            phase: phase,
            onToggle: onToggle,
            audioMuted: audioMuted,
            onToggleAudio: onToggleAudio,
            onRepeat: onRepeat,
            onDescribeScene: onDescribeScene,
            onMoreDetails: onMoreDetails,
            hasMoreDetails: hasMoreDetails,
            expandedText: expandedText,
          );
          final problem = error == null
              ? null
              : Semantics(
                  liveRegion: true,
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: pathSurface,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: pathYellow),
                    ),
                    child: Text(
                      'Session unavailable. $error',
                      style: const TextStyle(fontSize: 16, height: 1.35),
                    ),
                  ),
                );
          if (scroll) {
            return SingleChildScrollView(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  header,
                  const SizedBox(height: 12),
                  SizedBox(
                    height: (constraints.maxHeight * .55).clamp(280.0, 600.0),
                    child: camera,
                  ),
                  const SizedBox(height: 12),
                  _SpokenStrip(text: status, expanded: true),
                  if (problem != null) ...[const SizedBox(height: 12), problem],
                  const SizedBox(height: 16),
                  dock,
                ],
              ),
            );
          }
          // Errors get a bounded scroll area; camera and Stop remain reachable.
          return Padding(
            padding: const EdgeInsets.fromLTRB(12, 4, 12, 12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                header,
                const SizedBox(height: 8),
                Expanded(child: camera),
                if (problem != null) ...[
                  const SizedBox(height: 8),
                  ConstrainedBox(
                    constraints: const BoxConstraints(maxHeight: 100),
                    child: SingleChildScrollView(child: problem),
                  ),
                ],
                const SizedBox(height: 12),
                dock,
              ],
            ),
          );
        },
      ),
    ),
  );
}

class _CameraPanel extends StatelessWidget {
  const _CameraPanel({
    required this.phase,
    required this.preview,
    required this.detections,
    this.voiceStatus,
  });
  final SessionPhase phase;
  final Widget? preview;
  final List<Detection> detections;
  final String? voiceStatus;
  @override
  Widget build(BuildContext context) => ClipRRect(
    key: const ValueKey('camera-panel'),
    borderRadius: BorderRadius.circular(16),
    child: ColoredBox(
      color: pathSurface,
      child: Stack(
        fit: StackFit.expand,
        children: [
          if (phase == SessionPhase.live && preview != null)
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
                      phase == SessionPhase.starting ||
                              phase == SessionPhase.stopping
                          ? Icons.hourglass_empty
                          : Icons.videocam_off_outlined,
                      size: 48,
                      color: pathYellow,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    switch (phase) {
                      SessionPhase.idle => 'Camera is off',
                      SessionPhase.starting => 'Preparing camera',
                      SessionPhase.live => 'Detection is live',
                      SessionPhase.stopping => 'Ending session',
                    },
                    textAlign: TextAlign.center,
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ],
              ),
            ),
          if (voiceStatus != null)
            Positioned(
              left: 12,
              right: 12,
              bottom: 12,
              child: _SpokenStrip(text: voiceStatus!),
            ),
        ],
      ),
    ),
  );
}

class _SpokenStrip extends StatelessWidget {
  const _SpokenStrip({required this.text, this.expanded = false});
  final String text;
  final bool expanded;
  @override
  Widget build(BuildContext context) {
    final isMessage = text.startsWith('Last spoken: ');
    final message = isMessage ? text.substring('Last spoken: '.length) : text;
    final content = Row(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        const ExcludeSemantics(
          child: Icon(Icons.volume_up_outlined, size: 24, color: Colors.white),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                isMessage ? 'Last spoken' : 'Feedback',
                style: const TextStyle(fontSize: 12, color: Color(0xFFCCCCCC)),
              ),
              const SizedBox(height: 2),
              Text(
                message,
                maxLines: expanded ? null : 2,
                overflow: expanded ? null : TextOverflow.ellipsis,
                style: const TextStyle(
                  fontSize: 16,
                  height: 1.25,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ],
          ),
        ),
      ],
    );
    return Material(
      color: const Color(0xE6000000),
      borderRadius: BorderRadius.circular(12),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () => showDialog<void>(
          context: context,
          builder: (context) => AlertDialog(
            title: Text(isMessage ? 'Last spoken' : 'Feedback status'),
            content: SingleChildScrollView(child: Text(message)),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                style: TextButton.styleFrom(minimumSize: const Size(64, 64)),
                child: const Text('Close'),
              ),
            ],
          ),
        ),
        child: Semantics(
          button: true,
          label: text,
          hint: 'Open the full message',
          excludeSemantics: true,
          child: ConstrainedBox(
            constraints: const BoxConstraints(minHeight: 64),
            child: Padding(padding: const EdgeInsets.all(12), child: content),
          ),
        ),
      ),
    );
  }
}

class _ActionDock extends StatelessWidget {
  const _ActionDock({
    required this.phase,
    required this.onToggle,
    required this.audioMuted,
    required this.expandedText,
    this.onToggleAudio,
    this.onRepeat,
    this.onDescribeScene,
    this.onMoreDetails,
    required this.hasMoreDetails,
  });
  final SessionPhase phase;
  final bool audioMuted, expandedText, hasMoreDetails;
  final VoidCallback onToggle;
  final VoidCallback? onToggleAudio, onRepeat, onDescribeScene, onMoreDetails;
  @override
  Widget build(BuildContext context) {
    final active = phase == SessionPhase.live;
    final busy =
        phase == SessionPhase.starting || phase == SessionPhase.stopping;
    final label = switch (phase) {
      SessionPhase.idle => 'Start camera session',
      SessionPhase.starting => 'Starting camera…',
      SessionPhase.stopping => 'Stopping…',
      SessionPhase.live => hasMoreDetails ? 'More details' : 'Describe scene',
    };
    final action = busy
        ? null
        : active
        ? (hasMoreDetails ? onMoreDetails : onDescribeScene)
        : onToggle;
    final primary = FilledButton.icon(
      key: ValueKey(active ? 'scene-description' : 'session-toggle'),
      onPressed: action,
      icon: Icon(active ? Icons.volume_up_outlined : Icons.play_arrow),
      label: Text(label, textAlign: TextAlign.center),
    );
    final actions = [
      _DockButton(
        label: audioMuted ? 'Unmute audio' : 'Mute audio',
        icon: audioMuted ? Icons.volume_up_outlined : Icons.volume_off_outlined,
        onPressed: onToggleAudio,
      ),
      _DockButton(
        label: 'Repeat',
        semanticLabel: 'Repeat last alert',
        icon: Icons.replay,
        onPressed: onRepeat,
      ),
      _DockButton(
        key: ValueKey(active ? 'session-toggle' : 'inactive-stop'),
        label: 'Stop',
        icon: Icons.stop,
        accent: true,
        onPressed: active && !busy ? onToggle : null,
      ),
    ];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: MainAxisSize.min,
      children: [
        primary,
        const SizedBox(height: 12),
        if (expandedText) ...[
          for (var i = 0; i < actions.length; i++) ...[
            if (i > 0) const SizedBox(height: 16),
            actions[i],
          ],
        ] else
          IntrinsicHeight(
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                for (var i = 0; i < actions.length; i++) ...[
                  if (i > 0) const SizedBox(width: 12),
                  Expanded(child: actions[i]),
                ],
              ],
            ),
          ),
      ],
    );
  }
}

class _DockButton extends StatelessWidget {
  const _DockButton({
    super.key,
    required this.label,
    required this.icon,
    this.onPressed,
    this.semanticLabel,
    this.accent = false,
  });
  final String label;
  final String? semanticLabel;
  final IconData icon;
  final bool accent;
  final VoidCallback? onPressed;
  @override
  Widget build(BuildContext context) => Semantics(
    label: semanticLabel,
    child: OutlinedButton(
      onPressed: onPressed,
      style: OutlinedButton.styleFrom(
        foregroundColor: Colors.white,
        minimumSize: const Size(64, 80),
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 10),
        side: const BorderSide(color: Color(0xFFB3B3B3), width: 1.5),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            icon,
            size: 24,
            color: accent && onPressed != null ? pathYellow : null,
          ),
          const SizedBox(height: 6),
          Text(
            label,
            textAlign: TextAlign.center,
            style: const TextStyle(
              fontSize: 14,
              height: 1.2,
              fontWeight: FontWeight.w700,
            ),
          ),
        ],
      ),
    ),
  );
}

class _PathHeader extends StatelessWidget {
  const _PathHeader({
    required this.phase,
    required this.expandedText,
    this.onOpenSettings,
    this.onOpenLog,
    this.onDescribeScene,
    this.hapticsOn = false,
    this.hapticStatus,
    this.onToggleHaptics,
  });
  final SessionPhase phase;
  final bool expandedText;
  final bool hapticsOn;
  final String? hapticStatus;
  final VoidCallback? onToggleHaptics;
  final VoidCallback? onOpenSettings, onOpenLog, onDescribeScene;
  @override
  Widget build(BuildContext context) {
    final active = phase == SessionPhase.live;
    final status = Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        ExcludeSemantics(
          child: Icon(
            Icons.circle,
            size: 8,
            color: active ? const Color(0xFF55E889) : const Color(0xFFBDBDBD),
          ),
        ),
        const SizedBox(width: 6),
        Text(
          active ? 'LIVE' : 'IDLE',
          style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w700),
        ),
      ],
    );
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            ExcludeSemantics(
              child: Image.asset(
                'assets/figma/cpu.png',
                width: 24,
                height: 24,
                cacheWidth: 72,
                color: pathYellow,
              ),
            ),
            const SizedBox(width: 10),
            const Expanded(
              child: Text(
                'PATH',
                style: TextStyle(
                  fontSize: 24,
                  color: pathYellow,
                  fontWeight: FontWeight.w700,
                  letterSpacing: 1,
                ),
              ),
            ),
            if (!expandedText) status,
            SizedBox(
              width: 64,
              height: 64,
              child: PopupMenuButton<String>(
                tooltip: 'Open navigation menu',
                icon: const Icon(Icons.more_vert, color: Colors.white),
                onSelected: (value) {
                  if (value == 'settings') onOpenSettings?.call();
                  if (value == 'log') onOpenLog?.call();
                  if (value == 'describe') onDescribeScene?.call();
                  if (value == 'haptics') onToggleHaptics?.call();
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
                  PopupMenuItem(
                    height: 64,
                    value: 'describe',
                    enabled: active && onDescribeScene != null,
                    child: const Text('Describe scene'),
                  ),
                  CheckedPopupMenuItem(
                    height: 64,
                    value: 'haptics',
                    checked: hapticsOn,
                    enabled: onToggleHaptics != null,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(hapticsOn ? 'Haptics on' : 'Haptics off'),
                        if (hapticStatus != null)
                          Text(
                            hapticStatus!,
                            style: const TextStyle(fontSize: 12),
                          ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
        if (expandedText)
          Padding(padding: const EdgeInsets.only(top: 4), child: status),
      ],
    );
  }
}
