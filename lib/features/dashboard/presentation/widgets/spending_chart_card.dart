import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fl_chart/fl_chart.dart';

class SpendingChartCard extends ConsumerStatefulWidget {
  const SpendingChartCard({super.key});

  @override
  ConsumerState<SpendingChartCard> createState() => _SpendingChartCardState();
}

class _SpendingChartCardState extends ConsumerState<SpendingChartCard>
    with TickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _chartAnimation;
  late Animation<double> _fadeAnimation;
  
  int _selectedIndex = -1;
  bool _showPieChart = true;

  // Mock data - will be replaced with actual data from providers
  final List<SpendingCategory> _spendingData = [
    SpendingCategory(
      name: 'Food & Dining',
      amount: 450.75,
      color: Colors.orange,
      icon: Icons.restaurant,
    ),
    SpendingCategory(
      name: 'Transportation',
      amount: 320.50,
      color: Colors.blue,
      icon: Icons.directions_car,
    ),
    SpendingCategory(
      name: 'Shopping',
      amount: 280.25,
      color: Colors.purple,
      icon: Icons.shopping_bag,
    ),
    SpendingCategory(
      name: 'Entertainment',
      amount: 150.00,
      color: Colors.green,
      icon: Icons.movie,
    ),
    SpendingCategory(
      name: 'Utilities',
      amount: 200.00,
      color: Colors.red,
      icon: Icons.flash_on,
    ),
    SpendingCategory(
      name: 'Healthcare',
      amount: 120.30,
      color: Colors.teal,
      icon: Icons.local_hospital,
    ),
  ];

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 2000),
      vsync: this,
    );

    _chartAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: const Interval(0.2, 0.8, curve: Curves.easeOutCubic),
    ));

    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: const Interval(0.0, 0.6, curve: Curves.easeInOut),
    ));

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
            // Header with toggle
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Spending Breakdown',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Row(
                  children: [
                    IconButton(
                      onPressed: () {
                        setState(() {
                          _showPieChart = !_showPieChart;
                        });
                      },
                      icon: Icon(
                        _showPieChart ? Icons.bar_chart : Icons.pie_chart,
                        color: Theme.of(context).colorScheme.primary,
                      ),
                    ),
                    TextButton(
                      onPressed: () {
                        // TODO: Navigate to detailed analytics
                      },
                      child: const Text('Details'),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 24),
            
            // Animated chart
            AnimatedBuilder(
              animation: _animationController,
              builder: (context, child) {
                return FadeTransition(
                  opacity: _fadeAnimation,
                  child: LayoutBuilder(
                    builder: (context, constraints) {
                      // Responsive chart height
                      double chartHeight = 300;
                      if (constraints.maxWidth < 400) {
                        chartHeight = 250;
                      } else if (constraints.maxWidth > 600) {
                        chartHeight = 350;
                      }

                      return SizedBox(
                        height: chartHeight,
                        child: _showPieChart ? _buildPieChart() : _buildBarChart(),
                      );
                    },
                  ),
                );
              },
            ),
            
            const SizedBox(height: 24),
            
            // Legend
            _buildLegend(),
          ],
        ),
      ),
    );
  }

  Widget _buildPieChart() {
    final total = _spendingData.fold<double>(0, (sum, item) => sum + item.amount);
    
    return PieChart(
      PieChartData(
        pieTouchData: PieTouchData(
          touchCallback: (FlTouchEvent event, pieTouchResponse) {
            setState(() {
              if (!event.isInterestedForInteractions ||
                  pieTouchResponse == null ||
                  pieTouchResponse.touchedSection == null) {
                _selectedIndex = -1;
                return;
              }
              _selectedIndex = pieTouchResponse.touchedSection!.touchedSectionIndex;
            });
          },
        ),
        borderData: FlBorderData(show: false),
        sectionsSpace: 2,
        centerSpaceRadius: 60,
        sections: _spendingData.asMap().entries.map((entry) {
          final index = entry.key;
          final category = entry.value;
          final isSelected = index == _selectedIndex;
          final percentage = (category.amount / total * 100);
          
          return PieChartSectionData(
            color: category.color,
            value: category.amount * _chartAnimation.value,
            title: '${percentage.toStringAsFixed(1)}%',
            radius: isSelected ? 70 : 60,
            titleStyle: TextStyle(
              fontSize: isSelected ? 14 : 12,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
            badgeWidget: isSelected ? _buildBadge(category) : null,
            badgePositionPercentageOffset: 1.3,
          );
        }).toList(),
      ),
    );
  }

  Widget _buildBarChart() {
    final maxAmount = _spendingData.map((e) => e.amount).reduce((a, b) => a > b ? a : b);
    
    return BarChart(
      BarChartData(
        alignment: BarChartAlignment.spaceAround,
        maxY: maxAmount * 1.2,
        barTouchData: BarTouchData(enabled: false),
        titlesData: FlTitlesData(
          show: true,
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              getTitlesWidget: (value, meta) {
                if (value.toInt() >= 0 && value.toInt() < _spendingData.length) {
                  return Padding(
                    padding: const EdgeInsets.only(top: 8),
                    child: Icon(
                      _spendingData[value.toInt()].icon,
                      size: 20,
                      color: _spendingData[value.toInt()].color,
                    ),
                  );
                }
                return const Text('');
              },
            ),
          ),
          leftTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 40,
              getTitlesWidget: (value, meta) {
                return Text(
                  '\$${value.toInt()}',
                  style: Theme.of(context).textTheme.bodySmall,
                );
              },
            ),
          ),
          topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
        ),
        borderData: FlBorderData(show: false),
        barGroups: _spendingData.asMap().entries.map((entry) {
          final index = entry.key;
          final category = entry.value;
          
          return BarChartGroupData(
            x: index,
            barRods: [
              BarChartRodData(
                toY: category.amount * _chartAnimation.value,
                color: category.color,
                width: 20,
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(6),
                  topRight: Radius.circular(6),
                ),
              ),
            ],
          );
        }).toList(),
      ),
    );
  }

  Widget _buildBadge(SpendingCategory category) {
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Icon(
        category.icon,
        color: category.color,
        size: 20,
      ),
    );
  }

  Widget _buildLegend() {
    return Wrap(
      spacing: 16,
      runSpacing: 8,
      children: _spendingData.map((category) {
        return Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 12,
              height: 12,
              decoration: BoxDecoration(
                color: category.color,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            const SizedBox(width: 8),
            Text(
              category.name,
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(width: 4),
            Text(
              '\$${category.amount.toStringAsFixed(0)}',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        );
      }).toList(),
    );
  }
}

class SpendingCategory {
  final String name;
  final double amount;
  final Color color;
  final IconData icon;

  SpendingCategory({
    required this.name,
    required this.amount,
    required this.color,
    required this.icon,
  });
}
