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

Neil can view tagged posts
    Given I am logged in as the user neil_wichmann
    when I open the Dashboard
    and I write a status update    ${MESSAGE1}
    and I can add a tag    ${TAG1}
    and I submit the status update
    and I write a status update    ${MESSAGE2}
    and I can add a tag    ${TAG2}
    and I submit the status update
    then The message is visible as new status update and includes the tag    ${MESSAGE2}  ${TAG2}
    when I click the tag link  ${TAG2}
    then The message is visible as new status update and includes the tag    ${MESSAGE2}  ${TAG2}
    and The message is not visible  ${MESSAGE1}
    
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

The message is visible as new status update
    [arguments]  ${message}
    Wait Until Element Is visible  xpath=//div[@id='activity-stream']//div[@class='post item']//section[@class='post-content']//p[contains(text(), '${message}')][1]

The reply is visible
    [arguments]  ${message}
    Wait Until Element Is visible  xpath=//div[@id='activity-stream']//div[@class='post item']//section[@class='comment-content']//p[contains(text(), '${message}')][1]

The message is not visible
    [arguments]  ${message}
    Element should not be visible  xpath=//div[@id='activity-stream']//div[@class='post item']//section[@class='post-content']//p[contains(text(), '${message}')][1]

The message is visible as new status update that mentions the user
    [arguments]  ${message}  ${username}
    Wait Until Element Is visible  xpath=//div[@id='activity-stream']//div[@class='post item']//section[@class='post-content']//p[contains(text(), '${message}')][1]
    Wait Until Element Is visible  xpath=//div[@id='activity-stream']//div[@class='post item']//section[@class='post-content']//p//a[contains(text(), '@${username}')][1]

The message is visible as new status update and includes the tag
    [arguments]  ${message}  ${tag}
    Wait Until Element Is visible  xpath=//div[@id='activity-stream']//div[@class='post item']//section[@class='post-content']//p[contains(text(), '${message}')][1]
    Wait Until Element Is visible  xpath=//div[@id='activity-stream']//div[@class='post item']//section[@class='post-content']//p//a[contains(text(), '#${tag}')][1]

I click the tag link
    [arguments]  ${tag}
    Click Link  \#${tag}

The status update only appears once
    [arguments]  ${message}
    Element should be visible  xpath=//div[@id='activity-stream']//div[@class='post item']//section[@class='post-content']//p[contains(text(), '${message}')][1]
    Element should not be visible  xpath=//div[@id='activity-stream']//div[@class='post item']//section[@class='post-content']//p[contains(text(), '${message}')][2]

The message is visible after a reload
    [arguments]  ${message}
    ${location} =  Get Location
    Go to    ${location}
    The message is visible as new status update    ${message}

I post a reply on a status update
    [arguments]  ${message}  ${reply_message}
    Click Element  xpath=//div[@id='activity-stream']//div[@class='post item']//section[@class='post-content']//p[contains(text(), '${message}')]//..//..//../textarea[contains(@class, 'pat-content-mirror')]
    Wait Until Element Is visible  xpath=//div[@id='activity-stream']//div[@class='post item']//section[@class='post-content']//p[contains(text(), '${message}')]//..//..//../button[@name='form.buttons.statusupdate']
    Input Text  xpath=//div[@id='activity-stream']//div[@class='post item']//section[@class='post-content']//p[contains(text(), '${message}')]//..//..//../textarea[contains(@class, 'pat-content-mirror')]  ${reply_message}
    Click button  xpath=//div[@id='activity-stream']//div[@class='post item']//section[@class='post-content']//p[contains(text(), '${message}')]//..//..//../button[@name='form.buttons.statusupdate']

The reply is visible as a comment
    [arguments]  ${message}  ${reply_message}
    Wait Until Element Is visible  xpath=//div[@id='activity-stream']//div[@class='post item']//section[@class='post-content']//p[contains(text(), '${message}')][1]//..//..//..//div[@class='comments']//section[@class='comment-content']//p[contains(text(), '${reply_message}')]

The reply is not visible
    [arguments]  ${message}
    Element should not be visible  xpath=//div[@id='activity-stream']//div[@class='post item']//div[@class='comments']//section[@class='comment-content']//p[contains(text(), '${message}')]

The reply is visible after a reload
    [arguments]  ${message}  ${reply_message}
    ${location} =  Get Location
    Go to    ${location}
    The reply is visible as a comment  ${message}  ${reply_message}

Both replies are visible
    [arguments]  ${message}  ${reply_message1}  ${reply_message2}
    The reply is visible as a comment  ${message}  ${reply_message1}
    The reply is visible as a comment  ${message}  ${reply_message2}

Both replies are visible after a reload
    [arguments]  ${message}  ${reply_message1}  ${reply_message2}
    ${location} =  Get Location
    Go to    ${location}
    The reply is visible as a comment  ${message}  ${reply_message1}
    The reply is visible as a comment  ${message}  ${reply_message2}

I can add a tag
    [arguments]  ${tag}
    Click link    link=Add tags
    Wait Until Element Is visible    xpath=//form[@id='postbox-tags']
    Click element    css=input[name=tagsearch]
    Input text    css=input[name=tagsearch]  ${tag}
    [Documentation]  Wait until the temporary class 'injecting-content' has been removed, to be sure injection has completed
    Wait until page does not contain element  xpath=//form[@id='postbox-tags' and contains(@class, 'injecting-content')]
    Wait Until Element Is visible  xpath=//form[@id='postbox-tags']//fieldset[contains(@class, 'search-active')]//a//strong[contains(text(), '${tag}')][1]
    Click element  xpath=//form[@id='postbox-tags']//label/a/strong[contains(text(), '${tag}')]/../..
    Wait Until Element Is visible  xpath=//p[@class='content-mirror']//a[contains(text(), '#${tag}')][1]
    Click element    css=textarea.pat-content-mirror

I can add a tag and search for a tag
    [arguments]  ${tag1}  ${tag2}
    Click link    link=Add tags
    Wait Until Element Is visible    xpath=//form[@id='postbox-tags']
    Click element    css=input[name=tagsearch]
    Input text    css=input[name=tagsearch]  ${tag1}
    Wait Until Element Is visible  xpath=//form[@id='postbox-tags']//fieldset[contains(@class, 'search-active')]//a//strong[contains(text(), '${tag1}')][1]
    Click element  xpath=//form[@id='postbox-tags']//label/a/strong[contains(text(), '${tag1}')]/../..
    Wait Until Element Is visible  xpath=//p[@class='content-mirror']//a[contains(text(), '#${tag1}')][1]
    Click element    css=input[name=tagsearch]
    Input text    css=input[name=tagsearch]  ${tag2}
    [Documentation]  Wait until the temporary class 'injecting-content' has been removed, to be sure injection has completed
    Wait until page does not contain element  xpath=//form[@id='postbox-tags' and contains(@class, 'injecting-content')]
    Wait Until Element Is visible  xpath=//form[@id='postbox-tags']//fieldset[contains(@class, 'search-active')]//a//strong[contains(text(), '${tag2}')][1]
    Click element  xpath=//form[@id='postbox-tags']//label/a/strong[contains(text(), '${tag2}')]/../..
    Wait Until Element Is visible  xpath=//p[@class='content-mirror']//a[contains(text(), '#${tag2}')][1]
    Click element    css=textarea.pat-content-mirror

I can mention a user and search for a user
    [arguments]  ${username1}  ${username2}
    Click link    link=Mention people
    Wait Until Element Is visible    xpath=//form[@id='postbox-users']
    Click element  xpath=//form[@id='postbox-users']//label/a/strong[contains(text(), '${username1}')]/../..
    Wait Until Element Is visible  xpath=//p[@class='content-mirror']//a[contains(text(), '@${username1}')][1]
    Click element    css=input[name=usersearch]
    Input text    css=input[name=usersearch]  ${username2}
    [Documentation]  Wait until the temporary class 'injecting-content' has been removed, to be sure injection has completed
    Wait until page does not contain element  xpath=//form[@id='postbox-users' and contains(@class, 'injecting-content')]
    Wait Until Element Is visible  xpath=//form[@id='postbox-users']//fieldset[contains(@class, 'search-active')]//a//strong[contains(text(), '${username2}')][1]
    Click element  xpath=//form[@id='postbox-users']//label/a/strong[contains(text(), '${username2}')]/../..
    Wait Until Element Is visible  xpath=//p[@class='content-mirror']//a[contains(text(),'${username2}')][1]
    Click element    css=textarea.pat-content-mirror

The content stream is visible
    Wait until element is visible       css=#comments-document-comments

I save the document
    Click Button  Save
    Wait Until Page Contains  Your changes have been saved

The stream contains
    [arguments]    ${text}
    Wait until page contains    ${text}

The stream links to the document
    [arguments]  ${text}
    Wait until page contains element       link=${text}

The stream does not link to the document
    [arguments]  ${text}
    Page should not contain       link=${text}    