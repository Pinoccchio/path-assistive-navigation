import 'package:flutter/material.dart';

class PathPageHeader extends StatelessWidget {
  const PathPageHeader({super.key, required this.title});
  final String title;

  @override
  Widget build(BuildContext context) => Row(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      SizedBox(
        width: 64,
        child: OutlinedButton(
          onPressed: () => Navigator.of(context).maybePop(),
          style: OutlinedButton.styleFrom(
            minimumSize: const Size(64, 64),
            padding: const EdgeInsets.all(8),
            foregroundColor: Colors.white,
            side: const BorderSide(color: Color(0xFFB3B3B3), width: 2),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ExcludeSemantics(
                child: Image.asset(
                  'assets/figma/back.png',
                  width: 24,
                  height: 24,
                  cacheWidth: 72,
                ),
              ),
              const Text(
                'Back',
                style: TextStyle(fontFamily: 'Inter', fontSize: 14),
              ),
            ],
          ),
        ),
      ),
      const SizedBox(width: 16),
      Expanded(
        child: Semantics(
          header: true,
          child: Text(
            title,
            style: const TextStyle(
              fontSize: 28,
              height: 1.1,
              fontWeight: FontWeight.w700,
            ),
          ),
        ),
      ),
    ],
  );
}

Future<void> showPathDevelopment(BuildContext context, String feature) =>
    showDialog<void>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('$feature — In development'),
        content: const Text('This feature is not connected yet.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            style: TextButton.styleFrom(minimumSize: const Size(64, 64)),
            child: const Text('Close'),
          ),
        ],
      ),
    );
