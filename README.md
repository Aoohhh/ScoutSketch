# ScoutSketch
## Introduction
This paper first studies a new but important pattern for items in data streams, called promising items. 
The promising items mean that the frequencies of an item in multiple continuous time windows show an upward trend overall, 
while a slight decrease in some of these windows is allowed. Many practical applications can benefit from the property of promising items,
e.g., detecting potential hot events or news in social networks, preventing network congestion in communication channels, 
and monitoring latent attacks in computer networks. To accurately find promising items in data streams in real-time under
limited memory space, we propose a novel structure named Scout Sketch, which consists of Filter and Finder.
In contrast to promising items exhibiting an increasing trend, 
we also introduce damping items, demonstrating a decreasing trend. The detection of such items also holds significant practical
implications. We enhance Scout Sketch (called Scout Sketch+) to adaptively detect both types of items simultaneously. 
Finally, we conducted extensive experiments based on four real-world datasets. The experimental results show that the 
F1 Score and throughput of Scout Sketch are about 2.02 and 5.61 times that of the compared solutions, respectively.

## About this repo
This repo contains all the algorithms in our experiments. 
We respectively utilized C++ and Python languages to write code and conducted experimental validation.
Python was employed to validate the PR, RR, and F1 Score of the structure, while C++ was used to validate the Throughput of the structure.
We did not opt to provide the dataset used since it is readily available online.
