*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  ../lib/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Prepare test browser
Test Teardown  Close all browsers

*** Test Cases ***

Site Administrator can access dashboard
    Given I'm logged in as a 'Site Administrator'
     and I open the Dashboard
     then I am logged in as site administrator
     and I see the Dashboard

Allan can view the custom dashboard
    [Tags]  Heisenbug
    Given I am logged in as the user allan_neece
     When I open the Dashboard
      And I select the dashboard  custom
     Then I see the default custom dashboard
     When I customize the custom dashboard
     Then I see the customized custom dashboard
     When I reset the custom dashboard
     Then I see the default custom dashboard
     When I select the dashboard  activity
     Then I cannot see the pencil icon

*** Keywords ***

I see the Dashboard
    Element should be visible  css=#activity-stream

I select the dashboard
    [arguments]  ${dashboard_type}
    Select from list  dashboard  ${dashboard_type}
    Wait for injection to be finished

I see the default custom dashboard
    Element should be visible  css=#portlet-news.portlet.span-1
    Element should be visible  css=#portlet-library.portlet.span-1

I cannot see the pencil icon
    Element should not be visible  css=.icon.edit.pat-modal

I customize the custom dashboard
    Click element  css=.icon.edit.pat-modal
    Wait for injection to be finished
    Select from list  jquery=[name="display-./@@news.tile?title=News"]  span-2
    Select from list  jquery=[name="display-./@@my_documents.tile?title=My docs"]  none
    Click Element  css=#pat-modal button[name=save]
    Wait for injection to be finished

I see the customized custom dashboard
    Element should be visible  css=#portlet-news.portlet.span-2
    Element should not be visible  css=#portlet-library

I reset the custom dashboard
    [Documentation]  There is an hidden (for the moment) button to restore the default cutom dashboard, we are going to show it with some javascript
    Click element  css=.icon.edit.pat-modal
    Wait for injection to be finished
    Execute javascript  jQuery('.pat-modal [name=restore]').removeAttr('hidden')
    Click Element  css=#pat-modal button[name=restore]
    Wait for injection to be finished
