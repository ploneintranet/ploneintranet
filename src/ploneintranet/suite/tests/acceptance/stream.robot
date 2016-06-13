*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  ../lib/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  DebugLibrary

Test Setup  Prepare test browser
Test Teardown  Close all browsers

*** Variable ***

${MESSAGE1}    I am so excited, this is super!
${MESSAGE2}    Living next door to Alice
${MESSAGE3}    You know nothing, Jon Snow!
${USERNAME1}   François Gast
${USERNAME2}   Silvio De Paoli
${TAG1}        Rain
${TAG2}        Sun
${TAG3}        Moonshine

*** Test Cases ***

Allan can view the stream
    Given I am logged in as the user allan_neece
    when I open the Dashboard
    then I can see updates by  Christian Stoney

Allan can open his user filter stream and see only people he is following
    Given I am logged in as the user allan_neece
    when I open the Dashboard
    and I filter the stream as  network
    then I cannot see updates by  Christian Stoney
    and I can see updates by  Jorge Primavera

Allan can open his user filter stream and switch back to show all again
    Given I am logged in as the user allan_neece
    and I open the Dashboard
    and I filter the stream as  network
    and I cannot see updates by  Christian Stoney
    when I filter the stream as  all
    then I can see updates by  Christian Stoney

Allan can add a user to his user filter stream and remove him again
    Given I am logged in as the user allan_neece
    and I open the Dashboard
    and I can follow the profile link for user  Christian Stoney
    when I can toggle following the user
    and I open the Dashboard
    and I filter the stream as  network
    then I can see updates by  Christian Stoney
    when I can follow the profile link for user  Christian Stoney
    and I can toggle following the user
    and I open the Dashboard
    and I filter the stream as  network
    then I cannot see updates by  Christian Stoney

Allan can open his tag filter stream and see only tags he is following
    Given I am logged in as the user allan_neece
    when I open the Dashboard
    and I filter the stream as  network
    then I cannot see updates tagged  confidential

Allan can add a tag to his tag filter stream and remove it again
    Given I am logged in as the user allan_neece
    and I open the Dashboard
    and I click the tag link  confidential
    when I can toggle following the tag
    and I open the Dashboard
    and I filter the stream as  network
    then I can see updates tagged  confidential
    and I click the tag link  confidential
    when I can toggle following the tag
    and I open the Dashboard
    and I filter the stream as  network
    then I cannot see updates tagged  confidential

Neil can view the tag stream
    Given I am logged in as the user neil_wichmann
    when I open the Dashboard
    and I write a status update    ${MESSAGE1}
    and I can add a tag    ${TAG1}
    and I submit the status update
    when I open the Dashboard    
    and I write a status update    ${MESSAGE2}
    and I can add a tag    ${TAG2}
    and I submit the status update
    then The message is visible as new status update and includes the tag    ${MESSAGE2}  ${TAG2}
    when I click the tag link  ${TAG2}
    then The message is visible as new status update and includes the tag    ${MESSAGE2}  ${TAG2}
    and The message is not visible  ${MESSAGE1}

Tagged content status updates link to the tagstream
    Given I am in a workspace as a workspace admin
    And I can create a new document    My created document
    And I tag the item  ${TAG3}
    And I save the document
    Comment  We can only tag after creation has already fired. Fire publication.
    When I can publish the content item
    And I open the Dashboard
    And the stream links to the document     My created document
    Then I click the tag link  ${TAG3}
    And the stream links to the document     My created document

Neil can follow and unfollow tags from the tagstream
    Given I am logged in as the user neil_wichmann
    when I open the Dashboard
    and I write a status update    ${MESSAGE1}
    and I can add a tag    ${TAG1}
    and I submit the status update
    and The message is visible as new status update and includes the tag    ${MESSAGE1}  ${TAG1}
    and I click the tag link  ${TAG1}
    and I am not following the tag
    when I can toggle following the tag
    then I am following the tag
    and I can reload the page
    and I am following the tag
    when I can toggle following the tag
    then I am not following the tag
    and I can reload the page
    and I am not following the tag


*** Keywords ***

