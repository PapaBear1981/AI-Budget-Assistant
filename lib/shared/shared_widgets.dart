import 'package:flutter/material.dart';

/// Shared widgets and UI utilities used across features.
///
/// This file is intentionally small — it's a starter to ensure the
/// `lib/shared` directory exists and provides an example shared widget
/// following the project's Material 3 / theming conventions.
class SharedPrimaryButton extends StatelessWidget {
  final String label;
  final VoidCallback? onPressed;
  final EdgeInsetsGeometry padding;

  const SharedPrimaryButton({
    Key? key,
    required this.label,
    this.onPressed,
    this.padding = const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return ElevatedButton(
      style: ElevatedButton.styleFrom(
        backgroundColor: colorScheme.primary,
        foregroundColor: colorScheme.onPrimary,
        padding: padding,
        elevation: 2,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
      onPressed: onPressed,
      child: Text(
        label,
        style: TextStyle(
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}
