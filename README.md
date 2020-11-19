# Movie-Recommender-System-MVS-

This is a complete website with the capability to provide meaning recommendations to a particular user basing on the Movies that he likes and the Movies that similar users like have watched.
The model uses Cosine Similarity to compute the similarity between two any users. So, whenever recommendations need to calculated the Cosine Similarity is calculated between
all the users and results are sorted in a decreasing order. The User with most similarity is in the top of the list. From that we start recommending the titles those users have
rated high.

The website is built on Mongo and Flask.
Model : Cosine Similairity
