# Imagelytics web application for image classification with visualization and reporting

The Imagelytics web application requires Windows Server to run and it consists of:
1) SQL Server database <code>[DBScripts](DBScripts)</code>.
2) ASP.NET web application <code>[WebApp](WebApp)</code>. 
3) <code>[ImageProcessor](ImageProcessor)</code> developed in Python.

## SQL Server database prerequisites
1) Create <code>Imagelytics</code> database.
2) Recreate tables using the following SQL script <code>[DBScripts/Imagelytics.sql](DBScripts/Imagelytics.sql)</code>.

## WebApp prerequisites
1) To modify and publish the web application you will need Visual Studio 2022.
2) Before deploying the application please adjust the setting in <code>[WebApp/WebApp/Web.config](WebApp/WebApp/Web.config)</code> file marked with !!!TODO.
3) After publishing the web application, create a writable <code>img</code> folder in the deployment root folder which will keep uploaded images. 

## Image Processor prerequisites
1) Set up a virtual environment for the project. 
2) Install project requirements listed in the <code>[ImageProcessor/requirements.txt](ImageProcessor/requirements.txt)</code> file.
3) Change database connection settings in <code>[ImageProcessor/settings.py](ImageProcessor/settings.py)</code>
4) Start image processor by running <code>[ImageProcessor/main.py](ImageProcessor/main.py)</code> script using Python. To automatically start the Image Processor use Windows' Task Scheduler.

## Adding new models
1) To add a new model you will need to place the appropriate .h5 and .json files into the <code>[ImageProcessor/models](ImageProcessor/models)</code> folder.
2) Register a new model by adding an appropriate entry into the <code>TrainedModels</code> database table.
