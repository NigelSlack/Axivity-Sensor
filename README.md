# Wearable sensors
Tool to analyse and label sensor output files

This code has seven basic functions : 

  1. Label records in csv or xlsx files. The first variable in each record must be a timestamp, and there must be at least one other numeric variable.
     A plot is displayed of the time against selected numeric value(s). The user selects portions of the plot, and assigns a label to each portion. 
     An output file is produced containing the selected columns and time periods, with each record having the appropriate label appended to it. 
     The labels are chosen from a list held in the file sensorcodeConfigFile.txt in the same folder as the code.  
     Labels can be added or deleted. If the labels are changed the sensorcodeConfigFile.txt is updated, and the user can also create a copy of the 
     program code containing the new labels. If the config file is deleted, or the code run elsewhere, the new labels will be output to the new config
     file.  
       
     Time periods for which the user allocates the label 'Other' are excluded from the output file.    
     If the user selects any 'Other' labels, the timestamps of subsequent periods are adjusted to run immediately consecutive to the period preceding 
     that for 'Other'. The timestamps will no longer be the actual timestamps, but this does not affect using the output files for training models, and
     using the trained models for making predictions.  
       
     The user can specify which columns to include in the output file.    
     For example, an input file record might contain - 2022/04/15 12.36.10  -0.963  0.72  0.23  54    
       - a timestamp with accelerometer x,y and z values and a heartrate  
       If the user just wants the accelerometer data, plus timestamps and labels in the output file, they can select columns 0 to 3, and perhaps add a 
       human activity label to the time period containing this record of 'Walk'. The corresponding record in the output file will then be - 
       2022/04/15 12.36.10  -0.963  0.72  0.23  Walk  
  
     If there are multiple records per second in the input file, the user can select the proportion to keep (with records in the input file randomly 
     selected) for  inclusion in the output file. eg if there are 200 records per second in the input file the user might decide to keep an average of 
     10 per second in the output file.  
  
     Scaling can be applied to numeric values in the input file, either to the data itself, or just for the plot. For example, in the record above if 
     the last value  (heartrate) is included in the plot then the 3 accelorometer values will be squashed together at the bottom of the plot, with a big 
     gap separating them and the heartrate. If the output file is to be used to build predictive models (for future unlabelled data) the user may wish to 
     experiment with using scaled or unscaled data to see which results in the best predictions.   
     The user can opt for both scaled and unscaled outputs - it may be useful for comparing model predictions with scaled/unscaled inputs.  
       
     The user can add a 'root mean squared' value to the output file, ie the square root of the sum of the squares of selected variables.  
       
     The file type of the output file is set to the same as for the input file, eg if the input file is a csv file, then the output file will also be csv.  
     A summary file is also produced, with '-sum' appended to the output data file name, showing the mean and standard deviation of each of the numeric 
     variables, for each distinct period with respect to the labels applied. For example, if the labels 'Walk' and 'Sit' were chosen for the first 15 minutes 
     and the second 15 minutes respectively, then the mean values (and standard deviations) are shown for numeric values over these two periods.  
     A subjectid (eg person's name or initials) and a sensor location (eg left wrist or waist) can be included in the summary records.        
  
  2. Combine csv/xlsx files. The user selects files to combine, and each one is appended to the output file. As for option one, the user can select specific
     columns (variables) to include, can scale values, and can specify a proportion of input records to include in the output file. After the first file has 
     been added to the output file, the the timestamp value for subsequent files is adjusted to follow on from the last record of the previous file, at a second
     or minute level, depending on the gradation present in the first file - if the timestamps in the first file are at second level, timestamps for subsequent 
     files will start at a value one second after the last timestamp of the previous file. If they are at a minute level, one minute will be added to the last
     record to give the timestamp of the first record of the next file.      
     Input files do not need to contain the same number of columns (variables), so, for example, a file containing a timestamp and heartrate variable could be 
     appended to one cotaining a timestamp and 3 accelerometer variables. The file type of the first file determines the type of the output file, eg if the first 
     file specified is an xlsx file, then the output file will be too, although input files do not need to be of the same file type.  
  
  3. Pre-process a file containing (numerical) physiological data. A specific column containing the target data must be selected by the user. The code determines
     the mean of the values in the selected column on a minute by minute basis (M), by blocks of numbers of seconds (S), or by blocks of data containing a specified 
     number of records (B). If the difference in the mean value for a given block of size M/S/B, and the mean value for the block M/S/B preceeding it by two blocks
     of size M/S/B is greater than a specific percentage (chosen by the user), then the values for the block of M/S/B immediately before the current block of M/S/B
     are set to the same as for the current block.   
     The purpose of this is to attempt to improve the accuracy of models built using this data, that predict eg human activity.  
     For example, suppose a user wears two sensors, an accelerometer and a heart rate sensor. They switch between activities, eg sitting, walking, running etc and 
     the readings from the sensors are used to try to predict their activity types.  
     When changing activity the accelerometer readings will change in a fraction of a second, but the heartrate may take eg about 30 seconds to adjust. A machine 
     learning model is more likely to make accurate predictions if the heartrate transition is presented as more of a step change than a gradual change.    
  
  4. Merge two files. Data from the records of one file are appended to the records of another file (unlike for 'combine' where the data are appended to the end 
     of the file).  
     For example, if the first file contained 2022/04/15 12.36.10  -0.963  0.72  0.23   and the second contained  2022/04/15 12.36.01  67  (from an accelerometer 
     and a heartrate monitor), then the output record could contain   2022/04/15 12.36.10  -0.963  0.72  0.23  67  
     The file with the higher frequency is treated as the primary file - the timestamps will be taken from this file, and the selected columns from it will come
     first. If both files have the same frequency then the first file specified is used as the primary file. Where frequencies differ, values from the file with 
     lower frequency are repeated for an appropriate number of records. For example, if the first file contains 10 records per second, and the second has 5 per 
     minute, then the values from one record of the second file will be appended to 120 records of the first file (as the frequency of the first file is 120 times
     that of the second). This is calculated on a minute by minute basis. If the frequency of the second file exceeds that of the first file for a given minute a 
     warning is output, and excess records from the second file are discarded.  
     A plot is produced of the primary file, and the user selects the start and end times of the data to process.  
     If the timestamps of the two files are synchronised those of the primary file are used as a driver. If they are not synchronised a plot is also displayed of 
     the secondary file and the user selects the start time only for this file. The records from each file are then processed from these two start times on a minute
     by minute basis. Clearly in this case it is important to choose the correct start time for the secondary file to obtain a valid merge of the data.       
     Specific columns, scaling and the proportion of records to keep can be selected by the user for each file, as for other functions.       
  
   5. Display a histogram of selected data. Required elements of the input file are plotted on one histogram. If input values have different 
      magnitudes, eg if they include heartrate and accelerometer readings, scaling will be required to produce a meaningful plot. The creation 
      of a GaussianNB machine learning model assumes input data have approximately Normal distribution; a histogram plot of the data can be used 
      to determine if this is the case. The user specifies the number of bins to use.        
      
   6, 7 and 8. Create predictive models from labelled data. kMeans, Machine learning and Neural Network models can be created using labelled input data files. 
     The user specifies the column containing the category that the model may be used to predict, and as for other options the user can choose specific columns, 
     scaling and the proportion of records to keep from the input file. An additional file is created along with the model showing the categories used to create
     the model, and a sample data record.  
     For Machine Learning, five different models are created. The estimated accuracy of each model is determined using test data, and displayed to the user.  
       
   9, 10, 11. Run a predictive kMeans, Machine Learning or Neural network model to generate labels for an input file (using the categories contained in the data
     file from which the model was created). For example, if a model is created using data from a file generated by sensors monitoring human activity, and the 
     activities performed during data collection were 'Walk', 'Run', 'Sit', then it is only appropriate to run this model against input data collected during these
     activities if the purpose is to attempt to predict the label associated with the data. The code will expect the model to have an accompanying file showing the 
     categories used in its creation, and a sample record (as created by options 5, 6 and 7). An output file is produced with the predicted labels appended to each 
     input data record.   
     For example, if  2022/04/15 12.36.10  -0.963  0.72  0.23  67  is the input data record, then  2022/04/15 12.36.10  -0.963  0.72  0.23  67  Walk   might be the
     output record, where 'Walk' is the label predicted by the model.    
     The output file type will be the same as the input file type.       
  
  
Requirements : Python, plus required libraries   
               The code will attempt to install any required libraries that are not already installed at runtime. If it fails to do so a message is output and the 
               run terminates. Where a library is required for a specific function it will only be loaded for that function.                 
  
To run :  
  python labelData.py  
    
Input and output files and folders are selected by the user from a separate Explorer window.    
All input file records are required to have a timestamp as their first variable (in their first column).  
  
If an input file has potentially ambiguous month and day values (if none of the day values in the data exceed '12'), then the user may swap round the month and day
values - this will be required if the plot of the data is clearly wrong, with values strongly clumped together on the time axis when the user would expect them to be 
evenly distributed. The code  takes a random sample of 20 timestamps from the file to determine if this may be the case, and if no values greater than 12 are detected
in the month/day fields it asks the user if they wish to switch the two.  
  
The Axivity AX3 accelerometer :  
  
This code was originally developed for labelling data from this sensor.  
This is a wearable sensor that measures acceleration values in 3 orthogonal directions - x, y and z.  
Configuration of the sensor is performed using the 'Open Movement' (OM) software package that accompanies it, via a USB or wireless connection to a computer.  
Recording of data is started using OM, activities are undertaken by a user, then recording is stopped in OM.  
A compressed data file of type 'cwa' is generated by the sensor, with each record containing a timestamp, acceleration readings in the x, y and z directions,
and temperature readings.  
The x, y and z directions will depend on the orientation of the sensor during the time it is recording.  
OM has a facility for exporting the resultant 'cwa' files to other file types, such as csv files.  
   
This code processes exported files (from OM) of type 'raw csv', with datetime format Y-M-D h:m:s.f, and Accelerometer Units Gravity(g).   

The sensor can record between 12.5 and 500 readings per second (Hz), but the OM software warns that it may not process signals correctly if the rate
is set below 50Hz. It is probably best therefore to use this as a minimum frequency value when configuring the sensor. However, this number of readings
may not be required to determine label type, eg 10 or 20 readings per second may be sufficient to distinguish between different activities.  
  
Means of classifying data - most common techniques - KNN, kmeans and sub-clustering. From review paper -  
https://www.researchgate.net/publication/341303680_Unsupervised_Human_Activity_Recognition_Using_the_Clustering_Approach_A_Review  

