import matplotlib.pyplot as plt
import numpy as np

# Function to generate a bingo card
def generate_bingo_card(words, colors, filename):
    cell_size = 0.15
    font_size = 40

    fig, ax = plt.subplots(figsize=(8, 8))
    bingo_card = np.array(words).reshape(4, 4)  # Reshape to 4x4 grid

    table = ax.table(
        cellText=bingo_card, 
        cellColours=colors, 
        cellLoc='center', 
        loc='center', 
        colWidths=[cell_size] * 4,
        edges='closed')

    # Set uniform height for all cells
    for (i, j), cell in table.get_celld().items():
        cell.set_height(cell_size)  
        cell.set_width(cell_size)
        if cell.get_text() is not None:  # Ensure the cell has text before setting font size
           cell.get_text().set_fontsize(font_size); 
           cell.set_edgecolor('black')

    ax.axis('off')  # Hide axes
    ax.set_aspect('equal')  # Ensure cells are square by maintaining aspect ratio
    plt.title('Bingo Card', weight='bold', fontsize=font_size)
    plt.savefig(filename, bbox_inches='tight')
    plt.show()

words = [
    ('Run', 'verb'), ('Sky', 'noun'), ('Beautiful', 'adjective'), ('Jump', 'verb'),
    ('Ocean', 'noun'), ('Bright', 'adjective'), ('Play', 'verb'), ('Cloud', 'noun'),
    ('Happy', 'adjective'), ('Swim', 'verb'), ('Tree', 'noun'), ('Colorful', 'adjective'),
    ('Dance', 'verb'), ('Mountain', 'noun'), ('Soft', 'adjective'), ('Sing', 'verb')
]

color_key = {
    'noun': 'lightblue',
    'verb': 'lightpink',
    'adjective': 'lightgreen'
}


# Extract just the words for display
words_only = [word for word, pos in words]

# Create the corresponding color array
colors = [[color_key[pos] for word, pos in words[i*4:(i+1)*4]] for i in range(4)]

# Generate and save the bingo card
generate_bingo_card(words_only, colors, 'bingo_card_colored.pdf')