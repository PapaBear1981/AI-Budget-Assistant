import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../features/dashboard/presentation/pages/dashboard_page.dart';
import '../../features/transactions/presentation/pages/transactions_page.dart';
import '../../features/budgets/presentation/pages/budgets_page.dart';
import '../../features/bills/presentation/pages/bills_page.dart';
import '../../features/insights/presentation/pages/insights_page.dart';
import '../../features/settings/presentation/pages/settings_page.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/dashboard',
    routes: [
      ShellRoute(
        builder: (context, state, child) {
          return MainShell(child: child);
        },
        routes: [
          GoRoute(
            path: '/dashboard',
            name: 'dashboard',
            builder: (context, state) => const DashboardPage(),
          ),
          GoRoute(
            path: '/transactions',
            name: 'transactions',
            builder: (context, state) => const TransactionsPage(),
          ),
          GoRoute(
            path: '/budgets',
            name: 'budgets',
            builder: (context, state) => const BudgetsPage(),
          ),
          GoRoute(
            path: '/bills',
            name: 'bills',
            builder: (context, state) => const BillsPage(),
          ),
          GoRoute(
            path: '/insights',
            name: 'insights',
            builder: (context, state) => const InsightsPage(),
          ),
          GoRoute(
            path: '/settings',
            name: 'settings',
            builder: (context, state) => const SettingsPage(),
          ),
        ],
      ),
    ],
  );
});

class MainShell extends StatelessWidget {
  final Widget child;

  const MainShell({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Row(
        children: [
          // Navigation Rail for desktop
          if (MediaQuery.of(context).size.width >= 768)
            NavigationRail(
              selectedIndex: _getSelectedIndex(context),
              onDestinationSelected: (index) => _onDestinationSelected(context, index),
              labelType: NavigationRailLabelType.all,
              destinations: const [
                NavigationRailDestination(
                  icon: Icon(Icons.dashboard_outlined),
                  selectedIcon: Icon(Icons.dashboard),
                  label: Text('Dashboard'),
                ),
                NavigationRailDestination(
                  icon: Icon(Icons.receipt_long_outlined),
                  selectedIcon: Icon(Icons.receipt_long),
                  label: Text('Transactions'),
                ),
                NavigationRailDestination(
                  icon: Icon(Icons.account_balance_wallet_outlined),
                  selectedIcon: Icon(Icons.account_balance_wallet),
                  label: Text('Budgets'),
                ),
                NavigationRailDestination(
                  icon: Icon(Icons.receipt_outlined),
                  selectedIcon: Icon(Icons.receipt),
                  label: Text('Bills'),
                ),
                NavigationRailDestination(
                  icon: Icon(Icons.insights_outlined),
                  selectedIcon: Icon(Icons.insights),
                  label: Text('Insights'),
                ),
                NavigationRailDestination(
                  icon: Icon(Icons.settings_outlined),
                  selectedIcon: Icon(Icons.settings),
                  label: Text('Settings'),
                ),
              ],
            ),
          
          // Main content
          Expanded(child: child),
        ],
      ),
      
      // Bottom Navigation for mobile
      bottomNavigationBar: MediaQuery.of(context).size.width < 768
          ? BottomNavigationBar(
              currentIndex: _getSelectedIndex(context),
              onTap: (index) => _onDestinationSelected(context, index),
              type: BottomNavigationBarType.fixed,
              items: const [
                BottomNavigationBarItem(
                  icon: Icon(Icons.dashboard_outlined),
                  activeIcon: Icon(Icons.dashboard),
                  label: 'Dashboard',
                ),
                BottomNavigationBarItem(
                  icon: Icon(Icons.receipt_long_outlined),
                  activeIcon: Icon(Icons.receipt_long),
                  label: 'Transactions',
                ),
                BottomNavigationBarItem(
                  icon: Icon(Icons.account_balance_wallet_outlined),
                  activeIcon: Icon(Icons.account_balance_wallet),
                  label: 'Budgets',
                ),
                BottomNavigationBarItem(
                  icon: Icon(Icons.receipt_outlined),
                  activeIcon: Icon(Icons.receipt),
                  label: 'Bills',
                ),
                BottomNavigationBarItem(
                  icon: Icon(Icons.insights_outlined),
                  activeIcon: Icon(Icons.insights),
                  label: 'Insights',
                ),
              ],
            )
          : null,
    );
  }

  int _getSelectedIndex(BuildContext context) {
    final location = GoRouterState.of(context).location;
    switch (location) {
      case '/dashboard':
        return 0;
      case '/transactions':
        return 1;
      case '/budgets':
        return 2;
      case '/bills':
        return 3;
      case '/insights':
        return 4;
      case '/settings':
        return 5;
      default:
        return 0;
    }
  }

  void _onDestinationSelected(BuildContext context, int index) {
    switch (index) {
      case 0:
        context.go('/dashboard');
        break;
      case 1:
        context.go('/transactions');
        break;
      case 2:
        context.go('/budgets');
        break;
      case 3:
        context.go('/bills');
        break;
      case 4:
        context.go('/insights');
        break;
      case 5:
        context.go('/settings');
        break;
    }
  }
}
