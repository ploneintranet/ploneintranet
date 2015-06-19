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

Manager can create a case workspace
    Given I'm logged in as a 'Manager'
     Then I can create a new case    A case for outer space
     Then I can delete a case  a-case-for-outer-space

Manager can change the workflow of a case workspace
    Given I'm logged in as a 'Manager'
     Then I can create a new case  Workflow case
     Then I can go to the sidebar tasks tile of my case
     Then I can close the first milestone
     Then I can delete a case  workflow-case

Manager can toggle the state of a task
    Given I'm logged in as a 'Manager'
     Then I can go to the Minifest
     Then I can go to the sidebar tasks tile of my case
     Then I can toggle a milestone  New
     Then I select the task check box  Basisdatenerfassung
     Then I can go to the Minifest
     Then I can go to the sidebar tasks tile of my case
     Then I see a task is complete  Basisdatenerfassung
     Then I unselect the task check box  Basisdatenerfassung
     Then I can go to the Minifest
     Then I can go to the sidebar tasks tile of my case
     Then I see a task is open  Basisdatenerfassung
     Then I can toggle a milestone  New

Non-member cannot see into a workspace
    Given I am logged in as the user alice_lindstrom
     when I can go to the Minifest
     then I am redirected to the login page

Manager can view sidebar info
    Given I am in a case workspace as a workspace admin
    I can go to the sidebar info tile

Member can view sidebar info
    Given I am in a case workspace as a workspace member
    I can go to the sidebar info tile

Manager can view sidebar tasks
    Given I am in a case workspace as a workspace admin
    Then I can go to the sidebar tasks tile of my case

Member can view sidebar tasks
    Given I am in a case workspace as a workspace member
     Then I can go to the sidebar tasks tile of my case

Manager can add a new task
    Given I am in a case workspace as a workspace admin
     Then I can go to the sidebar tasks tile of my case
     Then I can add a new task  Make a plan

Manager can mark a new task complete on dashboard
    Given I am in a case workspace as a workspace admin
     Then I can go to the sidebar tasks tile of my case
     Then I can add a new task  Todo soon
     Then I go to the dashboard
     Then I mark a new task complete
     Then I go to the dashboard
     Then I do not see the completed task is not listed

The manager can invite Alice to join the Minifest
    Given I am in a case workspace as a workspace admin
     Then I can open the workspace member settings tab
      And I can invite Alice to join the workspace

The manager can invite Alice to join the Minifest from the menu
    Given I am in a case workspace as a workspace admin
      And I can open the workspace member settings tab
     Then I can invite Alice to join the workspace from the menu


*** Keywords ***

# See lib/keywords.robot in the section "case related keywords"

