Code optimization
=================

1. In the distribution_page_rank method, I noticed that when initializing the probability of each node, I was calculating the total number of nodes for each node, to initialize the probability to 1 / number of nodes. In order to save some time, I decided to calculate the total number of nodes once before the for loop, and assign this to a variable that can be reused (named num_nodes).
2. In the stochastic_page_rank method, I was originally using "import random" and then referencing the choice function via "random.choice". To optimize this, I instead used "from random import choice". This allows the choice function to be directly referenced by subsequent uses.