=====================
Personalized Pagerank
=====================

This package prototypes a search personalization strategy for intranets,
based on applying personalized PageRank calculations to a Plone social intranet system.

Status: incomplete, prototype, work in progress.

Installation
------------

Initialize and enter the docker container::

  home$ make docker-build
  home$ make docker-run

Run the buildout::

  app$ make

You can then run Plone::

  app$ bin/instance fg


PageRank
--------

Google's PageRank algorithm condenses the link structure of the web into
a single number for each page: that page's PageRank.

PageRank is a recursive algorithm, where the PageRank of a given page X is derived from the
PageRank of other pages that link to page X. The calculation usually stabilizes after enough
iterations, typically 30. The algorithm is well understood and implementations typically
use map-reduce parrallel calculations.

Intuitively, the PageRank of a given page can be understood as the probability that a web surfer
randomly following links, will be visiting that specific page on a random moment.

PageRank has a hologram-like character, in that each page's PageRank is determined by the
link structure of the whole web, and changes as the web changes.

The genius of PageRank is that it interprets hyperlinks as "votes" of importance,
and is able to reduce the whole link structure of the web into a single scalar per page,
that is then used to sort search results.

To summarize:

- single PageRank scalar per page
- incorporates human intent through link "voting"
- hologram-like reflection of overall web structure
- useful to sort search results
- well-known map-reduce algoritm


Intranet search
---------------

Intranets are way smaller than the open web, and also often feature a
more restricted editing and publishing environment, resulting in less
links per page and a small set of authors/editors dominating the collection.
This lack of data to inhibits a meaningful PageRank search result scoring.

Search in intranets is very important. The two dominant information retrieval
strategies of users are: browsing and search. 

With regards to browsing, the information architecture in large intranets
can be daunting, a problem that is compounded as the architecture
is ad-hoc changed to accomodate changing organizational realities, resulting in
information architectures that are both out-of-sync with the organization as
perceived by the employees, and moreover become confusing because of ad-hoc
inconsistencies. Link structures are poor, the browsing experience sucks,
and the intranet perenially risks lack of maintenance and a spiral into
irrelevance.

Search in intranets is typically keyword based. It's like a throwback to
the keyword-based Altavista search that dominated web search in the previous
century. For users accustomed to the spot-on relevance quality of Google search
that is a turn-off.

As a result, the business suffers. Both browsing and search are confusing and
disorienting experiences. Still, people need access to relevant information.
Research shows that up to 20% of knowledge worker's time is wasted on searching
for information. Any reduction in that time loss is a significant business win.

Fixing intranets
----------------

To remedy this situation we can employ a two-fold strategy:

1. Improve the intranet dataset by:

- increasing the number and diversity of authors
- increasing the amount of intranet pages
- increasing link density within the intranet page set

This is achieved by introducing social intranet features, that:

- encourage authorship by microblogging and self-managed teamspaces
- reduce friction in sharing content (microblogging, commenting, easy upload)
- gamify the creation of new links (follow, like, tag, comment)

2. Improve the search result relevancy ranking by:

- taking a user's activity into account (document interactions)
- taking a user's tags of interest into account (topic graph)
- taking a user's social connections into account (social graph)

This can be achieved by implementing a personalized search ranking strategy,
that takes the above three relevancy dimensions into account.

Personalized PageRank
---------------------

A personalized PageRank approach calculates, for every user individually,
the PageRank of all intranet pages.

In this approach we interpret every resouce on the intranet as a node.
This applies not only to pages, but also to people, group spaces, and tags.
Doing this gives us a far denser node and link network than considering just pages,
especially taking into account the resource and link creation elicited by implementing
social features, as discussed above.

Conceptually, we represent all pages, people, groups and tags on the intranets as nodes
in a network, and we express all affinity connections between pages, people etc as links
in that network. So somebody authoring a document creates a link. Documents can link to 
each other. Tagging a document links the author with the tag, the tag with the document,
and also the author to the document. Following a user, or liking an update, creates links.
Etcetera etcetera.

The full graph of resource nodes and affinity links is a global structure that changes
over time but provides an impersonal perspective. Personalization is applied by choosing
the perspective of a single user and assigning a high weight onto her outgoing links.
This results in a different PageRank assignment per document, for each user.

We can apply the same approach to other types of nodes in the intranet, for example
take a specific document as the starting point will yield personalized PageRanks for that
document perspective, which we can use to sort "see also" relevancy recommendations.

In a future stage, one can imagine replacing a simple "tag=keyword" node/link concept 
with more elaborate ontology networks to express the topic graph.

The beauty of PageRank is, that it results in a single scalar per document, that can be
used for search result ranking. Personalized PageRank implies that we store and retrieve
PageRank scores for each document, for each user. So instead of a single 
document->pagerank lookup this is more of a hashtable lookup: document->pagerank[user].

PageRank calculations are costly and typically performed in a batched map-reduce environment.
Because intranets are much smaller than the open web this is a much more tractable problem
than personalized PageRank calculations for the whole web.
We should try and implement `Personalized PageRank optimization`_ techniques that have been
developed specifically to solve this problem.

Applying this approach implies that:

- most of the computational cost is borne async index-time using scalable map-reduce
- query-time application involves lookup and application of a per-user per-document boost value

In other words, we decouple personalized PageRank index-time calculation from query-time lookup.

Note that index-time means *any* change in the system, since changes propagate because of the
hologram-like property of the algorithm. This becomes an ongoing computation that should leverage
the availablility of sharding and optimizations algorithms developed for PageRank calculations.

Query-time lookup can probably_ be implemented in Solr by crafting the right index_.


.. _Personalized PageRank optimization: http://www.amazon.co.uk/Numerical-Algorithms-Personalized-Self-organizing-Information/dp/0691145032/

.. _probably: http://www.slideshare.net/LucidImagination/boosting-documents-in-solr-by-recency-popularity-and-user-preferences

.. _index: http://blog.trifork.com/2011/11/16/apache-lucene-flexiblescoring-with-indexdocvalues/


Plone
-----

The above indicated two components of a personalized search solution:

1. index-time personalized PageRank computation
2. query-time personalized PageRank lookup

These both involve secondary, derived index data.
A full solution requires a third component: 

3. the primary data being indexed has to be stored in Plone.

Vanilla Plone already provides document-document linking (hyperlinks, references),
document-tag linking (DC:Subject), and document-person linking (DC:Creators, allowedUsersAndGroups).
PloneSocial adds to that person-person linking (followers, following).
The main challenge remaining in this regard is breaking the monilithic DC:Subject tagging,
which implies a global tag set that is true for everybody, with a more finegrained tagging
approach that enables personal tagging of documents (so that my tags can be different from yours).

These diverse primary data sources within Plone then have to be exposed through a consistent and
performant API, so the batched PageRank calculation can pull in the data it needs.

The resulting PageRank calculations express person-document, but also document-document
and tag-document affinities and need to be easily queryable, not just in the scenario of
a keyword search action, but also to power generic context recommendations in the form of
"see also these pages", "experts on this topic", "related topics".
