# LingoBingo - Expo App

A vocabulary learning game built with Expo that can be installed on your iPhone.

## 🎮 Game Mechanics

The game works as follows:

1. **Computer shows word cards** - The app randomly displays word definitions and images
2. **Player marks their bingo card** - You tap cells on your 4x4 bingo card to mark "I have this word"
3. **Computer reveals answers** - After you answer, the card flips to show synonyms
4. **Get feedback** - Correct answers turn green, incorrect turn red
5. **Get Bingo!** - Complete a row, column, or diagonal to win

## 🚀 Quick Setup

### Prerequisites

1. **Install Node.js** (if not already installed):
   ```bash
   # Download from https://nodejs.org/
   # Or use Homebrew: brew install node
   ```

2. **Install Expo CLI**:
   ```bash
   npm install -g @expo/cli
   ```

### Installation

1. **Navigate to the project**:
   ```bash
   cd LingoBingoExpo
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm start
   ```

### Running on iPhone

1. **Install Expo Go** on your iPhone from the App Store

2. **Scan the QR code** that appears in your terminal or browser

3. **The app will load** on your iPhone instantly!

## 📱 Building for iPhone

### Method 1: EAS Build (Recommended)

1. **Install EAS CLI**:
   ```bash
   npm install -g @expo/eas-cli
   ```

2. **Login to Expo**:
   ```bash
   eas login
   ```

3. **Configure EAS**:
   ```bash
   eas build:configure
   ```

4. **Build for iOS**:
   ```bash
   eas build --platform ios
   ```

5. **Download and install** the .ipa file on your iPhone

### Method 2: Local Build

1. **Install Xcode** from the Mac App Store

2. **Build locally**:
   ```bash
   eas build --platform ios --local
   ```

## 🎯 Game Features

- **4x4 Bingo Grid** with 16 random words from your 19 vocabulary words
- **Three Difficulty Levels**:
  - Easy (Grades 1-5 synonyms)
  - Medium (Original words)
  - Hard (Grades 9-12 synonyms)
- **Interactive Word Cards** with flip animations
- **Score Tracking** and bingo detection
- **Mobile Optimized** for iPhone

## 📁 Project Structure

```
LingoBingoExpo/
├── App.tsx                    # Main app component
├── app.json                   # Expo configuration
├── package.json              # Dependencies
├── src/
│   ├── components/           # Reusable components
│   │   ├── BingoCard.tsx    # 4x4 bingo grid
│   │   └── WordCard.tsx     # Flip card with definitions
│   ├── screens/             # Screen components
│   │   └── GameScreen.tsx   # Main game screen
│   └── data/                # Game data
│       └── wordData.ts      # 19 vocabulary words
└── assets/                  # Images and icons
```

## 🔧 Customization

### Adding More Words

Edit `src/data/wordData.ts`:

```typescript
{
  word: "NewWord",
  definition: "Definition of the word",
  easy: "Easy synonym",
  medium: "Medium synonym", 
  hard: "Hard synonym"
}
```

### Changing Difficulty

The difficulty affects which synonym is shown on the bingo card:
- **Easy**: Shows simple synonyms (Grades 1-5)
- **Medium**: Shows original words
- **Hard**: Shows advanced synonyms (Grades 9-12)

## 🛠️ Troubleshooting

### Common Issues

1. **"Command not found: expo"**
   ```bash
   npm install -g @expo/cli
   ```

2. **Metro bundler issues**
   ```bash
   npm start -- --reset-cache
   ```

3. **Build fails**
   ```bash
   # Clear cache
   expo r -c
   
   # Or restart with clean cache
   npm start -- --clear
   ```

### Development Tips

- Use `console.log()` for debugging
- Check Expo DevTools in browser
- Use Expo Go for quick testing

## 📱 App Store Deployment

To publish to the App Store:

1. **Create an Apple Developer account**
2. **Configure EAS Build**:
   ```bash
   eas build:configure
   ```
3. **Build for production**:
   ```bash
   eas build --platform ios --profile production
   ```
4. **Submit to App Store**:
   ```bash
   eas submit --platform ios
   ```

## 🎉 Features

- ✅ Complete game logic with correct mechanics
- ✅ Beautiful UI with animations
- ✅ Score tracking and bingo detection
- ✅ Three difficulty levels
- ✅ Mobile-optimized design
- ✅ TypeScript for type safety
- ✅ Ready for iPhone deployment
- ✅ Easy Expo development workflow

## 🚀 Advantages of Expo

- **Faster development** - No complex native setup
- **Easy testing** - Expo Go app for instant testing
- **Cross-platform** - Works on iOS and Android
- **Cloud builds** - No need for Xcode locally
- **Over-the-air updates** - Update app without App Store

The app is now ready to be built and installed on your iPhone! Follow the setup instructions above to get started. 