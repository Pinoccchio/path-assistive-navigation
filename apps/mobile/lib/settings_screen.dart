import 'package:flutter/material.dart';

import 'path_page.dart';
import 'path_preferences.dart';
import 'session_view.dart';
import 'figma_check.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key, required this.preferences});
  final PathPreferences preferences;

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  PathPreferences get preferences => widget.preferences;
  String? _lastIssue;

  @override
  void initState() {
    super.initState();
    preferences.addListener(_reportIssue);
    _reportIssue();
  }

  void _reportIssue() {
    final issue = preferences.error;
    if (issue == null) {
      _lastIssue = null;
      return;
    }
    if (_lastIssue == issue) return;
    _lastIssue = issue;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).hideCurrentSnackBar();
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(issue),
          duration: const Duration(seconds: 6),
          action: SnackBarAction(label: 'Retry', onPressed: preferences.save),
        ),
      );
    });
  }

  @override
  void didUpdateWidget(covariant SettingsScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.preferences != preferences) {
      oldWidget.preferences.removeListener(_reportIssue);
      preferences.addListener(_reportIssue);
      _lastIssue = null;
      _reportIssue();
    }
  }

  @override
  void dispose() {
    preferences.removeListener(_reportIssue);
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    body: SafeArea(
      child: AnimatedBuilder(
        animation: preferences,
        builder: (context, child) => LayoutBuilder(
          builder: (context, constraints) {
            final compact =
                constraints.maxHeight < 800 &&
                MediaQuery.textScalerOf(context).scale(18) <= 23;
            final sectionGap = compact ? 8.0 : 16.0;
            final labelGap = compact ? 4.0 : 8.0;
            return SingleChildScrollView(
              padding: EdgeInsets.fromLTRB(
                16,
                compact ? 8 : 12,
                16,
                compact ? 8 : 16,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const PathPageHeader(title: 'Accessibility & Alerts'),
                  SizedBox(height: compact ? 12 : 24),
                  if (!preferences.ready && preferences.error == null)
                    const LinearProgressIndicator(
                      semanticsLabel: 'Loading settings',
                    ),
                  const _Heading('Alert delivery'),
                  SizedBox(height: labelGap),
                  _Choices(
                    labels: const [
                      'Voice & Haptic',
                      'Voice Only',
                      'Haptic Only',
                    ],
                    selected: preferences.delivery.index,
                    onChanged: preferences.ready
                        ? (index) => preferences.update(
                            delivery: AlertDelivery.values[index],
                          )
                        : null,
                  ),
                  SizedBox(height: sectionGap),
                  const _Heading('Direction format'),
                  SizedBox(height: labelGap),
                  _Choices(
                    labels: const ['Clock-Hand System', '3-Zone Direction'],
                    minimumHeight: compact ? 64 : 72,
                    selected: preferences.direction.index,
                    onChanged: preferences.ready
                        ? (index) => preferences.update(
                            direction: DirectionFormat.values[index],
                          )
                        : null,
                  ),
                  SizedBox(height: sectionGap),
                  _SettingSlider(
                    label: 'Speech Rate',
                    value: preferences.speechRate,
                    min: 1,
                    max: 2,
                    divisions: 10,
                    unit: 'x',
                    onChanged: preferences.ready
                        ? (value) => preferences.update(speechRate: value)
                        : null,
                  ),
                  SizedBox(height: sectionGap),
                  _SettingSlider(
                    label: 'Alert Cooldown',
                    value: preferences.cooldown,
                    min: .5,
                    max: 3,
                    divisions: 5,
                    unit: 's',
                    onChanged: preferences.ready
                        ? (value) => preferences.update(cooldown: value)
                        : null,
                  ),
                  SizedBox(height: sectionGap),
                  const _Heading('Hazard alerts'),
                  SizedBox(height: sectionGap),
                  _HazardSwitch(
                    label: 'Stairs',
                    value: preferences.stairs,
                    onChanged: preferences.ready
                        ? (value) => preferences.update(stairs: value)
                        : null,
                  ),
                  const SizedBox(height: 16),
                  _HazardSwitch(
                    label: 'Vehicles',
                    value: preferences.vehicles,
                    onChanged: preferences.ready
                        ? (value) => preferences.update(vehicles: value)
                        : null,
                  ),
                  const SizedBox(height: 16),
                  _HazardSwitch(
                    label: 'Pedestrians',
                    value: preferences.pedestrians,
                    onChanged: preferences.ready
                        ? (value) => preferences.update(pedestrians: value)
                        : null,
                  ),
                  SizedBox(height: sectionGap),
                ],
              ),
            );
          },
        ),
      ),
    ),
  );
}

class _Heading extends StatelessWidget {
  const _Heading(this.text, {this.fontSize = 18});
  final String text;
  final double fontSize;
  @override
  Widget build(BuildContext context) => Semantics(
    header: true,
    child: Text(
      text,
      style: TextStyle(
        fontSize: fontSize,
        height: fontSize == 18 ? 22 / 18 : 1.2,
        fontWeight: FontWeight.w700,
        color: Colors.white,
      ),
    ),
  );
}

class _Choices extends StatelessWidget {
  const _Choices({
    required this.labels,
    required this.selected,
    required this.onChanged,
    this.minimumHeight = 64,
  });
  final List<String> labels;
  final int selected;
  final ValueChanged<int>? onChanged;
  final double minimumHeight;

  @override
  Widget build(BuildContext context) {
    final options = [
      for (var i = 0; i < labels.length; i++)
        Semantics(
          selected: selected == i,
          inMutuallyExclusiveGroup: true,
          child: OutlinedButton(
            onPressed: onChanged == null ? null : () => onChanged!(i),
            style: OutlinedButton.styleFrom(
              backgroundColor: selected == i ? pathYellow : Colors.black,
              foregroundColor: selected == i ? Colors.black : Colors.white,
              side: BorderSide(
                color: selected == i ? pathYellow : const Color(0xFFB3B3B3),
                width: 2,
              ),
              minimumSize: Size.fromHeight(minimumHeight),
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
              shape: const StadiumBorder(),
            ),
            child: Text(
              '${selected == i ? '✓' : '○'} ${labels[i]}',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: selected == i ? Colors.black : Colors.white,
                fontFamily: 'Inter',
                fontSize: 18,
                height: 1.15,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
        ),
    ];
    if (MediaQuery.textScalerOf(context).scale(18) > 24) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          for (var i = 0; i < options.length; i++) ...[
            if (i > 0) const SizedBox(height: 16),
            options[i],
          ],
        ],
      );
    }
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        for (var i = 0; i < options.length; i++) ...[
          if (i > 0) const SizedBox(width: 16),
          Expanded(child: options[i]),
        ],
      ],
    );
  }
}

class _SettingSlider extends StatelessWidget {
  const _SettingSlider({
    required this.label,
    required this.value,
    required this.min,
    required this.max,
    required this.divisions,
    required this.unit,
    required this.onChanged,
  });
  final String label;
  final double value, min, max;
  final int divisions;
  final String unit;
  final ValueChanged<double>? onChanged;

  @override
  Widget build(BuildContext context) => Column(
    children: [
      SizedBox(
        width: double.infinity,
        child: Wrap(
          alignment: WrapAlignment.spaceBetween,
          spacing: 16,
          runSpacing: 8,
          children: [
            _Heading(label, fontSize: 20),
            Text(
              '${value.toStringAsFixed(1)}$unit',
              style: const TextStyle(
                fontSize: 20,
                height: 1.2,
                color: pathYellow,
              ),
            ),
          ],
        ),
      ),
      SizedBox(
        height: 64 + (MediaQuery.textScalerOf(context).scale(14) - 14),
        child: Stack(
          children: [
            Positioned(
              left: 0,
              right: 0,
              top: -8,
              child: SliderTheme(
                data: SliderTheme.of(context).copyWith(
                  trackHeight: 4,
                  tickMarkShape: SliderTickMarkShape.noTickMark,
                  overlayShape: const RoundSliderOverlayShape(
                    overlayRadius: 24,
                  ),
                  thumbShape: const RoundSliderThumbShape(
                    enabledThumbRadius: 12,
                    elevation: 0,
                    pressedElevation: 0,
                  ),
                ),
                child: SizedBox(
                  height: 64,
                  child: Slider(
                    key: ValueKey(label),
                    padding: EdgeInsets.zero,
                    min: min,
                    max: max,
                    divisions: divisions,
                    value: value,
                    onChanged: onChanged,
                    label: '${value.toStringAsFixed(1)}$unit',
                    semanticFormatterCallback: (v) =>
                        '$label, ${v.toStringAsFixed(1)} ${unit == 'x' ? 'times' : 'seconds'}',
                    activeColor: pathYellow,
                    inactiveColor: const Color(0xFFB3B3B3),
                  ),
                ),
              ),
            ),
            Positioned(
              left: 0,
              right: 0,
              bottom: 0,
              child: IgnorePointer(
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      '${min.toStringAsFixed(1)}$unit',
                      style: const TextStyle(
                        fontSize: 14,
                        color: Color(0xFFBDBDBD),
                      ),
                    ),
                    Text(
                      '${max.toStringAsFixed(1)}$unit',
                      style: const TextStyle(
                        fontSize: 14,
                        color: Color(0xFFBDBDBD),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    ],
  );
}

class _HazardSwitch extends StatelessWidget {
  const _HazardSwitch({
    required this.label,
    required this.value,
    required this.onChanged,
  });
  final String label;
  final bool value;
  final ValueChanged<bool>? onChanged;

  @override
  Widget build(BuildContext context) {
    final labelWidget = Text(
      label,
      style: const TextStyle(
        fontFamily: 'Inter',
        fontSize: 20,
        height: 1.2,
        color: Colors.white,
      ),
    );
    final stateWidget = DecoratedBox(
      decoration: BoxDecoration(
        color: value ? pathYellow : pathSurface,
        borderRadius: BorderRadius.circular(99),
        border: Border.all(color: value ? pathYellow : const Color(0xFFB3B3B3)),
      ),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (value) ...[
              ExcludeSemantics(child: FigmaCheck()),
              const SizedBox(width: 6),
            ],
            Text(
              value ? 'ON' : 'OFF',
              style: TextStyle(
                fontFamily: 'Inter',
                fontSize: 18,
                height: 1.2,
                color: value ? Colors.black : Colors.white,
              ),
            ),
          ],
        ),
      ),
    );
    return Semantics(
      label: label,
      toggled: value,
      enabled: onChanged != null,
      excludeSemantics: true,
      onTap: onChanged == null ? null : () => onChanged!(!value),
      child: OutlinedButton(
        onPressed: onChanged == null ? null : () => onChanged!(!value),
        style: OutlinedButton.styleFrom(
          backgroundColor: pathSurface,
          foregroundColor: Colors.white,
          side: const BorderSide(color: Color(0xFFB3B3B3), width: 2),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
          minimumSize: const Size.fromHeight(64),
          padding: const EdgeInsets.all(12),
        ),
        child: MediaQuery.textScalerOf(context).scale(20) > 28
            ? Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  labelWidget,
                  const SizedBox(height: 12),
                  Align(alignment: Alignment.centerRight, child: stateWidget),
                ],
              )
            : Row(
                children: [
                  Expanded(child: labelWidget),
                  const SizedBox(width: 8),
                  stateWidget,
                ],
              ),
      ),
    );
  }
}
