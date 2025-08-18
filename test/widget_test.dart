// This is a basic Flutter widget test for AI Budget Assistant.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:ai_budget_assistant/main.dart';

void main() {
  testWidgets('AI Budget Assistant app smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(
      const ProviderScope(
        child: AIBudgetAssistantApp(),
      ),
    );

    // Verify that the app loads and shows the splash screen initially
    expect(find.byType(MaterialApp), findsOneWidget);

    // Wait for any initial animations to complete
    await tester.pumpAndSettle();
  });
}
