/**
 * Below are the colors that are used in the app. The colors are defined in the light and dark mode.
 * There are many other ways to style your app. For example, [Nativewind](https://www.nativewind.dev/), [Tamagui](https://tamagui.dev/), [unistyles](https://reactnativeunistyles.vercel.app), etc.
 */

import { Platform } from 'react-native';

const tintColorLight = '#0a7ea4';
const tintColorDark = '#fff';

export const Colors = {
  light: {
    primary: '#1E88E5', // Bleu principal
    accent: '#7E57C2', // Violet accent
    background: '#F4F6F8', // Fond clair
    surface: 'rgba(255, 255, 255, 0.7)',
    text: '#1C1C1E',
    textSecondary: '#6C757D',
    border: 'rgba(0, 0, 0, 0.1)',
    tint: '#1E88E5',
    success: '#43A047', // Vert succès
    error: '#E53935', // Rouge critique
    warning: '#FB8C00', // Orange alerte
    white: '#FFFFFF',
    icon: '#6C757D',
    tabIconDefault: '#6C757D',
    tabIconSelected: '#1E88E5',
  },
  dark: {
    primary: '#1E88E5',
    accent: '#7E57C2',
    background: '#000000',
    surface: 'rgba(28, 28, 30, 0.7)',
    text: '#FFFFFF',
    textSecondary: '#AEAEB2',
    border: 'rgba(255, 255, 255, 0.15)',
    tint: '#1E88E5',
    success: '#43A047',
    error: '#E53935',
    warning: '#FB8C00',
    white: '#FFFFFF',
    icon: '#AEAEB2',
    tabIconDefault: '#AEAEB2',
    tabIconSelected: '#1E88E5',
  },
};

export const Glass = {
  light: {
    backgroundColor: 'rgba(255, 255, 255, 0.65)',
    borderColor: 'rgba(255, 255, 255, 0.3)',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.1,
    shadowRadius: 24,
  },
  dark: {
    backgroundColor: 'rgba(28, 28, 30, 0.65)',
    borderColor: 'rgba(255, 255, 255, 0.1)',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.4,
    shadowRadius: 24,
  },
};

export const Fonts = Platform.select({
  ios: {
    /** iOS `UIFontDescriptorSystemDesignDefault` */
    sans: 'system-ui',
    /** iOS `UIFontDescriptorSystemDesignSerif` */
    serif: 'ui-serif',
    /** iOS `UIFontDescriptorSystemDesignRounded` */
    rounded: 'ui-rounded',
    /** iOS `UIFontDescriptorSystemDesignMonospaced` */
    mono: 'ui-monospace',
  },
  default: {
    sans: 'normal',
    serif: 'serif',
    rounded: 'normal',
    mono: 'monospace',
  },
  web: {
    sans: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
    serif: "Georgia, 'Times New Roman', serif",
    rounded: "'SF Pro Rounded', 'Hiragino Maru Gothic ProN', Meiryo, 'MS PGothic', sans-serif",
    mono: "SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace",
  },
});
