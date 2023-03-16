# Imagelytics: A standalone desktop application for image classification with visualization and reporting

## Prerequisites
1) Setup virtual environment for the project. 
2) Install project requirements listed in the <code>[requirements.txt](requirements.txt)</code> file.
3) To be able to build an installation package please install InnoSetup 6.2.1 or newer:</br>
https://jrsoftware.org/isinfo.php

## Adding new models
- To add a new model you will need to place the appropriate .h5 and .json files into the <code>[models](models)</code> folder.

## Instructions to build executable distribution
1) Delete previous <code>build</code> and <code>dist</code> folders.
2) To create a distribution open the terminal and activate <code>venv</code> if needed. Use the following command:<br/>
<code>venv\Scripts\activate.ps1</code>
3) Run the following command to make a distribution: <br/>
<code>pyinstaller main.spec</code>
4) The distribution can be found in <code>dist/main</code> folder. You may delete <code>build</code> folder since it no longer needed.

## Instructions to make installation package
1) Open <code>[setup.iss](setup.iss)</code> using InnoSetup 6.2.1 or newer.
2) Run the menu option <code>Build/Compile</code>.
3) The installation package will be created in the <code>dist/installation</code> folder.

## Testing the app
1) To test the build-in Chiro10-EfficientNetB2 model you may use images found in the <code>[../docs/chiro10-sample-images](../docs/chiro10-sample-images)</code> subfolder.
The appropriate test report <code>[../docs/chiro10-sample-report.html](../docs/chiro10-sample-report.html)</code> can be found in the <code>docs</code> folder. 
2) To test the built-in ImageNet-EfficientNetB2 model please download sample images from the following GitHub repository:<br/>
https://github.com/EliSchwartz/imagenet-sample-images
