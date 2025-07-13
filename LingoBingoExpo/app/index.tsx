import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  StatusBar,
  Dimensions,
} from 'react-native';
import { DifficultyLevel } from '../src/data/wordData';
import GameScreen from '../src/screens/GameScreen';

const { width } = Dimensions.get('window');

const Page: React.FC = () => {
  const [currentScreen, setCurrentScreen] = useState<'menu' | 'game'>('menu');
  const [difficulty, setDifficulty] = useState<DifficultyLevel>(DifficultyLevel.MEDIUM);
  const [score, setScore] = useState(0);
  const [bingos, setBingos] = useState(0);

  const startGame = () => {
    setCurrentScreen('game');
  };

  const backToMenu = () => {
    setCurrentScreen('menu');
  };

  const handleGameEnd = (finalScore: number, finalBingos: number) => {
    setScore(finalScore);
    setBingos(finalBingos);
    setCurrentScreen('menu');
  };

  if (currentScreen === 'game') {
    return (
      <SafeAreaView style={styles.container}>
        <StatusBar barStyle="dark-content" backgroundColor="#f8f9fa" />
        <GameScreen
          difficulty={difficulty}
          onGameEnd={handleGameEnd}
          onBackToMenu={backToMenu}
        />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#667eea" />
      <View style={styles.menuContainer}>
        <Text style={styles.title}>LingoBingo</Text>
        <Text style={styles.subtitle}>Vocabulary Learning Game</Text>
        
        <View style={styles.difficultyContainer}>
          <Text style={styles.difficultyLabel}>Select Difficulty:</Text>
          <View style={styles.difficultyButtons}>
            <TouchableOpacity
              style={[
                styles.difficultyButton,
                difficulty === DifficultyLevel.EASY && styles.selectedDifficulty,
              ]}
              onPress={() => setDifficulty(DifficultyLevel.EASY)}
            >
              <Text style={[
                styles.difficultyButtonText,
                difficulty === DifficultyLevel.EASY && styles.selectedDifficultyText,
              ]}>
                Easy
              </Text>
            </TouchableOpacity>
            
            <TouchableOpacity
              style={[
                styles.difficultyButton,
                difficulty === DifficultyLevel.MEDIUM && styles.selectedDifficulty,
              ]}
              onPress={() => setDifficulty(DifficultyLevel.MEDIUM)}
            >
              <Text style={[
                styles.difficultyButtonText,
                difficulty === DifficultyLevel.MEDIUM && styles.selectedDifficultyText,
              ]}>
                Medium
              </Text>
            </TouchableOpacity>
            
            <TouchableOpacity
              style={[
                styles.difficultyButton,
                difficulty === DifficultyLevel.HARD && styles.selectedDifficulty,
              ]}
              onPress={() => setDifficulty(DifficultyLevel.HARD)}
            >
              <Text style={[
                styles.difficultyButtonText,
                difficulty === DifficultyLevel.HARD && styles.selectedDifficultyText,
              ]}>
                Hard
              </Text>
            </TouchableOpacity>
          </View>
        </View>

        <TouchableOpacity style={styles.startButton} onPress={startGame}>
          <Text style={styles.startButtonText}>Start Game</Text>
        </TouchableOpacity>

        {score > 0 && (
          <View style={styles.statsContainer}>
            <Text style={styles.statsText}>Last Game Score: {score}</Text>
            <Text style={styles.statsText}>Bingos: {bingos}</Text>
          </View>
        )}
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#667eea',
  },
  menuContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  title: {
    fontSize: 48,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 18,
    color: 'rgba(255, 255, 255, 0.8)',
    marginBottom: 60,
    textAlign: 'center',
  },
  difficultyContainer: {
    marginBottom: 40,
    alignItems: 'center',
  },
  difficultyLabel: {
    fontSize: 18,
    color: 'white',
    marginBottom: 20,
    fontWeight: '600',
  },
  difficultyButtons: {
    flexDirection: 'row',
    gap: 15,
  },
  difficultyButton: {
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 25,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    borderWidth: 2,
    borderColor: 'rgba(255, 255, 255, 0.3)',
  },
  selectedDifficulty: {
    backgroundColor: 'white',
    borderColor: 'white',
  },
  difficultyButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  selectedDifficultyText: {
    color: '#667eea',
  },
  startButton: {
    backgroundColor: 'white',
    paddingHorizontal: 40,
    paddingVertical: 15,
    borderRadius: 30,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 4.65,
    elevation: 8,
  },
  startButtonText: {
    color: '#667eea',
    fontSize: 18,
    fontWeight: 'bold',
  },
  statsContainer: {
    marginTop: 40,
    alignItems: 'center',
  },
  statsText: {
    color: 'white',
    fontSize: 16,
    marginBottom: 5,
  },
});

export default Page;
