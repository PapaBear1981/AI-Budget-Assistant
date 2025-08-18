import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/theme/app_theme.dart';

class UpcomingBillsCard extends ConsumerStatefulWidget {
  const UpcomingBillsCard({super.key});

  @override
  ConsumerState<UpcomingBillsCard> createState() => _UpcomingBillsCardState();
}

class _UpcomingBillsCardState extends ConsumerState<UpcomingBillsCard>
    with TickerProviderStateMixin {
  late AnimationController _animationController;
  late List<Animation<double>> _scaleAnimations;
  late List<Animation<double>> _fadeAnimations;

  // Mock data - will be replaced with actual data from providers
  final List<Bill> _upcomingBills = [
    Bill(
      id: '1',
      title: 'Electricity Bill',
      company: 'Power Company',
      amount: 125.50,
      dueDate: DateTime.now().add(const Duration(days: 3)),
      icon: Icons.flash_on,
      color: Colors.amber,
      isPaid: false,
    ),
    Bill(
      id: '2',
      title: 'Internet',
      company: 'ISP Provider',
      amount: 79.99,
      dueDate: DateTime.now().add(const Duration(days: 5)),
      icon: Icons.wifi,
      color: Colors.blue,
      isPaid: false,
    ),
    Bill(
      id: '3',
      title: 'Phone Bill',
      company: 'Mobile Carrier',
      amount: 65.00,
      dueDate: DateTime.now().add(const Duration(days: 7)),
      icon: Icons.phone,
      color: Colors.green,
      isPaid: false,
    ),
    Bill(
      id: '4',
      title: 'Rent',
      company: 'Property Management',
      amount: 1200.00,
      dueDate: DateTime.now().add(const Duration(days: 12)),
      icon: Icons.home,
      color: Colors.purple,
      isPaid: false,
    ),
  ];

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 1800),
      vsync: this,
    );

    // Create staggered animations for each bill
    // Calculate safe intervals to prevent exceeding 1.0
    final itemCount = _upcomingBills.length;
    final maxScaleStart = itemCount > 0 ? (itemCount - 1) * 0.1 : 0.0;
    final maxFadeStart = itemCount > 0 ? (itemCount - 1) * 0.08 : 0.0;

    _scaleAnimations = List.generate(_upcomingBills.length, (index) {
      final start = (index * 0.1).clamp(0.0, 0.8);
      final end = (start + 0.4).clamp(start + 0.1, 1.0);

      return Tween<double>(
        begin: 0.0,
        end: 1.0,
      ).animate(CurvedAnimation(
        parent: _animationController,
        curve: Interval(
          start,
          end,
          curve: Curves.elasticOut,
        ),
      ));
    });

    _fadeAnimations = List.generate(_upcomingBills.length, (index) {
      final start = (index * 0.08).clamp(0.0, 0.7);
      final end = (start + 0.3).clamp(start + 0.1, 1.0);

      return Tween<double>(
        begin: 0.0,
        end: 1.0,
      ).animate(CurvedAnimation(
        parent: _animationController,
        curve: Interval(
          start,
          end,
          curve: Curves.easeInOut,
        ),
      ));
    });

    _animationController.forward();
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 4,
      child: Container(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Upcoming Bills',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                TextButton(
                  onPressed: () {
                    // TODO: Navigate to all bills
                  },
                  child: const Text('View All'),
                ),
              ],
            ),
            const SizedBox(height: 16),
            
            // Animated bills list
            ListView.separated(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: _upcomingBills.length,
              separatorBuilder: (context, index) => const SizedBox(height: 12),
              itemBuilder: (context, index) {
                final bill = _upcomingBills[index];
                return AnimatedBuilder(
                  animation: _animationController,
                  builder: (context, child) {
                    return ScaleTransition(
                      scale: _scaleAnimations[index],
                      child: FadeTransition(
                        opacity: _fadeAnimations[index],
                        child: _buildBillItem(context, bill),
                      ),
                    );
                  },
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBillItem(BuildContext context, Bill bill) {
    final daysUntilDue = bill.dueDate.difference(DateTime.now()).inDays;
    final isOverdue = daysUntilDue < 0;
    final isDueSoon = daysUntilDue <= 3 && daysUntilDue >= 0;
    
    Color urgencyColor = Theme.of(context).colorScheme.onSurface;
    if (isOverdue) {
      urgencyColor = AppTheme.errorColor;
    } else if (isDueSoon) {
      urgencyColor = AppTheme.warningColor;
    }
    
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surfaceVariant.withOpacity(0.3),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isOverdue || isDueSoon 
              ? urgencyColor.withOpacity(0.3)
              : Theme.of(context).colorScheme.outline.withOpacity(0.2),
          width: isOverdue || isDueSoon ? 2 : 1,
        ),
      ),
      child: Row(
        children: [
          // Icon container with animated background
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: bill.color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(
              bill.icon,
              color: bill.color,
              size: 24,
            ),
          ),
          const SizedBox(width: 16),
          
          // Bill details
          Expanded(
            flex: 3,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  bill.title,
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 4),
                Text(
                  bill.company,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Theme.of(context).colorScheme.onSurface.withOpacity(0.6),
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),

          const SizedBox(width: 8),

          // Amount and due date
          Flexible(
            flex: 2,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  '\$${bill.amount.toStringAsFixed(2)}',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: AppTheme.expenseColor,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 4),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
                  decoration: BoxDecoration(
                    color: urgencyColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    _formatDueDate(bill.dueDate),
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: urgencyColor,
                      fontWeight: FontWeight.w600,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  String _formatDueDate(DateTime dueDate) {
    final daysUntilDue = dueDate.difference(DateTime.now()).inDays;
    
    if (daysUntilDue < 0) {
      return 'Overdue';
    } else if (daysUntilDue == 0) {
      return 'Due Today';
    } else if (daysUntilDue == 1) {
      return 'Due Tomorrow';
    } else {
      return 'Due in ${daysUntilDue}d';
    }
  }
}

class Bill {
  final String id;
  final String title;
  final String company;
  final double amount;
  final DateTime dueDate;
  final IconData icon;
  final Color color;
  final bool isPaid;

  Bill({
    required this.id,
    required this.title,
    required this.company,
    required this.amount,
    required this.dueDate,
    required this.icon,
    required this.color,
    required this.isPaid,
  });
}
