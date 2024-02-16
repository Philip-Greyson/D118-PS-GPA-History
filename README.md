# D118-PS-GPA-History

Script to the GPAs of seniors for each semester they have been in high school, as well as their total "overall" GPA for their high school career.

## Overview

The script is pretty straightforward, it does an initial query for active 12th grade students, getting their ID number, internal ID, and name fields. Then the list of grades and term codes are iterated through in nested loops, starting with grade 9 semester 1 and progressing from there. The stored grades are used to calculate the adjusted point hours and those in turn to get the term GPA, and the totals are added into the running totals in order to calculate their overall high school GPA.
The general formula for the GPA is as follows:

 1. The class record's unadjusted GPA points (0-5 based on the grade) is added to the GPA added value (dependent on class, usually 0 or None) to get its adjusted GPA points.
 2. These adjusted points are multiplied by the earned credit hours for the class to get what I call `adjustedPointHours`
 3. Each class in the term's adjusted point hours are added together to get the `termAdjustedPointHours`. The potential credit hours for each class in the term are also added together to get the `termPotentialHours`.
 4. The term GPA is calculated by dividing the term adjusted point hours by the term potential hours.
 5. The term adjusted point hours and potential hours are added to the total adjusted point hours and total potential hours. The overall running GPA is calculated by dividing the total adjusted point hours by the total potential hours.

Each term is printed out to the output file with the term GPA and total GPA as of that term.

## Requirements

The following Environment Variables must be set on the machine running the script:

- POWERSCHOOL_READ_USER
- POWERSCHOOL_DB_PASSWORD
- POWERSCHOOL_PROD_DB

These are fairly self explanatory, and just relate to the usernames, passwords, and host IP/URLs for the PowerSchool server. If you wish to directly edit the script and include these credentials, you can.

Additionally, the following Python libraries must be installed on the host machine (links to the installation guide):

- [Python-oracledb](https://python-oracledb.readthedocs.io/en/latest/user_guide/installation.html)

## Customization

This is a pretty barebones script, and therefore there is not much major customization possible. That being said, here are a few things you could change:

- You will want to change the `SCHOOL_ID` constant to match the school code that the students you are working with got the grades stored in. This is probably not strictly necessary since the stored grades will only be for that student for the grades specified but I used it just as good practice.
- You can change the grade levels it searches through for stored grades by editing the `GRADE_LEVELS` constant list. If for example you only wanted the Freshman and Sophomore grades, you could edit it to be just `[9, 10]`.
- If there are other term codes, for instance if there are trimesters, quarters, etc instead of semesters, you will want to edit the `TERM_CODES` constant list to include the store codes found for those terms in the storedgrades table.
- If you wish to include other grade levels besides just seniors, or change the grade number, you want to edit the initial SQL query and change `... WHERE grade_level = 12 ...` to fit your needs.
- If you need to change the calculation for GPA, you will need to dig into the innermost loop
