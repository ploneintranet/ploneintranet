Ploneintranet Translations
==========================

.. contents:: Table of Contents
    :depth: 2
    :local:

Translation of the UI elements
------------------------------

**We aim at a professional market. We need a professional translation.**

For the recognition of the quality of Plone Intranet, a professional "native speaker level" translation is crucial, since it reflects the inner values into the interface in conjunction with the visual design.

When a user talks to his colleagues about usage of the Plone Intranet as a tool, the customer is much more successful transforming goals into working results when the experience of the meaning of the language is seamless on the point.

One big challenge to keep terms unique and non ambiguos throughout all occurences and contexts.

In other words: any user-visible change of translateable terms and i18n ids cannot be made by a backend developer, without first consulting the translation glossary and existing i18n IDs for the right term and getting a UI element reservation in the prototype for that purpose. This provides a major quality assurance on the user experience.

It is good practise to keep variable names and the main english terms in sync.


Transifex as the translators workbench tool
-------------------------------------------

The translations of Plone Intranet are not managed by editing plain .po files. Instead we use the professional translation platform transifex that is free for open source projects <https://www.transifex.com/projects/p/plone-intranet/>`_.

Transifex provides:
- Accounts for non-developer translators as teammembers
- Management and creation of .pot and .po files from a web interface without knowledge of git etc.
- Comments that can be treated optional as issues to be resolved by others.
- Different access rights for different languages
- Easy filtering of translateable strings and translations
- A translation glossary containing all specific terms that need to be consistent with management of type (verb, noun, adjectiv etc.) and additional comments per language.
- All language glossaries share the base terms in the canonical language english.

Benefits of the glossary
++++++++++++++++++++++++

- You see at once if a term is already in use.
- Then you can search for similar occurences to make them consistent.
- Use the comments to hint if there are ambiguos or false friend issues already given and avoid misuse.

.. note::

   You don't need to install Ploneintranet to work on translations!
   Get a transifex account and issue a join request.

Translation Workflow
===================

- Go to the Transifex project mainpage at <https://www.transifex.com/projects/p/plone-intranet/>`_
- If not already done join the team for a language.
- Click on the language you want to work on.
- The only currently listed resource is the **po** file related to **ploneintranet.pot**. Click on the resource.
- You will see some statistics. Even if the state is **100%** and **0 words remaining** click on translate or choose one of the tasks listed below.

    - Choose "View strings online" if you just want to browse. You can enter translation from there.

- Start from the top of the sentence translation list.
- Open the glossary view in another tab.

.. tipp:: To just search for existing terms in the glossary or "translationmemory" (TM in translators jargon) use the **CONCORDANCE SEARCH** button in the translation view at the top. It opens an overlay view at the bottom of the page.

.. tipp:: there is a list of **Keyboard Shortcuts** under the **gear-wheel icon**.


Adding terms to the glossary
----------------------------

- Take every non obviuos noun, verb or adjective and its translation.
- Open the glossary using the **View Glossary** button at the Transifex project mainpage at <https://www.transifex.com/projects/p/plone-intranet/>`_.
- Click on the green plus at the top left of the view.
- Enter the original term and select the right type of word. Be not ashamed to use a dictionary to check for this. If unsure leave unspecific.
- Enter your translation
- You can later enter a comment to both columns in the main listing.

    - Use the filter search to find it.

There are some challenges when translating
==========================================

- What if I find a second occurrence of a similar term in different context and I am not sure if this needs consistence or differentiation?

   - The best is to run the whole translation task as a single translator at least one time in one run to find those issues.
   - Make comments and optional personal notes to track them later.
   - Clear them only after a full run and understanding all the variations of usage to keep them distinguishable.
   - If a mess comes from the original, make sure your leave a comment and later redistribute this to the original as well.

- How do I deal with plural vs. singular or declination in the glossary?

   - For now keep the singular to track the term. This may have issues with searching. Instead use external dictionaries like the Duden or leo.org for German.
   - Always search for the stems of a word and not the full declined terms until necessary.
   - If there are extremely different terms in plurals add them as well.

- If I find a mistake like eg "Email" instead of "E-Mail" in the translation that may occour at multiple places.

   - Use the search for filtering in the sentence listing and list all the occurences and fix them (remember to use stem search!).

- How do I document the reason behind a correction, if I do a serious change?

   - First write a comment that describes the before and after and the reason. Mark the comment as issue before saving. If you miss this, copy the comment, delete the comment and recreate it.
   - Then fix the issue.
   - Finally mark the issue as resolved.

Expected Workflow for derivative languages
==========================================

Example Germany vs. Switzerland, Austria
----------------------------------------

Beside the currencies there is a need to split the german translations for Germany vs. Switzerland (and Austria) because e.g. of the double s issue for Switzerland and serious different wordings for some usual terms. Currently the German version uses the Switzerland way of avoiding the "ß" and using the "ss". We should ask austrian and suisse native writers (not speaker) to take care for a review.

.. note:: There is maybe also a need on demand for e.g. the "de-br" translation for Belgium since German is one of the official languages! The same for de-it for Tirol. The Plone Community is well known to take care of these details.

Expected Workflow for derivative languages
------------------------------------------

Example "DE"
++++++++++++

- Finish the main review of cases in doubt marked as issues in the leading "de" translation first
- Distribute the 100% complete current "de" version to the (currently not complete) "de-de" version.
- Then the "de-ch", "de-at" versions should get touchup.

Releases
========

Versioning inside of transifex
------------------------------

.. todo:: Check the history functions of Transifex. There seem to exist no commit messages, so using the issue/comment trick is the only way to document the purpose of a change.


Checking in a translation into the Plone Intranet GIT repo
----------------------------------------------------------

.. todo:: To be added later by the release manager...


Generation and updating of the pot files in Transifex
=====================================================

.. todo:: To be added later by the translations manager...