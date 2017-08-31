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

Admin can use the administrator tool app
    Given I'm logged in as a 'Site Administrator'
     Then I can go to the application  Administrator Tool
      And I can see the first search result is  Esmeralda Claassen
      And I can deactivate  Jorge Primavera
      And I can activate  Jorge Primavera
      And I can filter the users
     Then I can add the user  john_doe  John  Doe  jd@example.net
      # BBB: the user is automatically activate,
      # we need some pending user to test this one
      # And I can activate the new user  John Doe
     Then I can sort the users by creation date
      And I can see the first search result is  John Doe


*** Keywords ***

# See lib/keywords.robot in the section "case related keywords"
I can add the user
    [arguments]  ${username}  ${first_name}  ${last_name}  ${email}
    Click Link  jquery=#group-management-group-filter .icon.create
    Wait for injection to be finished
    Input text  jquery=.wizard-box [name=username]  ${username}
    Input text  jquery=.wizard-box [name=first_name]  ${first_name}
    Input text  jquery=.wizard-box [name=last_name]  ${last_name}
    Input text  jquery=.wizard-box [name=email]  ${email}
    Click Button  Create user account
    Wait for injection to be finished
    Page should contain Element  jquery=li:contains('${first_name} ${last_name}')


I can deactivate
    [arguments]  ${fullname}
    I can modify the state for user  ${fullname}  Enabled  Deactivate user

I can activate
    [arguments]  ${fullname}
    I can modify the state for user  ${fullname}  Disabled  Activate user

I can activate the new user
    [arguments]  ${fullname}
    I can modify the state for user  ${fullname}  Pending  Activate user

I can modify the state for user
    [arguments]  ${fullname}  ${state}  ${action}
    Wait for injection to be finished
    Click Element  jquery=li:contains(${fullname}) > .functions > a.user-status:contains(${state})
    Wait for injection to be finished
    Click Button  ${action}
    Wait for injection to be finished
    Click Button  Close

I can filter the users
    Wait for injection to be finished
    Input text  jquery=#group-management-group-filter [name=SearchableText]  st
    Wait for injection to be finished
    Page should contain Element  jquery=li:contains('Christian Stoney')
    Page should not contain Element  jquery=li:contains('Dollie Nocera')
    Input text  jquery=#group-management-group-filter [name=SearchableText]  strange
    Wait for injection to be finished
    Page should contain Element  jquery=#directory .notice:contains('No users found')

I can sort the users by creation date
    Select From List  sorting  -created
    Input text  jquery=#group-management-group-filter [name=SearchableText]  ${EMPTY}\n
    Wait for injection to be finished

I can see the first search result is
    [arguments]  ${fullname}
    Page should contain element  jquery=.user-account:first:contains(${fullname})
