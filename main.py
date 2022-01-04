# IMPORTING MODULES:
import numpy as np                
import random                     
import imageio                    
from datetime import datetime     
import matplotlib.pyplot as plt   
import matplotlib.image as mpimg  


# PART OF CACULATION OF PROGRAM DURATION:
start_time = datetime.now()    # determines time at start of program


# SETTING ARRAY DISPLAY OPTIONS:
np.set_printoptions(threshold=np.inf)
# full array elements will be printed without truncation
# (makes it easier to spot errors when testing code)


# CREATING ARRAY(S) FROM DATA FILE:
raw_height_data = open('DTM50.txt', 'r')    # opens DTM50 file in read mode
height_data = np.array([data.split() for data in raw_height_data.readlines()])
# list comprehension reads all lines from DTM50 file into a linear array
# whilst splitting data at all white spaces to separate data points
raw_height_data.close()     # closes file so other programs can run
height_array = height_data.reshape(200, 200)
# restructured version of height_data, now in a 200 x 200 numpy array
height_array2 = height_data.copy()
# a copy of the data used to ensure a square isn't flowed over twice.


# ARRAY FOR STORING FLOW PATTERN:
flow_pattern = np.zeros((200, 200))
# creates an np.array with each element starting as 0
# flow_pattern array has same dimensions to height_array (200 x 200)
# will be used to build and store the flow pattern


# ARRAY FOR STORING DEAD ENDS:
dead_end_map = np.zeros((200, 200))
# this dead_end_map will be an array used to store the location of points
# which do not return a lowest surrounding position.
# This is due to the point being a 'sink' or a 'loop'
# This is useful to understand where/why this happens


# MAKING A TITLE IN OUTPUT TERMINAL:
spacer, spacer2, spacer3 = ("="*70), ("\n " + "-" * 21), ("-" * 23 + "\n")
print("\n\n", spacer, spacer2, "DRAINAGE PATTERN ANALYSIS", spacer3, spacer)
# This is for user design


# PROGRAM EXPLANATION MESSAGE TO USER:
# lets user know what is about to happen and why it will not happen instantly
print("""\n\nThis program is designed to analyse elevation data from Scotland
The program will create a map which shows the flow pattern of rainfall
Four images will be saved to your files
A Fifth image will pop up, labelling the main geological features
(higher resolution maps will take slightly longer to produce)""")


# ERROR CATCHING FOR USER INPUT:
resolution = "not_given"        # variable set to "not_given" so while loop starts
# while loop so user has multiple chances to enter a valid input
while resolution == "not_given":
    resolution = str(input("\nhigh or medium resolution?  "))
    # user will input if they want high or low resolution
    # doesn't specify exactly what they should input as it's self-explanatory
    resolution = resolution.upper()
    # changes user input to upper case so easier to catch errors
    if "H" in resolution:       # any input with a 'h' or 'H' will be high res
        resolution = "high"     # saves result and breaks out of loop
        # this generously allows for any spelling errors that may be made
    elif "M" in resolution:     
        resolution = "medium"   # save result for use in next function
    else:                       # catches error as user put in a silly input
        resolution = "not_given"    # continues to loop around in while loop
        print("""                            ^ Invalid input:
                            (Please enter 'high' or 'medium')""")
        # arrow points to their input to emphasis their error
        # will loop around again to give user a chance to input what they want


# FUNCTION TO SPOT DEAD ENDS:
def dead_end_mapper(row, column):
    dead_end_map[row][column] += 1
    # adds one to the array in the position of the dead end
    # used in the lowest_adjoing function below


# FUNCTION TO FIND THE LOWEST SURROUNDING SQUARE:
# creating a user-defined function called lowest_adjoining
# the argument is the position of a height data point in the array
# function returns position of a surrounding square with the lowest height
# if lowest local selects an off-grid square (out of bounds), returns None
# if  all surrounding squares are higher, returns None
def lowest_adjoining(row, column):
    global height_array2    # making height_array2 a global variable
    # global variable so can access and edit data from outside the global frame
    local_height = height_array2[row, column]   # finds height at position
    North, East, South, West = row-1, column+1, row+1, column-1
    # creating variables represnting the new row or column number of a position
    # this is the position of a height found by travelling 50 metres N,E,S,or W
    # from a certain point in the hilly Scottish terrain being analysed

    if row == 0:            # These if and elif statements are to catch the
        North = 0           # special cases where the height data is positioned
    elif row == 199:        # on the top, bottom or side edges of the array.
        South = 199
    if column == 0:         # These if and elif statements will retain the row
        West = 0            # or column instead of setting it to an out of
    elif column == 199:     # bounds square, this catches off-grid squares
        East = 199          # and will later return None for them.

    # depending if the user chose a high or medium resolution flow pattern
    # surrounding is a list variable with each element being a list as well
    # in each list is a position, height at that position and compass direction
    # compass direction is only for debugging and code readability
    # if high resolutions, surrounding squares includes diagonals
    if resolution == "high":
        surrounding = [[[row, East], height_array2[row, East], 'E'],
                       [[South, column], height_array2[South, column], 'S'],
                       [[row, West], height_array2[row, West], 'W'],
                       [[North, column], height_array2[North, column], 'N'],
                       [[South, West], height_array2[South, West], 'SW'],
                       [[North, West], height_array2[North, West], 'NW'],
                       [[South, East], height_array2[South, East], 'SE'],
                       [[North, East], height_array2[North, East], 'NE']]

    # if medium res, surrounding squares include adjacent ones but not diagonal
    elif resolution == "medium":
        surrounding = [[[row, East], height_array2[row, East], 'E'],
                       [[South, column], height_array2[South, column], 'S'],
                       [[row, West], height_array2[row, West], 'W'],
                       [[North, column], height_array2[North, column], 'N']]

    lowest_surrounding = float(0)   # create variable and initially set to 0
    # variable holds the height difference between adjoining positions

    # loop around data for each adjoining square in the surrounding list
    # loops around data 3 times which takes time but avoids a RecursionError
    # maximum recursion depth (1000) exceeded if don't use all three loops
    for i in surrounding:                 # finding height difference
        # replaces height element with a float (difference in height)
        # height difference is positive if decrease in height
        i[1] = float(local_height) - float(i[1])

    for x in surrounding:   # loops around 'surrounding' list again
        # loops around data to find square with the greatest height difference
        # replaces the previous lowest if next square has greater height diff
        if x[1] >= lowest_surrounding:
            lowest_surrounding = x[1]   # data is compared to previous lowest

    lowest_list = []       # creating a list called lowest_list
    # lowest_list will store the position(s) of the lowest adjoining square

    for y in surrounding:   # loops around 'surrounding' list again
        if y[1] == lowest_surrounding:
            #           if the height difference saved at indexing
            #           position [1] is equal to the lowest_surrounding
            #           it means that water could flow to this square
            lowest_list += [y[0]]
            # position of square water could flow to added to lowest_list

    # if there is nothing in the lowest_list it means a point is a sink
    if len(lowest_list) == 0:       # check if point is a 'sink'
        height_array2 = height_array.copy()
        # resets height_array2 without + 1 over certain squares
        # uses dead_end_mapper function to add 1 to dead_end_array where
        # there are no lowest squares surrounding a tile
        dead_end_mapper(row, column)
        # returns None to code as all surrounding squares are higher
        return None

    # using randint from random module to select a random position from list
    # if only one position in list, then obviously that will be chosen
    # if there are 2+ surrounding squares with same lowest height:
    # computer will chose at random which path to take
    # (if you model the rainfall to split between each lowest option
    #  program could take up to 4X longer due to more recursion calls)
    selected_lowest = lowest_list[random.randint(0, len(lowest_list)-1)]
    # selected_lowest is the position that the rain is modelled to flow to
    height_array2[row, column] = (float(local_height) + 1)
    # add one to the height to ensure that path doesn't enter into a 'loop'

    # if position of selected_lowest is the same as the position as the point
    # it means that the computer has tried to select an off-grid square
    # this means flow has reached the end of it's viable path
    if selected_lowest[0] == row and selected_lowest[1] == column:
        height_array2 = height_array.copy()
        # resets height_array2 without + 1 over certain squares
        # uses dead_end_mapper function to add 1 to dead_end_array where
        # computer selects an off-grid or sunk square
        dead_end_mapper(row, column)
        return None    # returns None as nowhere for water to flow

    else:       # function returns the position of the lowest adjoining square
        return selected_lowest


# INFORMATIVE MESSAGE TO USER:
# lets user know that program is working but is likely to take some time
if resolution == "high":
    print("""\nAnalysing drainage pattern in high resolution
This will take around 30 seconds
Thank you for your patience\n
Progress creating your images: """)
# high resolution takes longer as 8 surrounding squares to call recursively
# medium resolution is quicker as only 4 adjoining squares to loop over
elif resolution == "medium":
    print("""\nAnalysing drainage pattern in medium resolution
This will take around 25 seconds
Thank you for your patience\n
Progress creating your images:""")


# FUNCTION LOCATING NEXT SQUARE:
# user-defined function which runs through all 40000 elements in height_array2
# the argument is the position of a height data point
# function returns the position of the next height data point
def next_square(row, column):
    next_row = row + 1                  # runs along rows before columns
    next_column = column                # data for same column, different row
    if row == 0 and column == 40:       # when 20% of program ran, column = 40
        print("20% complete")           # shows progress in output terminal
    elif row == 0 and column == 80:     # when 40% of program ran, column = 80
        print("40% complete")           # shows progress message in terminal
    elif row == 0 and column == 120:    # when 60% of program ran, column = 120
        print("60% complete")           # shows progress message in terminal
    elif row == 0 and column == 160:    # when 80% of program ran, column = 160
        print("80% complete")           # shows progress message in terminal
    elif row == 198 and column == 198:  # program almost ended (99.5% complete)
        # prints message to ignore 'Lossy conversion' warnings as not a problem
        print("100% complete\n\nYOU MAY IGNORE THESE WARNINGS:")
    if row == 199:                      # run through until reached end of row
        next_row = 0                    # starts from beginning of next row
        next_column += 1                # next row is one column along
    if column == 199 and row == 199:    # code has run through every data point
        return None, None               # returns None, None as no more data
    return next_row, next_column        # returns position of next square


# FUNCTION TO ADD TO FLOW PATTERN ARRAY:
# user defined function simulates rain being dropped evenly over entire area
# think of this as a single rain droplet flowing from one square to the next
# At each of the starting positions, 1 is added to the flow_pattern array
# function calls recursively to next square using lowest_adjoining
def rain_droplet(row, column):       # argument is the position of a data point
    flow_pattern[row, column] += 1   # adds 1 where raindrop starts an flows to
    flows_to = lowest_adjoining(row, column)    # next square in flow pattern
    if flows_to:    # if there is a next square in the flow pattern the rain
        #             droplet will flow there, calling recursively to next
        #             square which has the position (flows_to[0], flows_to[1])
        rain_droplet(flows_to[0], flows_to[1])
    else:               # if lowest_adjoining returns None, it will stop flow
        return None     # return None as nowhere left for rain droplet to flow


# FUNCTION TO TRACK RAIN FLOW PATTERNS:
# This function does not have an argument and does not return any variables
# This function takes the rain droplet and tracks its movement to the edge
# Then the function calls to the next data point to track a different droplet
def all_flow_patterns():
    row, column = 0, 0  # starting position is top corner of array
    # program ends if row is None as no more squares left to call
    while row is not None:
        rain_droplet(row, column)
        # calls rain_droplet function at certain position, finding next place
        # that rain droplet will flow to, adding 1 to the flow_pattern array
        # on every square where the rain droplet flows over, ends when reaches
        # an off-grid position as flow pattern for a specific raindrop finished
        # print('COMPLETED: ', row, column)           # for debugging purposes
        row, column = next_square(row, column)
        # when the flow pattern for one specific rain drop has finished (as it
        # has reached an off-grid position), another raindrop is placed in the
        # next square, and then the simulated path of this droplet is tracked
        # 1 added to the flow_pattern array on squares the droplet flows over
        # This function doesn't return anything so no need for return statement


# VECTORISING FLOW_PATTERNS:
all_flow_patterns()     # runs code by calling the all_flow_patterns function

high_contrast = (30.35)*(np.log(flow_pattern))
# high_contrast produces a clear image outlining tributaries
# and rives which lead into a lake

dark_mode = 3.84*(np.sqrt(flow_pattern))
# produces images where areas of particularly high flow are much lighter

light_mode = 255 - ((3.84)*(np.sqrt(flow_pattern)))
# produces opposite of dark_mode where areas of high flow shows as black

dead_end_pattern = (30.35)*(np.log(dead_end_map + 1))
# if don't use logs, the dead_end_pattern doesn't show up the lake
# all points of interest show up using this equation to vectorise


# CREATING IMAGE FILES USING IMAGEIO:
# using imwrite function from imageio module to write image files from the
# arrays, each 200 x 200 pixels ranging from 0-255 (255 = white, 0 = black)
# can ignore lossy conversion warning in output terminal due to floats
imageio.imwrite("dark_mode_flow_pattern.png", dark_mode)
imageio.imwrite("light_mode_flow_pattern.png", light_mode)
imageio.imwrite("high_contrast_flow_pattern.png", high_contrast)

imageio.imwrite("dead_end_pattern.png", dead_end_pattern)
# This dead_end _pattern produces an interesting image, of points where the
# water can no longer flow anywhere else. This is expected due to data being
# actual elevation data - puddles or lakes or eddies would occur in practice
# at these points this could be because a group of heights form a loop or sink
# so the program stops.


# CALCULATING RUN-TIME DURATION:
endtime = datetime.now()
# use datetime module to find time at instant program has ended
# message to user to notify that files have been saves and the time taken
print("""\nImages have been successfully saved to your files
Program duration:{}\n\n""".format(endtime - start_time))


# CREATING IMAGE GRAPH WITH LABELS
# using matplotlib module (mpimg and pyplot) to read an image into a graph
image_to_graph = mpimg.imread('high_contrast_flow_pattern.png')
# creates set of datapoints from image that graph will plot
imgplot = plt.imshow(image_to_graph)
# adding title and label features to map to make sense to user
plt.title("Features of the Scottish Terrain")
plt.text(153, 148, "LAKE", fontsize='14', weight='bold')
plt.text(30, 145, "RIVER", fontsize='12', weight='bold')
plt.text(99, 30, "TRIBUTARIES", fontsize='9', weight='bold')
plt.show()  # shows map, so pops up for user to view