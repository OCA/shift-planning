After configuring the application we can start making plannings. To create a new one:

1. Go to *Shifts > Plannings* and click on *Create*.
2. Set the year and week number for the planning and click *Save*.
3. Now click on *Generate* to pre-create the shifts assignments for your employees.

You can start assigning shifts click on the *Shifts* smart button where you'll go to
a kanban view with a card per employee that you can drag into the corresponding shift.
Once you do it, you'll the color of the week days in the card changes to the color of
the shift assigned.

![Drag to assign](../static/description/assignment_dragging.gif)

Now if you want to assign a different shift for a specific day of that week to that
employee, you can do so clicking on *__Shift details__*. In the detailed kanban view
drag the days to their corresponding shifts.

![Changing specific days](../static/description/assignment_details_dragging.gif)

Going back to the general assignment screen you'll see the difference in the days list
colors for the employee's card. Every day is clickable and it will pop up the shift
details for that specific day.

![Card with different shifts](../static/description/week_days_colors.png)

## Detecting employees issues

An employee could be on leave for one or serveral days of a planning week. In that case
when an assignment is made for that employee the overlapping days will be flagged as
unavailable and no shift will be assigned.

We can detect those issues from the general plannings view in *Shift > Plannings*.

![Mark as reviewed](../static/description/planning_card.png)

To set the issue as reviewed we can click on the checkbox of the employee's assignment
card. It won't be counted on the issues summary when is checked.

![Mark as reviewed](../static/description/reviewed_checkbox.png)

## Generate planning from another one

We can generate plannings from other planning so we can copy the shifts assigments. To
do so you can either click on *__Generate planning__* from the general plannings view in
*Shifts > Plannings* or click on *__Copy to new planning__* from the origin planning
form.

In both cases a wizard will open where you can choose to which week will the new
planning correspond to and from which planning we'll be copying the assignations.

## Regenerate shifts.

We can reset the assignments from the planning form clicking on *Regenerate shifts*.

## My shifts

All the internal users can view their assigned shifts going to *Shifts > My shifts*.
