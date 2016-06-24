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

Manager can post a status update
    Given I'm logged in as a 'Manager'
    when I open the Dashboard
    and I post a status update    ${MESSAGE1}
    then The message is visible as new status update    ${MESSAGE1}
    and The status update only appears once    ${MESSAGE1}
    Comment  Cleanup for easier interactive testing    
    I delete the status update    ${MESSAGE1}

Alice can post a status update
    Given I am logged in as the user alice_lindstrom
    when I open the Dashboard
    and I post a status update    ${MESSAGE2}
    then The message is visible as new status update    ${MESSAGE2}
    and The message is visible after a reload    ${MESSAGE2}
    Comment  Cleanup for easier interactive testing    
    I delete the status update    ${MESSAGE2}

Alice can delete modify status update of herself
    Given I am logged in as the user alice_lindstrom
    when I open the Dashboard
    and I post a status update    ${MESSAGE1}
    when I delete the status update    ${MESSAGE1}
    then I can see the status delete confirmation
    And the message is not visible    ${MESSAGE1}
    when I open the Dashboard
    Then the message is not visible    ${MESSAGE1}

Manager can delete modify status update of anybody
    Given I am logged in as the user alice_lindstrom
    when I open the Dashboard
    and I post a status update    ${MESSAGE1}
    When I'm logged in as a 'Manager'
    and I open the Dashboard
    and I delete the status update    ${MESSAGE1}
    then I can see the status delete confirmation
    And the message is not visible    ${MESSAGE1}
    when I open the Dashboard
    Then the message is not visible    ${MESSAGE1}

Alice can edit modify status update of herself
    Given I am logged in as the user alice_lindstrom
    when I open the Dashboard
    and I post a status update    ${MESSAGE1}
    then I can edit the status update    ${MESSAGE1}  ${MESSAGE2}
    and The message is visible after a reload    ${MESSAGE2}
    and the message is not visible    ${MESSAGE1}
    and I can access the original text  ${MESSAGE1}  ${MESSAGE2}
    Comment  Cleanup for easier interactive testing    
    I delete the status update    ${MESSAGE2}

Manager can edit modify status update of anybody
    Given I am logged in as the user alice_lindstrom
    when I open the Dashboard
    and I post a status update    ${MESSAGE1}
    When I'm logged in as a 'Manager'
    and I open the Dashboard    
    then I can edit the status update    ${MESSAGE1}  ${MESSAGE2}
    and The message is visible after a reload    ${MESSAGE2}
    and the message is not visible    ${MESSAGE1}
    and I can access the original text  ${MESSAGE1}  ${MESSAGE2}
    Comment  Cleanup for easier interactive testing    
    I delete the status update    ${MESSAGE2}

Allan cannot edit or delete modify status update of others
    Given I am logged in as the user alice_lindstrom
    when I open the Dashboard
    and I post a status update    ${MESSAGE1}
    When I am logged in as the user allan_neece
    and I open the Dashboard
    Then I cannot open the post action menu    ${MESSAGE1}
    Comment  Cleanup for easier interactive testing
    I am logged in as the user alice_lindstrom
    I open the dashboard
    I delete the status update    ${MESSAGE1}

Allan can post a reply
    Given I am logged in as the user allan_neece
    when I open the Dashboard
    and I post a status update    ${MESSAGE1}
    then The message is visible as new status update    ${MESSAGE1}
    When I post a reply on a status update    ${MESSAGE1}    ${MESSAGE2}
    then The reply is visible as a comment    ${MESSAGE1}    ${MESSAGE2}
    and The reply is visible after a reload    ${MESSAGE1}    ${MESSAGE2}

Esmeralda can reply to a reply
    Given I am logged in as the user esmeralda_claassen
    when I open the Dashboard
    and I post a status update    ${MESSAGE1}
    then The message is visible as new status update    ${MESSAGE1}
    When I post a reply on a status update    ${MESSAGE1}    ${MESSAGE2}
    then The reply is visible as a comment    ${MESSAGE1}    ${MESSAGE2}
    When I post a reply on a status update    ${MESSAGE1}    ${MESSAGE3}
    then The reply is visible as a comment    ${MESSAGE1}    ${MESSAGE3}
     And Both replies are visible    ${MESSAGE1}    ${MESSAGE3}    ${MESSAGE2}
    and Both replies are visible after a reload    ${MESSAGE1}    ${MESSAGE3}    ${MESSAGE2}

Alice can delete modify status reply of herself
    Given I am logged in as the user alice_lindstrom
    when I open the Dashboard
    and I post a status update    ${MESSAGE1}
    and I post a reply on a status update    ${MESSAGE1}    ${MESSAGE2}
    when I delete the status reply    ${MESSAGE2}
    then I can see the status reply delete confirmation
    And The reply is not visible    ${MESSAGE2}
    when I open the Dashboard
    Then The reply is not visible   ${MESSAGE2}
    Comment  Cleanup for easier interactive testing        
    I delete the status update    ${MESSAGE1}

Manager can delete modify status reply of anybody
    Given I am logged in as the user alice_lindstrom
    when I open the Dashboard
    and I post a status update    ${MESSAGE1}
    and I post a reply on a status update    ${MESSAGE1}    ${MESSAGE2}
    When I'm logged in as a 'Manager'
    and I open the Dashboard    
    when I delete the status reply    ${MESSAGE2}
    then I can see the status reply delete confirmation
    And The reply is not visible    ${MESSAGE2}
    when I open the Dashboard
    Then The reply is not visible   ${MESSAGE2}
    Comment  Cleanup for easier interactive testing        
    I delete the status update    ${MESSAGE1}

Allan cannot edit or delete modify status reply of others
    Given I am logged in as the user alice_lindstrom
    when I open the Dashboard
    and I post a status update    ${MESSAGE1}
    and I post a reply on a status update    ${MESSAGE1}    ${MESSAGE2}    
    When I am logged in as the user allan_neece
    and I open the Dashboard
    Then I cannot open the comment action menu    ${MESSAGE2}
    Comment  Cleanup for easier interactive testing
    I am logged in as the user alice_lindstrom
    I open the dashboard
    I delete the status update    ${MESSAGE1}

Alice can edit modify status reply of herself
    Given I am logged in as the user alice_lindstrom
    when I open the Dashboard
    and I post a status update    ${MESSAGE1}
    and I post a reply on a status update    ${MESSAGE1}    ${MESSAGE2}    
    then I can edit the status reply    ${MESSAGE2}  ${MESSAGE3}
    and The reply is not visible    ${MESSAGE2}    
    and The reply is visible after a reload    ${MESSAGE1}  ${MESSAGE3}
    and I can access the original reply text  ${MESSAGE2}  ${MESSAGE3}
    Comment  Cleanup for easier interactive testing    
    I delete the status update    ${MESSAGE1}

Manager can edit modify status reply of anybody
    Given I am logged in as the user alice_lindstrom
    when I open the Dashboard
    and I post a status update    ${MESSAGE1}
    and I post a reply on a status update    ${MESSAGE1}    ${MESSAGE2}
    When I'm logged in as a 'Manager'
    and I open the Dashboard        
    then I can edit the status reply    ${MESSAGE2}  ${MESSAGE3}
    and The reply is not visible    ${MESSAGE2}    
    and The reply is visible after a reload    ${MESSAGE1}  ${MESSAGE3}
    and I can access the original reply text  ${MESSAGE2}  ${MESSAGE3}
    Comment  Cleanup for easier interactive testing    
    I delete the status update    ${MESSAGE1}

Member can reply to a reply in a workspace
    Given I am in a workspace as a workspace member
    and I post a status update    ${MESSAGE1}
    then The message is visible as new status update    ${MESSAGE1}
    When I post a reply on a status update    ${MESSAGE1}    ${MESSAGE2}
    then The reply is visible as a comment    ${MESSAGE1}    ${MESSAGE2}
    When I post a reply on a status update    ${MESSAGE1}    ${MESSAGE3}
    then The reply is visible as a comment    ${MESSAGE1}    ${MESSAGE3}
    And Both replies are visible    ${MESSAGE1}    ${MESSAGE3}    ${MESSAGE2}
    and Both replies are visible after a reload    ${MESSAGE1}    ${MESSAGE3}    ${MESSAGE2}

Global stream replies to workspace posts are only visible for members of that workspace
    Given I am in a workspace as a workspace member
    and I post a status update    ${MESSAGE1}
    and The message is visible as new status update    ${MESSAGE1}
    and I open the Dashboard
    and I post a reply on a status update    ${MESSAGE1}    ${MESSAGE2}
    and The reply is visible as a comment    ${MESSAGE1}    ${MESSAGE2}
    and I post a status update    ${MESSAGE3}
    and The message is visible as new status update    ${MESSAGE3}
    When I am logged in as the user alice_lindstrom
    and I open the Dashboard
    Then the message is not visible    ${MESSAGE1}
    and the message is not visible    ${MESSAGE2}
    and The message is visible as new status update    ${MESSAGE3}

Member can mention a user
    Given I am in a workspace as a workspace member
    and I write a status update    ${MESSAGE1}
    then I can mention the user    ${USERNAME1}
    When I submit the status update
    then The message is visible as new status update that mentions the user    ${MESSAGE1}  ${USERNAME1}

Member can mention a user found by searching
    Given I am in a workspace as a workspace member
    and I write a status update    ${MESSAGE3}
    then I can mention a user and search for a user    ${USERNAME1}  ${USERNAME2}
    When I submit the status update
    then The message is visible as new status update that mentions the user    ${MESSAGE3}  ${USERNAME1}
    then The message is visible as new status update that mentions the user    ${MESSAGE3}  ${USERNAME2}

Neil can tag a post
    Given I am logged in as the user neil_wichmann
    when I open the Dashboard
    and I write a status update    ${MESSAGE2}
    then I can add a tag    ${TAG1}
    When I submit the status update
    then The message is visible as new status update and includes the tag    ${MESSAGE2}  ${TAG1}

Neil can tag a post by searching for a tag
    Given I am in a workspace as a workspace member
    and I write a status update    ${MESSAGE2}
    then I can add a tag and search for a tag    ${TAG1}  ${TAG2}
    When I submit the status update
    then The message is visible as new status update and includes the tag    ${MESSAGE2}  ${TAG1}
    then The message is visible as new status update and includes the tag    ${MESSAGE2}  ${TAG2}

Creating a page creates a statusupdate
    Given I am in a workspace as a workspace member
    And I can create a new document    My created document
    When I save the document    
    Then the content stream is visible
    And the stream contains     0 comments on 1 shares
    When I go to the Open Market Committee Workspace
    Then the stream links to the document     My created document
    When I open the Dashboard
    Then the stream links to the document     My created document

Publishing a page creates a statusupdate
    Given I am in a workspace as a workspace member
    And I can create a new document    My created document
    And I save the document
    When I am logged in as the user christian_stoney
    And maneuver to   My created document
    Then I can publish the content item
    And the content stream is visible
    And the stream contains     published this item
    When I go to the Open Market Committee Workspace
    Then the stream contains     published
    When I open the Dashboard
    Then the stream contains     published

Content status updates respect document security
    Given I am in a workspace as a workspace admin
    And I can create a new document    My created document
    And I save the document
    And I open the Dashboard
    Then the stream links to the document     My created document    
    When I am logged in as the user allan_neece
    And I open the Dashboard
    Then the stream does not link to the document       My created document

*** Keywords ***

