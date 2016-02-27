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
${USERNAME1}   Alice Lindström
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

Alice can post a status update
    Given I am logged in as the user alice_lindstrom
    when I open the Dashboard
    and I post a status update    ${MESSAGE2}
    then The message is visible as new status update    ${MESSAGE2}
    and The message is visibile after a reload    ${MESSAGE2}

Allan can post a reply
    Given I am logged in as the user allan_neece
    when I open the Dashboard
    and I post a status update    ${MESSAGE1}
    then The message is visible as new status update    ${MESSAGE1}
    When I post a reply on a status update    ${MESSAGE1}    ${MESSAGE2}
    then The reply is visibile as a comment    ${MESSAGE1}    ${MESSAGE2}
    and The reply is visible after a reload    ${MESSAGE1}    ${MESSAGE2}

Esmeralda can reply to a reply
    Given I am logged in as the user esmeralda_claassen
    when I open the Dashboard
    and I post a status update    ${MESSAGE1}
    then The message is visible as new status update    ${MESSAGE1}
    When I post a reply on a status update    ${MESSAGE1}    ${MESSAGE2}
    then The reply is visibile as a comment    ${MESSAGE1}    ${MESSAGE2}
    When I post a reply on a status update    ${MESSAGE1}    ${MESSAGE3}
    then The reply is visibile as a comment    ${MESSAGE1}    ${MESSAGE3}
     And Both replies are visible    ${MESSAGE1}    ${MESSAGE3}    ${MESSAGE2}
    and Both replies are visible after a reload    ${MESSAGE1}    ${MESSAGE3}    ${MESSAGE2}

Member can reply to a reply in a workspace
    Given I am in a workspace as a workspace member
    and I post a status update    ${MESSAGE1}
    then The message is visible as new status update    ${MESSAGE1}
    When I post a reply on a status update    ${MESSAGE1}    ${MESSAGE2}
    then The reply is visibile as a comment    ${MESSAGE1}    ${MESSAGE2}
    When I post a reply on a status update    ${MESSAGE1}    ${MESSAGE3}
    then The reply is visibile as a comment    ${MESSAGE1}    ${MESSAGE3}
    And Both replies are visible    ${MESSAGE1}    ${MESSAGE3}    ${MESSAGE2}
    and Both replies are visible after a reload    ${MESSAGE1}    ${MESSAGE3}    ${MESSAGE2}

Global stream replies to workspace posts are only visible for members of that workspace
    Given I am in a workspace as a workspace member
    and I post a status update    ${MESSAGE1}
    and The message is visible as new status update    ${MESSAGE1}
    and I open the Dashboard
    and I post a reply on a status update    ${MESSAGE1}    ${MESSAGE2}
    and The reply is visibile as a comment    ${MESSAGE1}    ${MESSAGE2}
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

*** Keywords ***

The message is visible as new status update
    [arguments]  ${message}
    Wait Until Element Is visible  xpath=//div[@id='activity-stream']//div[@class='post item']//section[@class='post-content']//p[contains(text(), '${message}')][1]  2

The message is not visible
    [arguments]  ${message}
    Element should not be visible  xpath=//div[@id='activity-stream']//div[@class='post item']//section[@class='post-content']//p[contains(text(), '${message}')][1]  2

The message is visible as new status update that mentions the user
    [arguments]  ${message}  ${username}
    Wait Until Element Is visible  xpath=//div[@id='activity-stream']//div[@class='post item']//section[@class='post-content']//p[contains(text(), '${message}')][1]  2
    Wait Until Element Is visible  xpath=//div[@id='activity-stream']//div[@class='post item']//section[@class='post-content']//p//a[contains(text(), '@${username}')][1]  2

The message is visible as new status update and includes the tag
    [arguments]  ${message}  ${tag}
    Wait Until Element Is visible  xpath=//div[@id='activity-stream']//div[@class='post item']//section[@class='post-content']//p[contains(text(), '${message}')][1]  2
    Wait Until Element Is visible  xpath=//div[@id='activity-stream']//div[@class='post item']//section[@class='post-content']//p//span[contains(text(), '#${tag}')][1]  2

The status update only appears once
    [arguments]  ${message}
    Element should be visible  xpath=//div[@id='activity-stream']//div[@class='post item']//section[@class='post-content']//p[contains(text(), '${message}')][1]
    Element should not be visible  xpath=//div[@id='activity-stream']//div[@class='post item']//section[@class='post-content']//p[contains(text(), '${message}')][2]

The message is visibile after a reload
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

The reply is visibile as a comment
    [arguments]  ${message}  ${reply_message}
    Wait Until Element Is visible  xpath=//div[@id='activity-stream']//div[@class='post item']//section[@class='post-content']//p[contains(text(), '${message}')][1]//..//..//..//div[@class='comments']//section[@class='comment-content']//p[contains(text(), '${reply_message}')]

The reply is visible after a reload
    [arguments]  ${message}  ${reply_message}
    ${location} =  Get Location
    Go to    ${location}
    The reply is visibile as a comment  ${message}  ${reply_message}

Both replies are visible
    [arguments]  ${message}  ${reply_message1}  ${reply_message2}
    The reply is visibile as a comment  ${message}  ${reply_message1}
    The reply is visibile as a comment  ${message}  ${reply_message2}

Both replies are visible after a reload
    [arguments]  ${message}  ${reply_message1}  ${reply_message2}
    ${location} =  Get Location
    Go to    ${location}
    The reply is visibile as a comment  ${message}  ${reply_message1}
    The reply is visibile as a comment  ${message}  ${reply_message2}

I can add a tag
    [arguments]  ${tag}
    Click link    link=Add tags
    Wait Until Element Is visible    xpath=//form[@id='postbox-tags']
    Click element    css=input[name=tagsearch]
    Input text    css=input[name=tagsearch]  ${tag1}
    Wait Until Element Is visible  xpath=//form[@id='postbox-tags']//fieldset[contains(@class, 'search-active')]//a//strong[contains(text(), '${tag1}')][1]  2
    Click element  xpath=//form[@id='postbox-tags']//label/a/strong[contains(text(), '${tag}')]/../..
    Wait Until Element Is visible  xpath=//p[@class='content-mirror']//a[contains(text(), '#${tag}')][1]  2
    Click element    css=textarea.pat-content-mirror

I can add a tag and search for a tag
    [arguments]  ${tag1}  ${tag2}
    Click link    link=Add tags
    Wait Until Element Is visible    xpath=//form[@id='postbox-tags']
    Click element    css=input[name=tagsearch]
    Input text    css=input[name=tagsearch]  ${tag1}
    Wait Until Element Is visible  xpath=//form[@id='postbox-tags']//fieldset[contains(@class, 'search-active')]//a//strong[contains(text(), '${tag1}')][1]  2
    Click element  xpath=//form[@id='postbox-tags']//label/a/strong[contains(text(), '${tag1}')]/../..
    Wait Until Element Is visible  xpath=//p[@class='content-mirror']//a[contains(text(), '#${tag1}')][1]  2
    Click element    css=input[name=tagsearch]
    Input text    css=input[name=tagsearch]  ${tag2}
    Wait Until Element Is visible  xpath=//form[@id='postbox-tags']//fieldset[contains(@class, 'search-active')]//a//strong[contains(text(), '${tag2}')][1]  2
    Click element  xpath=//form[@id='postbox-tags']//label/a/strong[contains(text(), '${tag2}')]/../..
    Wait Until Element Is visible  xpath=//p[@class='content-mirror']//a[contains(text(), '#${tag2}')][1]  2
    Click element    css=textarea.pat-content-mirror

I can mention a user and search for a user
    [arguments]  ${username1}  ${username2}
    Click link    link=Mention people
    Wait Until Element Is visible    xpath=//form[@id='postbox-users']
    Click element  xpath=//form[@id='postbox-users']//label/a/strong[contains(text(), '${username1}')]/../..
    Wait Until Element Is visible  xpath=//p[@class='content-mirror']//a[contains(text(), '@${username1}')][1]  2
    Click element    css=input[name=usersearch]
    Input text    css=input[name=usersearch]  ${username2}
    Wait Until Element Is visible  xpath=//form[@id='postbox-users']//fieldset[contains(@class, 'search-active')]//a//strong[contains(text(), '${username2}')][1]  2
    Click element  xpath=//form[@id='postbox-users']//label/a/strong[contains(text(), '${username2}')]/../..
    Wait Until Element Is visible  xpath=//p[@class='content-mirror']//a[contains(text(),'${username2}')][1]  2
    Click element    css=textarea.pat-content-mirror
