from app.points.score import Score

class Scores:
    '''
    Manages a collection of Score objects for leaderboard generation.

    This class acts as a container, providing functionality to hold multiple
    Score objects, add new ones, and generate a sorted list based on total points.
    '''
    def __init__(self, initial_scores: list[Score] = None):
        self._scores = []

        if initial_scores is not None:

            if not isinstance(initial_scores, list):
                raise TypeError('initial_scores must be a list of Score objects.')

            for score in initial_scores:
                self.add_score(score)

    def add_score(self, score_to_add: Score):
        '''
        Adds a single, validated Score object to the collection.

        Args:
            score_to_add (Score): The Score object to be added.

        Raises:
            TypeError: If the provided item is not an instance of the Score class.
        '''
        if not isinstance(score_to_add, Score):
            raise TypeError('Only Score objects can be added to the collection.')

        self._scores.append(score_to_add)

    def get_leaderboard(self) -> list[Score]:
        '''
        Returns the list of Score objects sorted by total_score in descending order.

        Returns:
        - list[Score]: A new list containing Score objects, sorted from the
                       highest total score to the lowest.
        '''
        return sorted(self._scores, key = lambda score: score.total_score, reverse = True)

    def __iter__(self):
        '''
        Makes the Scores collection iterable.
        '''
        return iter(self._scores)

    def __len__(self) -> int:
        '''
        Returns the count of Score objects currently in the collection.
        '''
        return len(self._scores)

    def __getitem__(self, index: int) -> Score:
        '''
        Retrieves a Score object by its index in the collection.
        '''
        return self._scores[index]