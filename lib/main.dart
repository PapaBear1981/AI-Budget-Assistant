import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'core/theme/app_theme.dart';
import 'core/navigation/app_router.dart';

void main() {
  runApp(
    const ProviderScope(
      child: AIBudgetAssistantApp(),
    ),
  );
}

class AIBudgetAssistantApp extends ConsumerWidget {
  const AIBudgetAssistantApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(appRouterProvider);
    
    return MaterialApp.router(
      title: 'AI Budget Assistant',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: ThemeMode.dark, // Force dark theme to match target design
      routerConfig: router,
    );
  }
}
