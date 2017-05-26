*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  ../lib/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  DebugLibrary

Variables  variables.py

Test Setup  Prepare test browser
Test Teardown  Close all browsers


*** Test Cases ***

Allan can use the todo app
    Given I am logged in as the user allan_neece
     Then I can go to the application  Todo
      And I have no personal tasks
     Then I create a personal task  My first task  Christian Stoney

*** Keywords ***

# See lib/keywords.robot in the section "case related keywords"

I have no personal tasks
    Wait until page contains element  jquery=#search-result .notice:contains(No results found)

I create a personal task
    [arguments]  ${title}  ${assignee}
    Click Element  jquery=.create-document
    Wait for injection to be finished
    Input Text  xpath=//div[@class='panel-body']//input[@name='title']  text=${title}
    Input Text  xpath=//div[@class='panel-body']//textarea[@name='description']  text=Plan for success
    # BBB Element Should Contain  xpath=//label[@class='initiator']//li[@class='select2-search-choice']/div  Allan Neece
    Input Text  css=label.assignee li.select2-search-field input  ${assignee}
    Wait Until Element Is visible  xpath=//span[@class='select2-match'][text()='${assignee}']
    Click Element  xpath=//span[@class='select2-match'][text()='${assignee}']
    Click Button  Create
    Wait Until Page Contains  ${title}
    Click Element  css=#toggle-sidebar .open
