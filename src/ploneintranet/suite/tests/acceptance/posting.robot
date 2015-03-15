*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  ../lib/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  DebugLibrary

Test Setup  Open test browser
Test Teardown  Close all browsers

*** Variable ***

${MESSAGE1}    I am so excited, this is super!
${MESSAGE2}    Living next door to Alice
${MESSAGE3}    You know nothing, Jon Snow!


*** Test Cases ***

Manager can post a status update
    Given I'm logged in as a 'Manager'
    when I open the Dashboard
    and I post a status update    ${MESSAGE1}
    then The message is visible as new status update    ${MESSAGE1}
    and The status update only appears once    ${MESSAGE1}

Alice can post a status update
    Given I'm logged in as a 'alice_lindstrom'
    when I open the Dashboard
    and I post a status update    ${MESSAGE2}
    then The message is visible as new status update    ${MESSAGE2}
    and The message is visibile after a reload    ${MESSAGE2}

Allan can post a reply
    Given I'm logged in as a 'allan_neece'
    when I open the Dashboard
    and I post a status update    ${MESSAGE1}
    then The message is visible as new status update    ${MESSAGE1}
    When I post a reply on a status update    ${MESSAGE1}    ${MESSAGE2}
    then The reply is visibile as a comment    ${MESSAGE1}    ${MESSAGE2}
    and The reply is visible after a reload    ${MESSAGE1}    ${MESSAGE2}

Esmeralda can reply to a reply
    Given I'm logged in as a 'esmeralda_claassen'
    when I open the Dashboard
    and I post a status update    ${MESSAGE1}
    then The message is visible as new status update    ${MESSAGE1}
    When I post a reply on a status update    ${MESSAGE1}    ${MESSAGE2}
    then The reply is visibile as a comment    ${MESSAGE1}    ${MESSAGE2}
    When I post a reply on a status update    ${MESSAGE1}    ${MESSAGE3}
    then The reply is visibile as a comment    ${MESSAGE1}    ${MESSAGE3}
    and Both replies are visible after a reload    ${MESSAGE1}    ${MESSAGE3}    ${MESSAGE2}


# Jesse can add tags to a status update
#     Given I'm logged in as a 'jesse_shaik'
#     when I open the Dashboard
#     and I write a status update    ${MESSAGE3}

*** Keywords ***

I write a status update
    [arguments]  ${message}
    Wait Until Element Is visible  css=textarea.pat-content-mirror
    Element should not be visible  css=button[name='form.buttons.statusupdate']
    Click element  css=textarea.pat-content-mirror
    Wait Until Element Is visible  css=button[name='form.buttons.statusupdate']
    Input Text  css=textarea.pat-content-mirror  ${message}

I post a status update
    [arguments]  ${message}
    I write a status update    ${message}
    Click button  css=button[name='form.buttons.statusupdate']


The message is visible as new status update
    [arguments]  ${message}
    Wait Until Element Is visible  xpath=//div[@id='activity-stream']//div[@class='post item']//section[@class='post-content']//p[contains(text(), '${message}')][1]

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

Both replies are visible after a reload
    [arguments]  ${message}  ${reply_message1}  ${reply_message2}
    ${location} =  Get Location
    Go to    ${location}
    The reply is visibile as a comment  ${message}  ${reply_message1}
    The reply is visibile as a comment  ${message}  ${reply_message2}