# Imagelytics Suite: Deep Learning-Powered Image Classification for Bioassessment in Desktop and Web Environments

The Imagelytics Suite consists of the desktop and web applications, so as the training scripts used to produce models for these applications.

## Repository structure
The repository consists of four folders:
1) The <code>[app](app)</code> folder contains the source code for the Imagelytic desktop application. It is an independent project that should have a separate virtual environment. For more details please check <code>[app/README.md](app/README.md)</code>.
2) The <code>[webapp](webapp)</code> folder contains the source code for the Imagelytic web application. For more details please check <code>[webapp/README.md](webapp/README.md)</code>.
3) The <code>[train](train)</code> folder contains scripts that can be used to train and prepare metadata for a new model that can be used with both desktop and web applications. It is also an independent project that should have a separate virtual environment. For more details please check <code>[train/README.md](train/README.md)</code>.
4) The <code>[docs](docs)</code> folder contains additional files: 
   - <code>[docs/chiro10-sample-images](docs/chiro10-sample-images)</code> - sample images that can be used to test the applications using the built-in Chiro10-EfficientNetB2 model.
   - <code>[docs/chiro10-sample-report.html](docs/chiro10-sample-report.html)</code> - sample report created with the desktop application and appropriate Chiro10 sample images.
   - <code>[docs/images](docs/images)</code> - images of the UI for this document.

## Download and install the Imagelytics desktop application
The Imagelytics installation package for Windows is available for download in the repository release section:<br/>
https://github.com/a-milosavljevic/imagelytics/releases

## Processing images with Imagelytics desktop application
1) Open the application, enter the <code>Title</code> and optionally the <code>Description</code> of the project, and select the <code>Model</code> you want to use.
![imagelytics1.png](docs/images/imagelytics1.png)
![imagelytics2.png](docs/images/imagelytics2.png)
2) Add images by dragging and dropping them into the central area labeled as <code>Images</code>. Alternatively, add them using the <code>Add</code> button. 
![imagelytics3.png](docs/images/imagelytics3.png)
3) To begin processing please click the <code>Process images</code> button. 
4) After you select the location where the report will be saved, the processing will begin.
5) The processing is done in the background and it can take a significant amount of time. To track the progress, the number and percentage of processed images are shown. You may also request to cancel the process by clicking the <code>Cancel processing</code> button.
![imagelytics4.png](docs/images/imagelytics4.png)
6) Once the process finishes you may open the report by clicking the <code>Open report</code> button. The <code>Edit project</code> button will return the edit mode.
![imagelytics5.png](docs/images/imagelytics5.png)
![imagelytics6.png](docs/images/imagelytics6.png)

## Paper describing Imagelytics desktop application
Milosavljević, A., Predić, B., Milošević, D. (2023). Imagelytics: A Deep Learning-Based Image Classification Tool to Support Bioassessment. In: Jove, E., Zayas-Gato, F., Michelena, Á., Calvo-Rolle, J.L. (eds) Distributed Computing and Artificial Intelligence, Special Sessions II - Intelligent Systems Applications, 20th International Conference. DCAI 2023. Lecture Notes in Networks and Systems, vol 742. Springer, Cham. https://doi.org/10.1007/978-3-031-38616-9_5

## Acknowledgement
This research was supported by the [Science Fund of the Republic of Serbia](http://fondzanauku.gov.rs/?lang=en), #7751676, Application of deep learning in bioassessment of aquatic ecosystems: toward the construction of automatic identifier of aquatic macroinvertebrates - [AIAQUAMI](https://twitter.com/AIAQUAMI).
