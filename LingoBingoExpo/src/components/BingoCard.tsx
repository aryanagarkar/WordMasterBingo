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
const cellSize = (width - 60) / 4; // 4x4 grid with margins

interface BingoCardProps {
  words: WordData[];
  difficulty: DifficultyLevel;
  markedCells: boolean[][];
  correctAnswers: boolean[][];
  onCellPress: (row: number, col: number) => void;
}

const BingoCard: React.FC<BingoCardProps> = ({
  words,
  difficulty,
  markedCells,
  correctAnswers,
  onCellPress,
}) => {
  const renderCell = (row: number, col: number) => {
    const index = row * 4 + col;
    const word = words[index];
    const isMarked = markedCells[row]?.[col] || false;
    const isCorrect = correctAnswers[row]?.[col] || false;
    
    let cellStyle = styles.cell;
    let textStyle = styles.cellText;
    
    if (isMarked) {
      if (isCorrect) {
        cellStyle = [styles.cell, styles.correctCell];
        textStyle = [styles.cellText, styles.correctText];
      } else {
        cellStyle = [styles.cell, styles.incorrectCell];
        textStyle = [styles.cellText, styles.incorrectText];
      }
    }
    
    return (
      <TouchableOpacity
        key={`${row}-${col}`}
        style={cellStyle}
        onPress={() => onCellPress(row, col)}
        disabled={isMarked}
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
  },
  row: {
    flexDirection: 'row',
    marginBottom: 8,
  },
  cell: {
    width: cellSize,
    height: cellSize,
    backgroundColor: '#f8f9fa',
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 8,
    borderWidth: 2,
    borderColor: '#e9ecef',
  },
  cellText: {
    fontSize: 12,
    fontWeight: '600',
    textAlign: 'center',
    color: '#495057',
    paddingHorizontal: 4,
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
});

export default BingoCard; 