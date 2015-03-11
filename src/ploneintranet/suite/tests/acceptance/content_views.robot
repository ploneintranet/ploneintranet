*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  ../lib/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  DebugLibrary

Test Setup  Open test browser
Test Teardown  Close all browsers

*** Test Cases ***

Alice can change the title of a document
    Given I'm logged in as a 'alice_lindstrom'
    And I browse to a document
    And I change the title
    And I view a document
    The document has the new title

Alice can change the description of a document
    Given I'm logged in as a 'alice_lindstrom'
    And I browse to a document
    And I change the description
    And I view a document
    The document has the new description

Alice can tag a document
    Given I'm logged in as a 'alice_lindstrom'
    And I browse to a document
    And I tag the description
    And I view a document
    The document has the new tag

*** Keywords ***
I browse to a document
    Go To  ${PLONE_URL}/workspaces/open-market-committee
    Click Link  link=Manage Information
    Click Link  xpath=//a[contains(@href, 'public-bodies-reform')]

I view a document
    Go To  ${PLONE_URL}/workspaces/open-market-committee/manage-information/public-bodies-reform

I change the title
    Comment  Toggle the metadata to give the JavaScript time to load
    Click Link  link=Toggle extra metadata
    Click Link  link=Toggle extra metadata
    Input Text  title  New title ♥
    Click Button  Save

The document has the new title
    Textfield Should Contain  title  New title ♥

I change the description
    Click Link  link=Toggle extra metadata
    Input Text  xpath=//textarea[@name='description']  New description ☀
    Click Button  Save

The document has the new description
    Page Should Contain  New description ☀

I tag the description
    Click Link  link=Toggle extra metadata
    Input Text  id=s2id_autogen2  NewTag☃,
    Click Button  Save

The document has the new tag
    Click Link  link=Toggle extra metadata
    Page Should Contain  NewTag☃
