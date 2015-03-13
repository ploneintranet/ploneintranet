*** Settings ***
Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/saucelabs.robot
#Library   Dialogs
Library   Remote  ${PLONE_URL}/RobotRemote

Test Setup     Open SauceLabs test browser
Test Teardown  Run keywords  Report test status  Close all browsers

*** Test Cases ***


DebugHome
    [Tags]  debug home
    Go to  ${PLONE_URL}
#    Pause execution
