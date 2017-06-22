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

Alice can add a personal task
    Given I am logged in as the user alice_lindstrom
     Then I can go to the application  Todo
      And I have no personal tasks
     Then I create a personal task  My first task  Christian Stoney
     Then I delete the current document
      And I have no personal tasks

Allan can add a workspace task
    Given I am logged in as the user allan_neece
     Then I can go to the application  Todo
     Then I create a workspace task  My first task  Christian Stoney
     Then I delete the current document

Allan can use the todo apps filters
    Given I am logged in as the user allan_neece
     Then I can go to the application  Todo
     Then I can see that the first task is  Populate Metadata
     When I sort the results  Alphabetically
     Then I can see that the first task is  Budget
     When I filter the results by state  Closed
     Then I can see that the first task is  Identify the requirements
     [Documentation]  The filters are persistent through a cookie
     Then I can go to the application  Todo
      And I can see that the first task is  Identify the requirements
     When I reset the filters
     Then I can see that the first task is  Populate Metadata


*** Keywords ***

# See lib/keywords.robot in the section "case related keywords"

I have no personal tasks
    Wait until page contains element  jquery=#search-result .notice:contains(No results found)

I create a workspace task
    [arguments]  ${title}  ${assignee}
    Click link  Create new task
    I create a task  My first task  Christian Stoney

I create a personal task
    [arguments]  ${title}  ${assignee}
    Click Element  jquery=.create-document
    I create a task  My first task  Christian Stoney

I create a task
    [arguments]  ${title}  ${assignee}
    Wait for injection to be finished
    Input Text  xpath=//div[@class='panel-body']//input[@name='title']  text=${title}
    Input Text  xpath=//div[@class='panel-body']//textarea[@name='description']  text=Plan for success
    Input Text  css=label.assignee li.select2-search-field input  ${assignee}
    Wait Until Element Is visible  xpath=//span[@class='select2-match'][text()='${assignee}']
    Click Element  xpath=//span[@class='select2-match'][text()='${assignee}']
    Click Button  Create
    Wait Until Page Contains Element  jquery=.pat-notification-panel :contains('Close')
    Click Element  jquery=.pat-notification-panel :contains('Close')

I delete the current document
    Click Element  css=div.quick-functions a.icon-ellipsis
    Wait for injection to be finished
    Click Element  css=#extra-options a.icon-trash
    Wait for injection to be finished
    Click Button  I am sure, delete now
    Wait for injection to be finished

I can see that the first task is
    [arguments]  ${title}
    Wait for injection to be finished
    Page Should Contain Element  jquery=#search-result .panel-content :first a:contains(${title})

I sort the results
    [arguments]  ${title}
    Select From List  sort-mode  ${title}

I filter the results by state
    [arguments]  ${title}
    Select From List  state-mode  ${title} tasks

I reset the filters
    Click Button  Reset search and filters
