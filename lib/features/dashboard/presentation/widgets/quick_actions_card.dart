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
      elevation: 6,
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          gradient: LinearGradient(
            colors: [
              Theme.of(context).colorScheme.surfaceVariant.withOpacity(0.3),
              Theme.of(context).colorScheme.surface,
            ],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Theme.of(context).colorScheme.primary.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(
                    Icons.flash_on,
                    color: Theme.of(context).colorScheme.primary,
                    size: 20,
                  ),
                ),
                const SizedBox(width: 12),
                Text(
                  'Quick Actions',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            LayoutBuilder(
              builder: (context, constraints) {
                // Calculate responsive grid parameters
                final screenWidth = constraints.maxWidth;
                int crossAxisCount = 2;
                double childAspectRatio = 1.5;

                if (screenWidth > 600) {
                  crossAxisCount = 4;
                  childAspectRatio = 1.2;
                } else if (screenWidth > 400) {
                  crossAxisCount = 2;
                  childAspectRatio = 1.5;
                } else {
                  crossAxisCount = 2;
                  childAspectRatio = 1.3;
                }

                return GridView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: crossAxisCount,
                    crossAxisSpacing: 12,
                    mainAxisSpacing: 12,
                    childAspectRatio: childAspectRatio,
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
      elevation: 2,
      borderRadius: BorderRadius.circular(16),
      child: InkWell(
        onTap: () {
          _animateButtonPress(action);
        },
        borderRadius: BorderRadius.circular(16),
        splashColor: action.color.withOpacity(0.2),
        highlightColor: action.color.withOpacity(0.1),
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [
                action.color.withOpacity(0.1),
                action.color.withOpacity(0.05),
              ],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: action.color.withOpacity(0.2),
              width: 1.5,
            ),
            boxShadow: [
              BoxShadow(
                color: action.color.withOpacity(0.1),
                blurRadius: 8,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: action.color.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  action.icon,
                  size: 28,
                  color: action.color,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                action.title,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                  color: Theme.of(context).colorScheme.onSurface,
                ),
                textAlign: TextAlign.center,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
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
