import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  Dimensions,
  Modal,
  Animated,
} from 'react-native';
import { WordData, DifficultyLevel, wordData, getWordByDifficulty } from '../data/wordData';
import BingoCard from '../components/BingoCard';
import WordCard from '../components/WordCard';

const { width } = Dimensions.get('window');

interface GameScreenProps {
  difficulty: DifficultyLevel;
  onGameEnd: (score: number, bingos: number) => void;
  onBackToMenu: () => void;
}

const GameScreen: React.FC<GameScreenProps> = ({
  difficulty,
  onGameEnd,
  onBackToMenu,
}) => {
  const [bingoWords, setBingoWords] = useState<WordData[]>([]);
  const [markedCells, setMarkedCells] = useState<boolean[][]>([
    [false, false, false, false],
    [false, false, false, false],
    [false, false, false, false],
    [false, false, false, false],
  ]);
  const [correctAnswers, setCorrectAnswers] = useState<boolean[][]>([
    [false, false, false, false],
    [false, false, false, false],
    [false, false, false, false],
    [false, false, false, false],
  ]);
  const [currentWord, setCurrentWord] = useState<WordData | null>(null);
  const [showWordCard, setShowWordCard] = useState(false);
  const [score, setScore] = useState(0);
  const [bingos, setBingos] = useState(0);
  const [usedWords, setUsedWords] = useState<WordData[]>([]);

  useEffect(() => {
    startNewGame();
  }, []);

  const startNewGame = () => {
    // Select 16 random words for the bingo card
    const shuffled = [...wordData].sort(() => Math.random() - 0.5);
    const selectedWords = shuffled.slice(0, 16);
    setBingoWords(selectedWords);
    
    // Reset game state
    setMarkedCells([
      [false, false, false, false],
      [false, false, false, false],
      [false, false, false, false],
      [false, false, false, false],
    ]);
    setCorrectAnswers([
      [false, false, false, false],
      [false, false, false, false],
      [false, false, false, false],
      [false, false, false, false],
    ]);
    setScore(0);
    setBingos(0);
    setUsedWords([]);
    
    // Show first word after a short delay
    setTimeout(() => {
      showNextWord();
    }, 1000);
  };

  const showNextWord = () => {
    // Select a random word that hasn't been used yet
    const availableWords = wordData.filter(word => !usedWords.includes(word));
    if (availableWords.length === 0) {
      // All words used, restart
      setUsedWords([]);
      showNextWord();
      return;
    }
    
    const randomWord = availableWords[Math.floor(Math.random() * availableWords.length)];
    setCurrentWord(randomWord);
    setShowWordCard(true);
    setUsedWords([...usedWords, randomWord]);
  };

  const handleCellPress = (row: number, col: number) => {
    if (markedCells[row][col]) return; // Already marked
    
    const newMarkedCells = [...markedCells];
    newMarkedCells[row][col] = true;
    setMarkedCells(newMarkedCells);
  };

  const handleWordCardAnswer = (isCorrect: boolean) => {
    if (!currentWord) return;
    
    // Find if the current word is on the bingo card
    const wordIndex = bingoWords.findIndex(word => word.word === currentWord.word);
    const hasWord = wordIndex !== -1;
    
    // Check if player's answer was correct
    const playerCorrect = (hasWord && isCorrect) || (!hasWord && !isCorrect);
    
    if (playerCorrect) {
      setScore(score + 10);
    }
    
    // Update correct answers array
    const newCorrectAnswers = [...correctAnswers];
    if (hasWord) {
      const row = Math.floor(wordIndex / 4);
      const col = wordIndex % 4;
      newCorrectAnswers[row][col] = true;
      setCorrectAnswers(newCorrectAnswers);
    }
    
    // Check for bingo
    if (checkBingo()) {
      setBingos(bingos + 1);
      setScore(score + 100);
      Alert.alert(
        '🎉 BINGO! 🎉',
        'Congratulations! You got a bingo!',
        [
          {
            text: 'Continue',
            onPress: () => {
              setShowWordCard(false);
              setTimeout(() => showNextWord(), 1000);
            },
          },
        ]
      );
    } else {
      setShowWordCard(false);
      setTimeout(() => showNextWord(), 1000);
    }
  };

  const checkBingo = (): boolean => {
    // Check rows
    for (let row = 0; row < 4; row++) {
      if (correctAnswers[row].every(cell => cell)) {
        return true;
      }
    }
    
    // Check columns
    for (let col = 0; col < 4; col++) {
      if (correctAnswers.every(row => row[col])) {
        return true;
      }
    }
    
    // Check diagonals
    if (correctAnswers[0][0] && correctAnswers[1][1] && 
        correctAnswers[2][2] && correctAnswers[3][3]) {
      return true;
    }
    
    if (correctAnswers[0][3] && correctAnswers[1][2] && 
        correctAnswers[2][1] && correctAnswers[3][0]) {
      return true;
    }
    
    return false;
  };

  const handlePause = () => {
    Alert.alert(
      'Game Paused',
      'What would you like to do?',
      [
        {
          text: 'Resume',
          style: 'default',
        },
        {
          text: 'New Game',
          onPress: startNewGame,
        },
        {
          text: 'Main Menu',
          onPress: onBackToMenu,
        },
      ]
    );
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.scoreContainer}>
          <Text style={styles.scoreText}>Score: {score}</Text>
          <Text style={styles.bingosText}>Bingos: {bingos}</Text>
        </View>
        <TouchableOpacity style={styles.pauseButton} onPress={handlePause}>
          <Text style={styles.pauseButtonText}>⏸️</Text>
        </TouchableOpacity>
      </View>

      {/* Bingo Card */}
      <View style={styles.bingoContainer}>
        <BingoCard
          words={bingoWords}
          difficulty={difficulty}
          markedCells={markedCells}
          correctAnswers={correctAnswers}
          onCellPress={handleCellPress}
        />
      </View>

      {/* Word Card Modal */}
      {currentWord && (
        <WordCard
          word={currentWord}
          isVisible={showWordCard}
          onFlip={() => {}}
          onAnswer={handleWordCardAnswer}
        />
      )}

      {/* Instructions */}
      <View style={styles.instructions}>
        <Text style={styles.instructionText}>
          Tap cells on your bingo card to mark them as "I have this word"
        </Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
    padding: 20,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 10,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  scoreContainer: {
    flexDirection: 'row',
    gap: 20,
  },
  scoreText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  bingosText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#667eea',
  },
  pauseButton: {
    padding: 10,
  },
  pauseButtonText: {
    fontSize: 20,
  },
  bingoContainer: {
    flex: 1,
    justifyContent: 'center',
  },
  instructions: {
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 10,
    marginTop: 20,
  },
  instructionText: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
  },
});

export default GameScreen; 