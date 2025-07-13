import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  Dimensions,
} from 'react-native';
import { WordData, DifficultyLevel, wordData } from '../data/wordData';
import BingoCard from '../components/BingoCard';

const { width, height } = Dimensions.get('window');

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
  const [currentWord, setCurrentWord] = useState<WordData | null>(null);
  const [markedCells, setMarkedCells] = useState<boolean[][]>([
    [false, false, false, false],
    [false, false, false, false],
    [false, false, false, false],
    [false, false, false, false],
  ]);
  const [correctAnswers, setCorrectAnswers] = useState<(boolean | null)[][]>([
    [null, null, null, null],
    [null, null, null, null],
    [null, null, null, null],
    [null, null, null, null],
  ]);
  const [gamePhase, setGamePhase] = useState<'placing' | 'checking' | 'complete'>('placing');
  const [score, setScore] = useState(0);
  const [bingos, setBingos] = useState(0);
  const [usedWords, setUsedWords] = useState<WordData[]>([]);

  useEffect(() => {
    startNewGame();
  }, []);

  const startNewGame = () => {
    // Select 16 random words for the bingo card (this stays constant)
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
      [null, null, null, null],
      [null, null, null, null],
      [null, null, null, null],
      [null, null, null, null],
    ]);
    setScore(0);
    setBingos(0);
    setUsedWords([]);
    setGamePhase('placing');
    
    // Show first word
    showNextWord();
  };

  const showNextWord = () => {
    try {
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
      setUsedWords([...usedWords, randomWord]);
      setGamePhase('placing');
      
      // Reset marked cells for new word (correct answers persist)
      setMarkedCells([
        [false, false, false, false],
        [false, false, false, false],
        [false, false, false, false],
        [false, false, false, false],
      ]);
      // Note: correctAnswers array is NOT reset - green tiles persist!
    } catch (error) {
      console.error('Error in showNextWord:', error);
      // Fallback: restart game
      startNewGame();
    }
  };

  const handleCellPress = (row: number, col: number) => {
    if (gamePhase !== 'placing') return;
    
    const newMarkedCells = [...markedCells];
    newMarkedCells[row][col] = !newMarkedCells[row][col]; // Toggle
    setMarkedCells(newMarkedCells);
  };

  const handleDonePress = () => {
    // Check if the current word is on the bingo card
    const wordIndex = bingoWords.findIndex(word => word.word === currentWord?.word);
    const wordIsOnCard = wordIndex !== -1;
    
    // Check which marked cells are correct
    const newCorrectAnswers = [...correctAnswers];
    let correctCount = 0;
    let feedbackMessage = '';
    
    if (wordIsOnCard) {
      // Word is on the card - check marked cells
      for (let row = 0; row < 4; row++) {
        for (let col = 0; col < 4; col++) {
          const cellWordIndex = row * 4 + col;
          const cellWord = bingoWords[cellWordIndex];
          
          if (markedCells[row][col]) {
            // Check if this word matches the current word's definition
            if (currentWord && cellWord.word === currentWord.word) {
              newCorrectAnswers[row][col] = true;
              correctCount++;
              feedbackMessage += `${cellWord.word}: ✅ Correct\n`;
            } else {
              newCorrectAnswers[row][col] = false;
              feedbackMessage += `${cellWord.word}: ❌ Incorrect\n`;
            }
          } else if (currentWord && cellWord.word === currentWord.word) {
            // Word is on the card but user didn't mark it - mark as incorrect
            newCorrectAnswers[row][col] = false;
            feedbackMessage += `${cellWord.word}: ❌ You missed this one!\n`;
          }
        }
      }
    } else {
      // Word is NOT on the card - all marked cells are incorrect
      for (let row = 0; row < 4; row++) {
        for (let col = 0; col < 4; col++) {
          if (markedCells[row][col]) {
            const cellWordIndex = row * 4 + col;
            const cellWord = bingoWords[cellWordIndex];
            newCorrectAnswers[row][col] = false;
            feedbackMessage += `${cellWord.word}: ❌ Incorrect\n`;
          }
        }
      }
    }
    
    setCorrectAnswers(newCorrectAnswers);
    setGamePhase('checking');
    
    // Update score
    const newScore = score + (correctCount * 10);
    setScore(newScore);
    
    // Show feedback
    if (wordIsOnCard) {
      feedbackMessage = `The word "${currentWord?.word}" is on your bingo card!\n\n${feedbackMessage}`;
    } else {
      feedbackMessage = `The word "${currentWord?.word}" is NOT on your bingo card.\n\n${feedbackMessage}`;
    }
    
    // Check for bingo
    if (checkBingo(newCorrectAnswers)) {
      setBingos(bingos + 1);
      Alert.alert(
        '🎉 BINGO! 🎉',
        `Congratulations! You got a bingo!\n\n${feedbackMessage}`,
        [
          {
            text: 'Continue',
            onPress: () => {
              startNewGame();
            },
          },
        ]
      );
    } else {
      Alert.alert(
        'Results',
        feedbackMessage || 'No cells were marked.',
        [
          {
            text: 'Continue',
            onPress: () => {
              showNextWord();
            },
          },
        ]
      );
    }
  };

  const checkBingo = (answers: (boolean | null)[][]): boolean => {
    // Check rows
    for (let row = 0; row < 4; row++) {
      if (answers[row].every(cell => cell === true)) {
        return true;
      }
    }
    
    // Check columns
    for (let col = 0; col < 4; col++) {
      if (answers.every(row => row[col] === true)) {
        return true;
      }
    }
    
    // Check diagonals
    if (answers[0][0] === true && answers[1][1] === true && 
        answers[2][2] === true && answers[3][3] === true) {
      return true;
    }
    
    if (answers[0][3] === true && answers[1][2] === true && 
        answers[2][1] === true && answers[3][0] === true) {
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

  if (!currentWord) {
    return (
      <View style={styles.container}>
        <Text>Loading...</Text>
      </View>
    );
  }

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

      {/* Word Card (Top) */}
      <View style={styles.wordCardContainer}>
        <View style={styles.wordCard}>
          <View style={styles.cardHeader}>
            <Text style={styles.cardTitle}>
              {gamePhase === 'checking' ? 'Answer' : 'Definition'}
            </Text>
          </View>
          <View style={styles.cardBody}>
            {gamePhase === 'checking' ? (
              <>
                <Text style={styles.answerWordCentered}>{currentWord.word}</Text>
                <Text style={styles.synonymTitle}>Synonyms:</Text>
                <Text style={styles.synonymText}>
                  Easy: {currentWord.easy} | Medium: {currentWord.medium} | Hard: {currentWord.hard}
                </Text>
              </>
            ) : (
              <>
                <Text style={styles.definition}>{currentWord.definition}</Text>
                <View style={styles.imagePlaceholder}>
                  <Text style={styles.imageText}>📚</Text>
                </View>
              </>
            )}
          </View>
        </View>
      </View>

      {/* Bingo Card (Bottom) */}
      <View style={styles.bingoContainer}>
        <Text style={styles.bingoTitle}>Bingo Card</Text>
        <BingoCard
          words={bingoWords}
          difficulty={difficulty}
          markedCells={markedCells}
          correctAnswers={correctAnswers}
          onCellPress={handleCellPress}
          gamePhase={gamePhase}
        />
      </View>

      {/* Instructions and Controls */}
      <View style={styles.controlsContainer}>
        {gamePhase === 'placing' && (
          <>
            <Text style={styles.instructionText}>
              Tap cells to mark words you think match the definition
            </Text>
            <TouchableOpacity 
              style={styles.doneButton} 
              onPress={handleDonePress}
            >
              <Text style={styles.doneButtonText}>Done</Text>
            </TouchableOpacity>
          </>
        )}
        
        {gamePhase === 'checking' && (
          <TouchableOpacity 
            style={styles.continueButton} 
            onPress={() => showNextWord()}
          >
            <Text style={styles.continueButtonText}>Continue</Text>
          </TouchableOpacity>
        )}
        
        {gamePhase === 'complete' && (
          <Text style={styles.completeText}>
            Next word coming up...
          </Text>
        )}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
    padding: 15,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: 'white',
    padding: 10,
    borderRadius: 8,
    marginBottom: 10,
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
    gap: 15,
  },
  scoreText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  bingosText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#667eea',
  },
  pauseButton: {
    padding: 5,
  },
  pauseButtonText: {
    fontSize: 16,
  },
  wordCardContainer: {
    marginBottom: 10,
  },
  wordCard: {
    backgroundColor: 'white',
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.2,
    shadowRadius: 3,
    elevation: 5,
  },
  cardHeader: {
    backgroundColor: '#667eea',
    padding: 12,
    borderTopLeftRadius: 10,
    borderTopRightRadius: 10,
    alignItems: 'center',
  },
  cardTitle: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  cardBody: {
    padding: 15,
  },
  definition: {
    fontSize: 14,
    lineHeight: 20,
    color: '#333',
    marginBottom: 10,
    textAlign: 'center',
  },
  imagePlaceholder: {
    height: 60,
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#dee2e6',
    borderStyle: 'dashed',
  },
  imageText: {
    fontSize: 24,
  },
  answerSection: {
    backgroundColor: '#f8f9fa',
    padding: 12,
    borderBottomLeftRadius: 10,
    borderBottomRightRadius: 10,
    alignItems: 'center',
  },
  answerTitle: {
    fontSize: 12,
    color: '#666',
    marginBottom: 3,
  },
  answerWord: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#667eea',
  },
  answerWordCentered: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#667eea',
    textAlign: 'center',
    marginBottom: 10,
  },
  bingoContainer: {
    flex: 1,
    marginBottom: 10,
  },
  bingoTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center',
    marginBottom: 8,
  },
  controlsContainer: {
    backgroundColor: 'white',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  instructionText: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
    marginBottom: 10,
  },
  doneButton: {
    backgroundColor: '#28a745',
    paddingHorizontal: 30,
    paddingVertical: 10,
    borderRadius: 20,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.2,
    shadowRadius: 3,
    elevation: 4,
  },
  doneButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: 'bold',
  },
  checkingText: {
    fontSize: 14,
    color: '#667eea',
    fontWeight: '600',
  },
  completeText: {
    fontSize: 14,
    color: '#28a745',
    fontWeight: '600',
  },
  synonymTitle: {
    fontSize: 12,
    color: '#666',
    marginTop: 8,
    marginBottom: 3,
    textAlign: 'center',
  },
  synonymText: {
    fontSize: 11,
    color: '#333',
    textAlign: 'center',
    lineHeight: 16,
  },
  continueButton: {
    backgroundColor: '#007bff',
    paddingHorizontal: 20,
    paddingVertical: 8,
    borderRadius: 15,
    marginTop: 10,
  },
  continueButtonText: {
    color: 'white',
    fontSize: 12,
    fontWeight: 'bold',
  },
});

export default GameScreen; 