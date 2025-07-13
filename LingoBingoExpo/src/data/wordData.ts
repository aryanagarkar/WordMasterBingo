export interface WordData {
  word: string;
  definition: string;
  easy: string;
  medium: string;
  hard: string;
  imagePath?: string;
}

export const wordData: WordData[] = [
  {
    word: "Absolution",
    definition: "Release from guilt or punishment",
    easy: "Forgiveness",
    medium: "Absolution", 
    hard: "Exoneration"
  },
  {
    word: "Renounce",
    definition: "To give up power or a position",
    easy: "Quit",
    medium: "Renounce",
    hard: "Abdicate"
  },
  {
    word: "Enraged",
    definition: "Extremely angry",
    easy: "Upset",
    medium: "Enraged",
    hard: "Livid"
  },
  {
    word: "Conundrum",
    definition: "A confusing problem or question",
    easy: "Puzzle",
    medium: "Conundrum",
    hard: "Enigma"
  },
  {
    word: "Debacle",
    definition: "A sudden and complete failure",
    easy: "Disaster",
    medium: "Debacle",
    hard: "Fiasco"
  },
  {
    word: "Dauntless",
    definition: "Showing no fear; very bold and determined even when facing danger or difficulties",
    easy: "Brave",
    medium: "Dauntless",
    hard: "Intrepid"
  },
  {
    word: "Examine",
    definition: "To look at something carefully and closely - especially to learn more about it or find out important details",
    easy: "Observe",
    medium: "Examine",
    hard: "Scrutinize"
  },
  {
    word: "Articulate",
    definition: "Fluent or persuasive in speaking",
    easy: "Clear",
    medium: "Articulate",
    hard: "Eloquent"
  },
  {
    word: "Galvanic",
    definition: "Sudden and dramatic like an electric shock",
    easy: "Shocking",
    medium: "Galvanic",
    hard: "Convulsive"
  },
  {
    word: "Fanatical",
    definition: "Showing extreme or blind admiration",
    easy: "Worshipful",
    medium: "Fanatical",
    hard: "Idolatrous"
  },
  {
    word: "Simpleton",
    definition: "A person who is lacking in common sense or is gullible",
    easy: "Fool",
    medium: "Simpleton",
    hard: "Ignoramus"
  },
  {
    word: "Jocular",
    definition: "Joking or playful",
    easy: "Funny",
    medium: "Jocular",
    hard: "Facetious"
  },
  {
    word: "Painstaking",
    definition: "Extremely careful and precise",
    easy: "Careful",
    medium: "Painstaking",
    hard: "Meticulous"
  },
  {
    word: "Obsequious",
    definition: "Overly eager to please or obey",
    easy: "Fawning",
    medium: "Obsequious",
    hard: "Sycophantic"
  },
  {
    word: "Pallid",
    definition: "Lacking healthy color - usually from illness or fear",
    easy: "Pale",
    medium: "Pallid",
    hard: "Wan"
  },
  {
    word: "Resilient",
    definition: "Able to recover quickly",
    easy: "Tough",
    medium: "Resilient",
    hard: "Buoyant"
  },
  {
    word: "Omnipresent",
    definition: "Found everywhere",
    easy: "Common",
    medium: "Omnipresent",
    hard: "Ubiquitous"
  },
  {
    word: "Vindictive",
    definition: "Having a strong desire for revenge",
    easy: "Spiteful",
    medium: "Vindictive",
    hard: "Retaliatory"
  },
  {
    word: "Exonym",
    definition: "A name for a place, person, or group that is used by outsiders",
    easy: "Foreign Name",
    medium: "Exonym",
    hard: "Xenonym"
  }
];

export enum DifficultyLevel {
  EASY = 'easy',
  MEDIUM = 'medium',
  HARD = 'hard'
}

export const getWordByDifficulty = (word: WordData, difficulty: DifficultyLevel): string => {
  switch (difficulty) {
    case DifficultyLevel.EASY:
      return word.easy;
    case DifficultyLevel.MEDIUM:
      return word.medium;
    case DifficultyLevel.HARD:
      return word.hard;
    default:
      return word.medium;
  }
}; 