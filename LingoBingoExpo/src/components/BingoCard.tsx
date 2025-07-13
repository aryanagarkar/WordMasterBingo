import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Dimensions,
} from 'react-native';
import { WordData, DifficultyLevel, getWordByDifficulty } from '../data/wordData';

const { width } = Dimensions.get('window');
const cellSize = Math.min((width - 80) / 4, 80); // 4x4 grid with margins, max 80px per cell

interface BingoCardProps {
  words: WordData[];
  difficulty: DifficultyLevel;
  markedCells: boolean[][];
  correctAnswers: (boolean | null)[][];
  onCellPress: (row: number, col: number) => void;
  gamePhase: 'placing' | 'checking' | 'complete';
}

const BingoCard: React.FC<BingoCardProps> = ({
  words,
  difficulty,
  markedCells,
  correctAnswers,
  onCellPress,
  gamePhase,
}) => {
  const renderCell = (row: number, col: number) => {
    const index = row * 4 + col;
    const word = words[index];
    const isMarked = markedCells[row]?.[col] || false;
    const isCorrect = correctAnswers[row]?.[col];
    
    let cellStyle: any = styles.cell;
    let textStyle: any = styles.cellText;
    
    if (isMarked) {
      if (gamePhase === 'placing') {
        // During placing phase, show green for marked cells
        cellStyle = [styles.cell, styles.markedCell];
        textStyle = [styles.cellText, styles.markedText];
      } else if (gamePhase === 'checking' || gamePhase === 'complete') {
        // During checking/complete phase, show correct/incorrect feedback
        if (isCorrect === true) {
          cellStyle = [styles.cell, styles.correctCell];
          textStyle = [styles.cellText, styles.correctText];
        } else {
          cellStyle = [styles.cell, styles.incorrectCell];
          textStyle = [styles.cellText, styles.incorrectText];
        }
      }
    } else if (isCorrect === true) {
      // Show persistent correct tiles (green)
      cellStyle = [styles.cell, styles.correctCell];
      textStyle = [styles.cellText, styles.correctText];
    } else if (isCorrect === false) {
      // Show persistent incorrect tiles (red)
      cellStyle = [styles.cell, styles.incorrectCell];
      textStyle = [styles.cellText, styles.incorrectText];
    }
    
    return (
      <TouchableOpacity
        key={`${row}-${col}`}
        style={cellStyle}
        onPress={() => onCellPress(row, col)}
        disabled={gamePhase !== 'placing'}
      >
        <Text style={textStyle} numberOfLines={2}>
          {word ? getWordByDifficulty(word, difficulty) : ''}
        </Text>
      </TouchableOpacity>
    );
  };

  return (
    <View style={styles.container}>
      {[0, 1, 2, 3].map((row) => (
        <View key={row} style={styles.row}>
          {[0, 1, 2, 3].map((col) => renderCell(row, col))}
        </View>
      ))}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 20,
    backgroundColor: 'white',
    borderRadius: 15,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
    alignItems: 'center',
  },
  row: {
    flexDirection: 'row',
    marginBottom: 0,
  },
  cell: {
    width: cellSize,
    height: cellSize,
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 6,
    marginBottom: 6,
    borderWidth: 1,
    borderColor: '#e9ecef',
  },
  cellText: {
    fontSize: 12,
    fontWeight: '600',
    textAlign: 'center',
    color: '#495057',
    paddingHorizontal: 4,
  },
  markedCell: {
    backgroundColor: '#d4edda',
    borderColor: '#28a745',
  },
  markedText: {
    color: '#155724',
  },
  correctCell: {
    backgroundColor: '#d4edda',
    borderColor: '#28a745',
  },
  correctText: {
    color: '#155724',
  },
  incorrectCell: {
    backgroundColor: '#f8d7da',
    borderColor: '#dc3545',
  },
  incorrectText: {
    color: '#721c24',
  },
  debugText: {
    fontSize: 10,
    color: '#666',
    textAlign: 'center',
    marginTop: 5,
  },
});

export default BingoCard; 