# Imagelytics web application for image classification with visualization and reporting

The Imagelytics web application consists of ASP.NET web application:
1) SQL Server database that can be recreated using SQL script <code>[DBScripts/Imagelytics.sql](DBScripts/Imagelytics.sql)</code>.
2) ASP.NET web application <code>[WebApp](WebApp)</code>. To open the project and prepare executable version you will need Visual Studio 2022. Before deploying the application please adjust setting in <code>[WebApp/WebApp/Web.config](WebApp/WebApp/Web.config)</code> file.
3) Background <code>[ImageProcessor](ImageProcessor)</code> developed in Python.

## Prerequisites for Image Processor
1) Setup virtual environment for the project. 
2) Install project requirements listed in the <code>[ImageProcessor/requirements.txt](ImageProcessor/requirements.txt)</code> file.
3) Change database connection settings in <code>[ImageProcessor/settings.py](ImageProcessor/settings.py)</code>
4) Start image processor by running <code>[ImageProcessor/main.py](ImageProcessor/main.py)</code> script using Python. 

## Adding new models
1) To add a new model you will need to place the appropriate .h5 and .json files into the <code>[ImageProcessor/models](ImageProcessor/models)</code> folder.
2) Register new model by adding appropriate entry into TrainedModels database table.
