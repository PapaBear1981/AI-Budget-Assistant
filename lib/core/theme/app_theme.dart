import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_fonts/google_fonts.dart';

/// Gothic-inspired theme for AI Budget Assistant
///
/// This theme implements a dark gothic aesthetic with:
/// - Deep blacks (#000000, #0A0A0A, #1A1A1A) for backgrounds
/// - Silver/metallic grays (#C0C0C0, #808080, #404040) for secondary elements
/// - Deep reds (#8B0000, #A52A2A, #DC143C) for accent colors
/// - Dark navy blues (#000080, #191970, #2F4F4F) for contrast elements
/// - Playfair Display font for headers (gothic-inspired serif)
/// - Open Sans font for body text (clean, readable sans-serif)
/// - Preserved vibrant colors for charts and data visualization
class AppTheme {
  // Gothic-Inspired Color Scheme
  // Primary Gothic Colors - Deep blacks and metallic grays
  static const Color primaryColor = Color(0xFF8B0000); // Deep red accent
  static const Color secondaryColor = Color(0xFF000080); // Dark navy blue
  static const Color tertiaryColor = Color(0xFFA52A2A); // Brown red
  static const Color errorColor = Color(0xFFDC143C); // Crimson red
  static const Color successColor = Color(0xFF10B981); // Keep vibrant green for data
  static const Color warningColor = Color(0xFFF59E0B); // Keep vibrant orange for data

  // Gothic Background Colors - Deep blacks
  static const Color darkBackground = Color(0xFF000000); // Pure black
  static const Color cardBackground = Color(0xFF0A0A0A); // Very dark gray
  static const Color sidebarBackground = Color(0xFF1A1A1A); // Dark gray

  // Gothic Metallic Colors - Silver/Gray tones
  static const Color lightSilver = Color(0xFFC0C0C0); // Light silver
  static const Color mediumSilver = Color(0xFF808080); // Medium gray
  static const Color darkSilver = Color(0xFF404040); // Dark gray

  // Gothic Accent Colors - Deep reds and navy blues
  static const Color deepRed = Color(0xFF8B0000); // Dark red
  static const Color brownRed = Color(0xFFA52A2A); // Brown red
  static const Color crimsonRed = Color(0xFFDC143C); // Crimson
  static const Color darkNavy = Color(0xFF000080); // Navy blue
  static const Color midnightBlue = Color(0xFF191970); // Midnight blue
  static const Color darkSlateGray = Color(0xFF2F4F4F); // Dark slate gray

  // Financial Colors - Keep vibrant for data visualization
  static const Color incomeColor = Color(0xFF10B981); // Vibrant green
  static const Color expenseColor = Color(0xFFEF4444); // Vibrant red
  static const Color savingsColor = Color(0xFF3B82F6); // Vibrant blue
  static const Color budgetColor = Color(0xFF8B5CF6); // Vibrant purple

  // Chart Colors - Keep all existing vibrant colors for data visualization
  static const List<Color> chartColors = [
    Color(0xFF10B981), // Green
    Color(0xFF3B82F6), // Blue
    Color(0xFF8B5CF6), // Purple
    Color(0xFFEF4444), // Red
    Color(0xFFF59E0B), // Orange
    Color(0xFF06B6D4), // Cyan
    Color(0xFFEC4899), // Pink
    Color(0xFF84CC16), // Lime
  ];

  // Gothic Gradient Colors
  static const List<Color> backgroundGradient = [
    Color(0xFF000000), // Pure black
    Color(0xFF0A0A0A), // Very dark gray
    Color(0xFF1A1A1A), // Dark gray
  ];

  // Typography - Gothic-inspired fonts using Google Fonts
  static TextStyle get headingFont => GoogleFonts.playfairDisplay(); // Gothic-inspired serif for headers
  static TextStyle get bodyFont => GoogleFonts.openSans(); // Clean sans-serif for body text

  // Animation durations
  static const Duration fastAnimation = Duration(milliseconds: 200);
  static const Duration normalAnimation = Duration(milliseconds: 300);
  static const Duration slowAnimation = Duration(milliseconds: 500);

  // Elevation levels
  static const double cardElevation = 4.0;
  static const double modalElevation = 8.0;
  static const double fabElevation = 6.0;

  static ThemeData get lightTheme {
    // For now, return dark theme as the design is dark-focused
    return darkTheme;
  }

  static ThemeData get darkTheme {
    final colorScheme = ColorScheme.dark(
      primary: primaryColor, // Deep red
      secondary: secondaryColor, // Dark navy
      tertiary: tertiaryColor, // Brown red
      surface: cardBackground, // Very dark gray
      surfaceContainerHighest: darkSilver, // Dark gray for elevated surfaces
      error: errorColor, // Crimson red
      onPrimary: lightSilver, // Light silver text on red
      onSecondary: lightSilver, // Light silver text on navy
      onTertiary: lightSilver, // Light silver text on brown red
      onSurface: lightSilver, // Light silver text on dark surfaces
      onError: Colors.white, // White text on error red
      outline: mediumSilver, // Medium gray for borders
      outlineVariant: darkSilver, // Dark gray for subtle borders
    );

    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      textTheme: _buildTextTheme(),
      brightness: Brightness.dark,
      scaffoldBackgroundColor: darkBackground, // Pure black background

      // App Bar Theme with gothic styling
      appBarTheme: AppBarTheme(
        centerTitle: false,
        elevation: 0,
        scrolledUnderElevation: 0,
        backgroundColor: Colors.transparent,
        foregroundColor: lightSilver,
        titleTextStyle: GoogleFonts.playfairDisplay(
          fontSize: 24,
          fontWeight: FontWeight.w700,
          color: lightSilver,
        ),
        systemOverlayStyle: const SystemUiOverlayStyle(
          statusBarColor: Colors.transparent,
          statusBarIconBrightness: Brightness.light,
          systemNavigationBarColor: darkBackground,
          systemNavigationBarIconBrightness: Brightness.light,
        ),
      ),

      // Gothic Card Theme
      cardTheme: CardTheme(
        elevation: 8,
        color: cardBackground, // Very dark gray
        shadowColor: Colors.black.withOpacity(0.5), // Deeper shadows for gothic feel
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
          side: BorderSide(
            color: darkSilver.withOpacity(0.3), // Subtle dark gray border
            width: 1,
          ),
        ),
        clipBehavior: Clip.antiAlias,
        margin: const EdgeInsets.all(8),
      ),
      
      // Elevated Button Theme
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          elevation: 2,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),
      
      // Input Decoration Theme
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: colorScheme.surfaceContainerHighest.withOpacity(0.3),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide.none,
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: colorScheme.primary, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: colorScheme.error, width: 2),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
      ),
      
      // Navigation Rail Theme
      navigationRailTheme: NavigationRailThemeData(
        backgroundColor: colorScheme.surface,
        selectedIconTheme: IconThemeData(color: colorScheme.primary),
        unselectedIconTheme: IconThemeData(color: colorScheme.onSurface.withOpacity(0.6)),
        selectedLabelTextStyle: TextStyle(color: colorScheme.primary),
        unselectedLabelTextStyle: TextStyle(color: colorScheme.onSurface.withOpacity(0.6)),
      ),
      
      // Bottom Navigation Bar Theme
      bottomNavigationBarTheme: BottomNavigationBarThemeData(
        backgroundColor: colorScheme.surface,
        selectedItemColor: colorScheme.primary,
        unselectedItemColor: colorScheme.onSurface.withOpacity(0.6),
        type: BottomNavigationBarType.fixed,
        elevation: 8,
      ),

      // FloatingActionButton Theme
      floatingActionButtonTheme: FloatingActionButtonThemeData(
        elevation: fabElevation,
        highlightElevation: fabElevation + 2,
        backgroundColor: colorScheme.primaryContainer,
        foregroundColor: colorScheme.onPrimaryContainer,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
      ),

      // Chip Theme
      chipTheme: ChipThemeData(
        backgroundColor: colorScheme.surfaceContainerHighest,
        selectedColor: colorScheme.secondaryContainer,
        disabledColor: colorScheme.onSurface.withOpacity(0.12),
        labelStyle: TextStyle(color: colorScheme.onSurface.withOpacity(0.8)),
        secondaryLabelStyle: TextStyle(color: colorScheme.onSecondaryContainer),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),

      // Dialog Theme
      dialogTheme: DialogTheme(
        elevation: modalElevation,
        backgroundColor: colorScheme.surface,
        surfaceTintColor: colorScheme.surfaceTint,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
      ),



      // Snackbar Theme
      snackBarTheme: SnackBarThemeData(
        backgroundColor: colorScheme.inverseSurface,
        contentTextStyle: TextStyle(color: colorScheme.onInverseSurface),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        behavior: SnackBarBehavior.floating,
        elevation: 6,
      ),

      // Page Transitions
      pageTransitionsTheme: const PageTransitionsTheme(
        builders: {
          TargetPlatform.android: CupertinoPageTransitionsBuilder(),
          TargetPlatform.iOS: CupertinoPageTransitionsBuilder(),
          TargetPlatform.windows: FadeUpwardsPageTransitionsBuilder(),
          TargetPlatform.macOS: CupertinoPageTransitionsBuilder(),
          TargetPlatform.linux: FadeUpwardsPageTransitionsBuilder(),
        },
      ),
    );
  }

  // Helper method to build gothic-inspired text theme
  static TextTheme _buildTextTheme() {
    return TextTheme(
      // Display styles - Gothic serif for large text
      displayLarge: GoogleFonts.playfairDisplay(
        fontSize: 32,
        fontWeight: FontWeight.w700,
        color: lightSilver,
      ),
      displayMedium: GoogleFonts.playfairDisplay(
        fontSize: 28,
        fontWeight: FontWeight.w600,
        color: lightSilver,
      ),
      displaySmall: GoogleFonts.playfairDisplay(
        fontSize: 24,
        fontWeight: FontWeight.w600,
        color: lightSilver,
      ),

      // Headline styles - Gothic serif for headers
      headlineLarge: GoogleFonts.playfairDisplay(
        fontSize: 22,
        fontWeight: FontWeight.w600,
        color: lightSilver,
      ),
      headlineMedium: GoogleFonts.playfairDisplay(
        fontSize: 20,
        fontWeight: FontWeight.w500,
        color: lightSilver,
      ),
      headlineSmall: GoogleFonts.playfairDisplay(
        fontSize: 18,
        fontWeight: FontWeight.w500,
        color: lightSilver,
      ),

      // Title styles - Clean sans-serif for titles
      titleLarge: GoogleFonts.openSans(
        fontSize: 16,
        fontWeight: FontWeight.w600,
        color: lightSilver,
      ),
      titleMedium: GoogleFonts.openSans(
        fontSize: 14,
        fontWeight: FontWeight.w500,
        color: mediumSilver,
      ),
      titleSmall: GoogleFonts.openSans(
        fontSize: 12,
        fontWeight: FontWeight.w500,
        color: mediumSilver,
      ),

      // Body styles - Clean sans-serif for body text
      bodyLarge: GoogleFonts.openSans(
        fontSize: 14,
        fontWeight: FontWeight.w400,
        color: lightSilver,
      ),
      bodyMedium: GoogleFonts.openSans(
        fontSize: 12,
        fontWeight: FontWeight.w400,
        color: mediumSilver,
      ),
      bodySmall: GoogleFonts.openSans(
        fontSize: 11,
        fontWeight: FontWeight.w400,
        color: mediumSilver,
      ),
    );
  }

  // Helper methods for accessing theme colors
  static Color getChartColor(int index) {
    return chartColors[index % chartColors.length];
  }

  static List<Color> getChartColorPalette() {
    return chartColors;
  }

  // Gothic color getters for easy access
  static Color get gothicBackground => darkBackground;
  static Color get gothicCard => cardBackground;
  static Color get gothicSidebar => sidebarBackground;
  static Color get gothicPrimary => primaryColor;
  static Color get gothicSecondary => secondaryColor;
  static Color get gothicAccent => tertiaryColor;
}
