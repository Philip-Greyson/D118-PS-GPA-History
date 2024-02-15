"""Script to get the GPA for each semester of our seniors.

https://github.com/Philip-Greyson/D118-PS-GPA-History

needs oracledb: pip install oracledb --upgrade

See the following for PS table information:
https://ps.powerschool-docs.com/pssis-data-dictionary/latest/storedgrades-31-ver3-6-1
"""

# import modules
import datetime
import os
from datetime import *

import oracledb

DB_UN = os.environ.get('POWERSCHOOL_READ_USER')  # username for read-only database user
DB_PW = os.environ.get('POWERSCHOOL_DB_PASSWORD')  # the password for the database account
DB_CS = os.environ.get('POWERSCHOOL_PROD_DB')  # the IP address, port, and database name to connect to

print(f"Username: {DB_UN} | Password: {DB_PW} | Server: {DB_CS}")  # debug so we can see where oracle is trying to connect to/with

GRADE_LEVELS = [9, 10, 11, 12]
TERM_CODES = ['S1', 'S2']
SCHOOL_ID = 5

if __name__ == '__main__':  # main file execution
    with open('gpa_log.txt', 'w') as log:  # open logging file
        with open('gpa_summary.csv', 'w') as output:
            startTime = datetime.now()
            todaysDate = datetime.now()
            startTime = startTime.strftime('%H:%M:%S')
            print(f'INFO: Execution started at {startTime}')
            print(f'INFO: Execution started at {startTime}', file=log)
            print('Student Number,Student Name,Grade Level,Semester,Term GPA,Total GPA', file=output)
            # formula: sum( gpa_points * gpa_potentialCredit ) / sum( gpa_potentialCredit )
            with oracledb.connect(user=DB_UN, password=DB_PW, dsn=DB_CS) as con:  # create the connecton to the database
                try:
                    with con.cursor() as cur:  # start an entry cursor
                        cur.execute('SELECT student_number, id, first_name, last_name FROM students WHERE grade_level = 12 AND enroll_status = 0')
                        students = cur.fetchall()
                        for student in students:
                            try:
                                stuNum = str(int(student[0]))
                                id = student[1]
                                stuFirst = str(student[2])
                                stuLast = str(student[3])
                                totalGPA = None  # reset running GPA for new student
                                totalAdjustedPointHours = None  # reset running GPA points for each student
                                totalPotentialHours = None  # reset running potential hours for each student
                                for grade in GRADE_LEVELS:  # go through each year of high school
                                    for code in TERM_CODES:  # go through each semester code
                                        # do the query for the stored grades for the current semester in the current grade of the current student
                                        cur.execute("SELECT gpa_points, gpa_addedvalue, earnedCrHrs, potentialCrHrs, grade_level, storecode FROM storedgrades WHERE studentid = :student AND grade_level = :grade AND NOT excludefromgpa = 1 AND schoolid = :school AND storecode = :code", student = id, grade = grade, school = SCHOOL_ID, code = code)
                                        grades = cur.fetchall()
                                        termAdjustedPointHours = 0  # reset term values for new term
                                        termPotentialHours = 0  # reset term values for new term
                                        termGPA = 0  # reset term values for new term
                                        if grades:  # some semesters may not have any data in them
                                            for storedGrade in grades:
                                                # print(grade)
                                                unadjustedGPAPoints = storedGrade[0]
                                                adjustmentPoints = storedGrade[1] if storedGrade[1] else 0  # most of the values are none, in which case just take a 0
                                                earnedHours = storedGrade[2]
                                                potentialHours = storedGrade[3]
                                                gradeLevel = int(storedGrade[4])
                                                semester = str(storedGrade[5])
                                                # start the actual calculation
                                                adjustedPoints = unadjustedGPAPoints + adjustmentPoints  # add any adjustments onto the raw points to get the adjusted points
                                                adjustedPointHours = adjustedPoints * earnedHours  # mutliply adjusted points by the earned credit hours to get the adjusted point hours value
                                                termAdjustedPointHours += adjustedPointHours  # the running total of the term point hours gets the current stored grades values added to it
                                                termPotentialHours += potentialHours  # the running total of the term potential hours gets the current stored grade potential hour value added to it
                                            termGPA = termAdjustedPointHours / termPotentialHours  # calculate this term's GPA by dividing the term point hours by the potential hours
                                            # add this term's values to the overall high school total for the student
                                            totalAdjustedPointHours = termAdjustedPointHours if not totalAdjustedPointHours else (totalAdjustedPointHours + termAdjustedPointHours)  # if the current total is None (first semester), the term is the total, otherwise add the old total with this term to get the new total
                                            totalPotentialHours = termPotentialHours if not totalPotentialHours else (totalPotentialHours + termPotentialHours)  # if the current total is None (first semester), the term is the total, otherwise add the old total with this term to get the new total
                                            totalGPA = totalAdjustedPointHours / totalPotentialHours  # calculate their overall high school GPA by dividing total adjusted point hours by the total potential hours
                                            print(f'{stuNum},"{stuLast}, {stuFirst}",{grade},{semester},{termAdjustedPointHours},{termPotentialHours},{termGPA:5.3f},{totalAdjustedPointHours},{totalPotentialHours},{totalGPA:5.3f}', file=log)  # uses the :5.3f to force a total length of 5 (padding zeros on end) and 3 decimal places for the float output
                                            print(f'{stuNum},"{stuLast}, {stuFirst}",{grade},{semester},{termGPA:5.3f},{totalGPA:5.3f}', file=output)

                            except Exception as er:
                                print(f'ERROR on {student[0]}: {er}')
                                print(f'ERROR on {student[0]}: {er}', file=log)

                except Exception as er:
                    print(f'ERROR while doing initial PowerSchool query or file handling: {er}')
                    print(f'ERROR while doing initial PowerSchool query or file handling: {er}', file=log)
