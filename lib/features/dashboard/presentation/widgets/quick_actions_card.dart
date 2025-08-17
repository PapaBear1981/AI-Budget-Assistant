import 'package:flutter/material.dart';

class QuickActionsCard extends StatefulWidget {
  const QuickActionsCard({super.key});

  @override
  State<QuickActionsCard> createState() => _QuickActionsCardState();
}

class _QuickActionsCardState extends State<QuickActionsCard>
    with TickerProviderStateMixin {
  late List<AnimationController> _controllers;
  late List<Animation<double>> _scaleAnimations;

  final List<QuickAction> _actions = [
    QuickAction(
      title: 'Add Transaction',
      icon: Icons.add_circle_outline,
      color: Colors.blue,
      onTap: () {
        // TODO: Navigate to add transaction
      },
    ),
    QuickAction(
      title: 'Import Data',
      icon: Icons.upload_file,
      color: Colors.green,
      onTap: () {
        // TODO: Navigate to import
      },
    ),
    QuickAction(
      title: 'View Reports',
      icon: Icons.analytics_outlined,
      color: Colors.purple,
      onTap: () {
        // TODO: Navigate to reports
      },
    ),
    QuickAction(
      title: 'Set Budget',
      icon: Icons.account_balance_wallet_outlined,
      color: Colors.orange,
      onTap: () {
        // TODO: Navigate to budget creation
      },
    ),
  ];

  @override
  void initState() {
    super.initState();
    _controllers = List.generate(
      _actions.length,
      (index) => AnimationController(
        duration: Duration(milliseconds: 300 + (index * 100)),
        vsync: this,
      ),
    );

    _scaleAnimations = _controllers.map((controller) {
      return Tween<double>(
        begin: 0.0,
        end: 1.0,
      ).animate(CurvedAnimation(
        parent: controller,
        curve: Curves.elasticOut,
      ));
    }).toList();

    // Start animations with staggered delay
    for (int i = 0; i < _controllers.length; i++) {
      Future.delayed(Duration(milliseconds: i * 150), () {
        if (mounted) {
          _controllers[i].forward();
        }
      });
    }
  }

  @override
  void dispose() {
    for (final controller in _controllers) {
      controller.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Quick Actions',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            GridView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                crossAxisSpacing: 12,
                mainAxisSpacing: 12,
                childAspectRatio: 1.5,
              ),
              itemCount: _actions.length,
              itemBuilder: (context, index) {
                return AnimatedBuilder(
                  animation: _scaleAnimations[index],
                  builder: (context, child) {
                    return Transform.scale(
                      scale: _scaleAnimations[index].value,
                      child: _buildActionButton(context, _actions[index]),
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

  Widget _buildActionButton(BuildContext context, QuickAction action) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: () {
          _animateButtonPress(action);
        },
        borderRadius: BorderRadius.circular(12),
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: action.color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: action.color.withOpacity(0.3),
              width: 1,
            ),
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                action.icon,
                size: 32,
                color: action.color,
              ),
              const SizedBox(height: 8),
              Text(
                action.title,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                  color: action.color,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _animateButtonPress(QuickAction action) {
    // Create a temporary animation for button press feedback
    final controller = AnimationController(
      duration: const Duration(milliseconds: 150),
      vsync: this,
    );

    final scaleAnimation = Tween<double>(
      begin: 1.0,
      end: 0.95,
    ).animate(CurvedAnimation(
      parent: controller,
      curve: Curves.easeInOut,
    ));

    controller.forward().then((_) {
      controller.reverse().then((_) {
        controller.dispose();
        action.onTap();
      });
    });
  }
}

class QuickAction {
  final String title;
  final IconData icon;
  final Color color;
  final VoidCallback onTap;

  QuickAction({
    required this.title,
    required this.icon,
    required this.color,
    required this.onTap,
  });
}
