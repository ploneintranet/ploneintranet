*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  ../lib/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  DebugLibrary

Test Setup  Prepare test browser
Test Teardown  Close all browsers

*** Variable ***

${MESSAGE1}    What a thing to say - and on my birthday!
${MESSAGE2}    something I need to get off my chest.
${MESSAGE3}    Why would you say that?

*** Test Cases ***


Allan can access messaging via the topbar
    Given I am logged in as the user allan_neece
     Then I can see my unread message count is  6
     When I click the message counter
     Then I can see an unread conversation with  guy_hackey
     When I open the conversation with  guy_hackey
     Then I can see a message  ${MESSAGE1}
      And I can not see an unread conversation

Allan can access messaging via the apps section
    Given I am logged in as the user allan_neece
     When I go to the apps section
      And The messaging app indicates unread messages  6
     When I click the messaging app
     Then I can see an unread conversation with  guy_hackey

Allan can send a new message to Alice
    Given I am logged in as the user allan_neece
      And I open the messaging app
      And I open the conversation with  alice_lindstrom
     Then I can see a message  ${MESSAGE2}
      And I can send a new message  ${MESSAGE3}
     When I am logged in as the user alice_lindstrom
      And I open the messaging app
      And I can see the byline  ${MESSAGE3}
      And I open the conversation with  allan_neece
     Then I can see a message  ${MESSAGE3}

Dollie can start a new conversation with Esmeralda
    Given I am logged in as the user dollie_nocera
     When I open the messaging app
     Then I can start a new conversation with  esmeralda_claassen
      And I can send a new message  Hi Esmeralda, welcome aboard.
     When I am logged in as the user esmeralda_claassen
      And I open the messaging app
     Then I can see an unread conversation with  dollie_nocera
      And I open the conversation with  dollie_nocera
      And I can see a message  Hi Esmeralda, welcome aboard.

Guido can search his inbox
    Given I am logged in as the user guido_stevens
      And I open the messaging app
      And I can see a conversation with  jamie_jacko
      And I can see a conversation with  alice_lindstrom
     When I search a conversation  strom
     Then I can see a conversation with  alice_lindstrom
      And I can not see a conversation with  jamie_jacko


*** Keywords ***

I can see my unread message count is
    [arguments]  ${count}
    Element Should Be Visible  xpath=//a[@id="messages-link"]/sup[contains(text(), '${count}')]

I click the message counter
    Click Link  css=#messages-link

I go to the apps section
    Go To  ${PLONE_URL}/apps.html

The messaging app indicates unread messages
    [arguments]  ${count}
    Element Should Be Visible  xpath=//div[contains(@class, "app-messages")]//sup[contains(text(), '${count}')]

I click the messaging app
    Click Link  css=div.app-messages a.link

I open the messaging app
    Go To  ${PLONE_URL}/apps/@@app-messaging

I can see a conversation with
    [arguments]  ${userid}
    Page Should Contain Element  css=label#selector-item-${userid}

I can not see a conversation with
    [arguments]  ${userid}
    Page Should Not Contain Element  css=label#selector-item-${userid}

I can see an unread conversation with
    [arguments]  ${userid}
    Page Should Contain Element  css=label#selector-item-${userid}.unread

I can not see an unread conversation
    Page Should Not Contain Element  css=#selector-items label.unread

I can see the byline
    [arguments]  ${text}
    Page Should Contain Element  xpath=//dfn[@class='byline'][contains(text(), "${text}")]

I open the conversation with
    [arguments]  ${userid}
    Click Element  css=label#selector-item-${userid}
    Wait Until Page Does Not Contain  css=#document-body.injecting

I can see a message
    [arguments]  ${text}
    Page Should Contain Element  xpath=//ul[@class='chat']//p[@class='content'][contains(text(), "${text}")]

I can send a new message
    [arguments]  ${text}
    Click Element  css=#chat-bar input[name='message']
    Input Text  css=#chat-bar input[name='message']  ${text}\n
    Wait Until Page Does Not Contain  css=#chat-bar.injecting

I can start a new conversation with
    [arguments]  ${userid}
    Click Link  css=div.quick-functions a.new-chat
    Input Text  css=#pat-modal div.users input.focus  ${userid}
    Wait Until Page Contains Element  xpath=//div[@class='select2-result-label'][contains(text(), ${userid})]
    Click Element  xpath=//div[@class='select2-result-label'][contains(text(), ${userid})]
    Click Element  css=button.close-panel[type='submit']

I search a conversation
    [arguments]  ${query}
    Input Text  css=input[name="search"]  ${query}
    Wait Until Page Does Not Contain Element  xpath=//form[@id='selector-items'][contains(@class, 'injecting')]
