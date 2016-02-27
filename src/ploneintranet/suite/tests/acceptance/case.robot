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

User can create a case workspace
    Given I am logged in as the user allan_neece
     Then I can create a new case    A case for outer space
      And I can delete a case  a-case-for-outer-space

User can create a template case workspace
    Given I am logged in as the user allan_neece
     Then I can create a new template case    New template
     Then I can create a new case from a template  New template  A new type of case
     Then I can delete a template case  new-template
     Then I can delete a case  a-new-type-of-case

Member can toggle the state of a task
    Given I am in a case workspace as a workspace member
     Then I can go to the Example Case
     Then I can go to the sidebar tasks tile of my case
     Then I can open a milestone task panel  prepare
     Then I select the task check box  Draft proposal
     Then I can go to the Example Case
     Then I can go to the sidebar tasks tile of my case
     # auto-closed, reopen
     Then I can open a milestone task panel  prepare
     Then I see a task is complete  Draft proposal
     Then I unselect the task check box  Draft proposal
     Then I can go to the Example Case
     Then I can go to the sidebar tasks tile of my case
     Then I can open a milestone task panel  prepare
     Then I see a task is open  Draft proposal

Manager can close a case milestone but only after closing open task
    Given I am logged in as the user allan_neece
      And I can create a new case  Workflow case
      And I can go to the sidebar tasks tile of my case
     Then I cannot close a milestone  new
     When I select the task check box  Populate Metadata
     Then I can close a milestone  new
      And I can delete a case  workflow-case

Manager can reopen a case milestone without closing open tasks
    Given I am logged in as the user allan_neece
      And I can create a new case  Workflow case
      And I can go to the sidebar tasks tile of my case
      And I can open a milestone task panel  new
      And I select the task check box  Populate Metadata
     When I can close a milestone  new
     Then I can reopen a milestone  new

Member cannot close a complete case milestone
    Given Admin moves the example workspace to state complete
      And I am in a case workspace as a workspace member
     Then I cannot close a milestone  complete

Member cannot edit content in a complete case milestone
    Given Admin moves the example workspace to state complete
      And I am in a case workspace as a workspace member
     Then I cannot create a new document

Member closing milestone sets planned task to open
   Given I am in a case workspace as a workspace member
     And I move the example workspace to state prepare
    Then I see the task Quality check has state  Planned
    When I can go to the sidebar tasks tile of my case
     And I can open a milestone task panel  prepare
     And I can close a milestone  prepare
    # switches to a protected state, veryify todo transition has worked
    Then I see the task Quality check has state  Open

Non-member cannot see into a workspace
    Given I am logged in as the user alice_lindstrom
     when I can go to the Example Case
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

Member can add a new task
    Given I am in a case workspace as a workspace member
     Then I can go to the sidebar tasks tile of my case
     Then I can add a new task  Make a plan  new

Member can close an unassigned task from the sidebar
    Given I am in a case workspace as a workspace member
     Then I can go to the sidebar tasks tile of my case
     Then I can add a new task  Unassigned task
     Then I select the task check box  Unassigned task
     Then I see a task is complete  Unassigned task

Member can mark a new task complete on dashboard
    Given I am in a case workspace as a workspace member
     Then I can go to the sidebar tasks tile of my case
     Then I can add a new task  Todo soon  prepare
     Then I go to the dashboard
     Then I select the task centric view
     Then I mark a new task complete
     Then I go to the dashboard
     Then I select the task centric view
     Then I do not see the completed task is not listed

## These tagging tests are intractable because the save confirmation
## message is set OK but not displayed - no indicator of injection complete
## is available that works for both tasks and documents/files/images
#
# Manager can tag a task
#     Given I am in a case workspace as a workspace admin
#     And I view the task
#     And I tag the item
#     And I view the task
#     Then the metadata has the new tag

# Member can tag a task with a tag suggestion
#     Given I am in a case workspace as a workspace admin
#     And I view the task
#     And I tag the item
#     And I clear the tag for an item
#     And I tag the item with a suggestion
#     Then the metadata has the new tag

The manager can invite Alice to join the Example Case
    Given I am in a case workspace as a workspace admin
     Then I can open the workspace member settings tab
      And I can invite Alice to join the workspace

The manager can invite Alice to join the Example Case from the menu
    Given I am in a case workspace as a workspace admin
      And I can open the workspace member settings tab
     Then I can invite Alice to join the workspace from the menu


*** Keywords ***

# See lib/keywords.robot in the section "case related keywords"
