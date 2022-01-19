from collections import defaultdict

class PopulationStatistics:
    words = []
    weights = {}

    def __init__(self):
        with open('wordle.txt', 'r') as file:
            """
            Populate the class property with a word list contained in a textfile.
            This will allow us to trim the word list as required.
            For example, if a word doesn't exist in wordle, we can remove it.
            """
            self.words = [word.upper() for word in file.read().splitlines()]

        self.rank_word_list(self.words)

    def calculate_letter_weights(self, words):
        """
        Iterate through a list of words, count the occurrences of different letters
        and provide a ranked mapping of these letters for use in scoring. 
        """
        counter = defaultdict(int)

        for letter in "".join(words):
            counter[letter] += 1

        x_min = min(counter.values())
        x_max = max(counter.values())

        counter = sorted(counter.items(), key=lambda x: x[1])

        weights = {}
        for row in counter:
            (letter, occurences) = row
            normalized_value = (occurences - x_min) / (x_max - x_min)
            weights[letter] = normalized_value

        return weights

    def calculate_word_value(self, word, weights):
        """
        Use normalised letter weight as a starting point.
        Punish words that have repeating letters to encourage more varied words. 
        """
        letters = []
        for letter in word:
            if letter not in letters:
                letters.append(letter)

        score = 0
        for letter in letters:
            score += weights[letter]

        return score * (len(letters) / 5)

    def rank_word_list(self, words):
        """
        This solver will use the concept of a "letter weight", this will let us give
        and arbitrary score to a letter found in any given population. 

        As the word population shrinks, we'll naturally want to reuse this function
        to improve our guess. 
        """
        weights = self.calculate_letter_weights(words)

        ranked_words = {}
        for word in words:
            ranked_words[word] = self.calculate_word_value(word, weights)
        
        ranked_words = sorted(ranked_words.items(), key=lambda x: x[1], reverse=True)

        return ranked_words[0]


class Solver:
    population = None
    incorrect_positions = []
    incorrect_letters = []
    correct_letters = []
    word_state = []
    words = []
    current_guess = None

    def __init__(self, population):
        self.population = population
        self.words = population.words
        self.word_state = [False] * 5
        self.current_guess = self.calculate_starting_word()

    def calculate_starting_word(self):
        starting_guess = self.population.rank_word_list(self.population.words)
        return starting_guess[0]

    def store_incorrect_letter(self, position):
        letter = self.current_guess[position]
        self.incorrect_letters.append(letter)

    def store_correct_letter(self, position):
        letter = self.current_guess[position]
        self.correct_letters.append((letter, position))
        self.word_state[position] = letter.upper()

    def store_incorrect_position(self, position):
        letter = self.current_guess[position]        
        self.incorrect_positions.append((letter, position))

    def parse_guess_results(self, response):
        response = response.upper()

        assert type(response) == str, "Answer is not a string"
        assert len(response) == 5, "Answer response exceeds 5 letters"

        for index, char in enumerate(response):
            if char == 'C':
                self.store_correct_letter(index)
            elif char == 'W':
                self.store_incorrect_position(index)
            elif char == 'N':
                self.store_incorrect_letter(index)

        self.recalculate_word_list()
        self.get_next_guess()

    def recalculate_word_list(self):
        words = self.words

        if len(self.incorrect_letters):
            words = [word for word in words if not any([letter in self.incorrect_letters for letter in word])]

        if len(self.correct_letters) > 0:
            for letter, position in self.correct_letters:
                words = list(filter(lambda word: word[position] == letter, words))

        if len(self.incorrect_positions) > 0:
            words = [word for word in words if all([letter[0] for letter in self.incorrect_positions if letter[0] in word])]    
            for letter, position in self.incorrect_positions:
                words = list(filter(lambda word: word[position] != letter, words))

        self.words = words

    def get_next_guess(self):
        guess = self.population.rank_word_list(self.words)
        self.current_guess = guess[0]
        return guess[0]

population = PopulationStatistics()
solver = Solver(population)


solver.parse_guess_results('nnwnn')
print(solver.current_guess)
solver.parse_guess_results('wccnn')
print(solver.current_guess)
solver.parse_guess_results('wcccn')
print(solver.current_guess)
