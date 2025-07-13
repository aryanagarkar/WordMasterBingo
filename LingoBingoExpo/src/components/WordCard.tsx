import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Animated,
  Dimensions,
  Modal,
} from 'react-native';
import { WordData } from '../data/wordData';

const { width } = Dimensions.get('window');

interface WordCardProps {
  word: WordData;
  isVisible: boolean;
  onFlip: () => void;
  onAnswer: (isCorrect: boolean) => void;
}

const WordCard: React.FC<WordCardProps> = ({
  word,
  isVisible,
  onFlip,
  onAnswer,
}) => {
  const [isFlipped, setIsFlipped] = useState(false);
  const [flipAnim] = useState(new Animated.Value(0));

  useEffect(() => {
    if (isVisible) {
      setIsFlipped(false);
      flipAnim.setValue(0);
    }
  }, [isVisible]);

  const handleFlip = () => {
    setIsFlipped(!isFlipped);
    Animated.timing(flipAnim, {
      toValue: isFlipped ? 0 : 1,
      duration: 500,
      useNativeDriver: true,
    }).start();
    onFlip();
  };

  const frontInterpolate = flipAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['0deg', '180deg'],
  });

  const backInterpolate = flipAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['180deg', '360deg'],
  });

  const frontAnimatedStyle = {
    transform: [{ rotateY: frontInterpolate }],
  };

  const backAnimatedStyle = {
    transform: [{ rotateY: backInterpolate }],
  };

  if (!isVisible) return null;

  return (
    <Modal
      visible={isVisible}
      transparent={true}
      animationType="fade"
    >
      <View style={styles.container}>
        <View style={styles.cardContainer}>
          {/* Front of card */}
          <Animated.View style={[styles.card, styles.front, frontAnimatedStyle]}>
            <View style={styles.cardHeader}>
              <Text style={styles.cardTitle}>Definition</Text>
            </View>
            <View style={styles.cardBody}>
              <Text style={styles.definition}>{word.definition}</Text>
              <View style={styles.imagePlaceholder}>
                <Text style={styles.imageText}>📚</Text>
              </View>
            </View>
            <TouchableOpacity style={styles.flipButton} onPress={handleFlip}>
              <Text style={styles.flipButtonText}>Flip Card</Text>
            </TouchableOpacity>
          </Animated.View>

          {/* Back of card */}
          <Animated.View style={[styles.card, styles.back, backAnimatedStyle]}>
            <View style={styles.cardHeader}>
              <Text style={styles.cardTitle}>Synonyms</Text>
            </View>
            <View style={styles.cardBody}>
              <View style={styles.synonymItem}>
                <Text style={styles.synonymLabel}>Easy:</Text>
                <Text style={styles.synonymText}>{word.easy}</Text>
              </View>
              <View style={styles.synonymItem}>
                <Text style={styles.synonymLabel}>Medium:</Text>
                <Text style={styles.synonymText}>{word.medium}</Text>
              </View>
              <View style={styles.synonymItem}>
                <Text style={styles.synonymLabel}>Hard:</Text>
                <Text style={styles.synonymText}>{word.hard}</Text>
              </View>
            </View>
            <View style={styles.answerButtons}>
              <TouchableOpacity
                style={[styles.answerButton, styles.correctButton]}
                onPress={() => onAnswer(true)}
              >
                <Text style={styles.answerButtonText}>I Have This Word</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.answerButton, styles.incorrectButton]}
                onPress={() => onAnswer(false)}
              >
                <Text style={styles.answerButtonText}>I Don't Have This Word</Text>
              </TouchableOpacity>
            </View>
          </Animated.View>
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  cardContainer: {
    width: width - 40,
    height: 400,
    perspective: 1000,
  },
  card: {
    position: 'absolute',
    width: '100%',
    height: '100%',
    backfaceVisibility: 'hidden',
    backgroundColor: 'white',
    borderRadius: 15,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 4.65,
    elevation: 8,
  },
  front: {
    transform: [{ rotateY: '0deg' }],
  },
  back: {
    transform: [{ rotateY: '180deg' }],
  },
  cardHeader: {
    backgroundColor: '#667eea',
    padding: 20,
    borderTopLeftRadius: 15,
    borderTopRightRadius: 15,
    alignItems: 'center',
  },
  cardTitle: {
    color: 'white',
    fontSize: 20,
    fontWeight: 'bold',
  },
  cardBody: {
    flex: 1,
    padding: 20,
    justifyContent: 'center',
  },
  definition: {
    fontSize: 16,
    lineHeight: 24,
    color: '#333',
    marginBottom: 20,
    textAlign: 'center',
  },
  imagePlaceholder: {
    height: 100,
    backgroundColor: '#f8f9fa',
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#dee2e6',
    borderStyle: 'dashed',
  },
  imageText: {
    fontSize: 40,
  },
  flipButton: {
    backgroundColor: '#667eea',
    padding: 15,
    margin: 20,
    borderRadius: 10,
    alignItems: 'center',
  },
  flipButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  synonymItem: {
    marginBottom: 15,
    padding: 10,
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#667eea',
  },
  synonymLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#495057',
    marginBottom: 5,
  },
  synonymText: {
    fontSize: 16,
    color: '#333',
  },
  answerButtons: {
    flexDirection: 'row',
    padding: 20,
    gap: 10,
  },
  answerButton: {
    flex: 1,
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
  },
  correctButton: {
    backgroundColor: '#28a745',
  },
  incorrectButton: {
    backgroundColor: '#dc3545',
  },
  answerButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '600',
  },
});

export default WordCard; 