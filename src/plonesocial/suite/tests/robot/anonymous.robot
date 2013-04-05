*** Settings ***
Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/saucelabs.robot
Library   Dialogs

Test Setup  Open SauceLabs test browser
Test Teardown  Run keywords  Report test status  Close all browsers


*** Test Cases ***
Home view
      [Tags]                            anon  home
      Go to                             ${PLONE_URL}
      Page should contain               Powered by Plon
      # Element should not be visible     id=plonesocialsuite-navigation
      # Pause execution

      

