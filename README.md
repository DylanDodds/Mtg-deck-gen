# Mtg-ai
#### A Magic the gathering deck generator
This application generates a magic the gathering deck based on pro statistics. In this repository are some scripts I wrote
using selenium to quickly scrape as much data from MTGTop8.com as it can and import it into a database. generate_deck.py then uses the genetic algorithm described below to generate a deck based on the winning statistcs of professional matches.


### The Algorithm:
##### (This description was taken from a thread on my forums I originally shared to explain my process)

> Recently, a friend of mine went to regionals for a Magic the Gathering competition and he asked me if it was possible to write an algorithm that could generate a winning deck. I did some research and learnt that when you participate in a Magic the Gathering tournament, you are required to write down every card in your deck, and the number of that card you are using. This data is used to check if players are cheating by using too many cards, or using cards that are not in the current "standard" set rotation. After the tournament, the data is sent of to Wizards, and forwarded to websites such as mtgtop8.com. On this site is a list of Magic the Gathering decks, the cards and counts they contain, the events they played in, and the rank the player came in that tournament. The ranks are as followed:
>
> - Rank 1 - first place,
> - Rank 2 - second place,
> - Rank 3, 3-4, 4 :  third place
>
> ( and a few others, the ranks in a tournament were entirely dependent on how many players played. For example, if there was a tournament with 50+ played, they top 16 places are counted as "placed in tournament")
>
>Using these ranks I was able to generate a table to convert scores to points using constant values.
>For example:
> - 1st = 100 points
> - 2nd = 80 points
> - 3-4 = 60
> - ...
>
> Using this system I could calculate the score of individual cards by adding up the points of every event that card played in. The cards that were played the most, and won the most games would have the highest scores.
>
>Though I could generate a deck of the best cards, it wouldn't be enough to create a "winning deck". In Magic the Gathering, certain cards are played together because their effects benefit other cards. So along side scoring the cards, I had to score pairs of cards. So i generated a list of all possible cards combinations and for each combination i took the common events that both cards in the combination played in and added up those events total score. This total would be the score of the pair. Using this information, I wrote a genetic algorithm, that took into account which cards were played in the most winning games, and which pairs were played with those cards in winning games. The genetic algorithm calculated the average score of each card and pair in the deck, and any card or pair in the deck that was below the average of the current population (the deck), was mutated with a new card in the next generation. Most of the cards in the generated deck were meant to be played together, but the algorithm seemed to pick up good pairs that didn't play well with other good pairs.
>
>So it seems i need to do a bit of more tweaking, I'll be sure to report more as i continue development.