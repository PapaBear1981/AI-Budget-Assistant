import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/theme/app_theme.dart';

class AnimatedBalanceCard extends ConsumerStatefulWidget {
  const AnimatedBalanceCard({super.key});

  @override
  ConsumerState<AnimatedBalanceCard> createState() => _AnimatedBalanceCardState();
}

class _AnimatedBalanceCardState extends ConsumerState<AnimatedBalanceCard>
    with TickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  late Animation<double> _balanceAnimation;
  late Animation<Color?> _colorAnimation;

  // Mock data - will be replaced with actual data from providers
  final double _currentBalance = 2847.50;
  final double _monthlyIncome = 4200.00;
  final double _monthlyExpenses = 1352.50;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 2000),
      vsync: this,
    );

    _scaleAnimation = Tween<double>(
      begin: 0.8,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: const Interval(0.0, 0.5, curve: Curves.elasticOut),
    ));

    _balanceAnimation = Tween<double>(
      begin: 0,
      end: _currentBalance,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: const Interval(0.3, 0.8, curve: Curves.easeOutCubic),
    ));

    _colorAnimation = ColorTween(
      begin: Colors.grey.shade300,
      end: AppTheme.successColor,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: const Interval(0.5, 1.0, curve: Curves.easeInOut),
    ));

    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return Transform.scale(
          scale: _scaleAnimation.value,
          child: Card(
            elevation: 8,
            child: Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(16),
                gradient: LinearGradient(
                  colors: [
                    Theme.of(context).colorScheme.primary,
                    Theme.of(context).colorScheme.primary.withOpacity(0.8),
                  ],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Current Balance',
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          color: Theme.of(context).colorScheme.onPrimary.withOpacity(0.9),
                        ),
                      ),
                      Icon(
                        Icons.visibility_outlined,
                        color: Theme.of(context).colorScheme.onPrimary.withOpacity(0.7),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  
                  // Animated balance
                  AnimatedBuilder(
                    animation: _balanceAnimation,
                    builder: (context, child) {
                      return Text(
                        '\$${_balanceAnimation.value.toStringAsFixed(2)}',
                        style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: Theme.of(context).colorScheme.onPrimary,
                        ),
                      );
                    },
                  ),
                  
                  const SizedBox(height: 24),
                  
                  // Income and Expenses row
                  Row(
                    children: [
                      Expanded(
                        child: _buildStatItem(
                          context,
                          'Income',
                          _monthlyIncome,
                          Icons.trending_up,
                          AppTheme.incomeColor,
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: _buildStatItem(
                          context,
                          'Expenses',
                          _monthlyExpenses,
                          Icons.trending_down,
                          AppTheme.expenseColor,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildStatItem(
    BuildContext context,
    String label,
    double amount,
    IconData icon,
    Color color,
  ) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.onPrimary.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                icon,
                size: 16,
                color: color,
              ),
              const SizedBox(width: 4),
              Text(
                label,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Theme.of(context).colorScheme.onPrimary.withOpacity(0.8),
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            '\$${amount.toStringAsFixed(2)}',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
              color: Theme.of(context).colorScheme.onPrimary,
            ),
          ),
        ],
      ),
    );
  }
}
