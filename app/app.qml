import QtQuick.Window
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import Qt.labs.folderlistmodel

Window {
    id: theWindow
    visible: true
    title: qsTr("Imagelytics")
    visibility: Window.AutomaticVisibility
    width:  980
    height: 700

    property int state: 0 // 0 - edit mode, 1 - processing, 2 - finished, 3 - cancelled

    property bool processing: qtApp.processing
    onProcessingChanged: {
        if(processing)
        {
            state = 1
            timerCheckProgress.start()
        }
    }

    property int processedImages: 0
    property string outputFile: ""
    property string processingError: ""

    function start_processing(model_name, output_file, project_name, project_desc)
    {
        var images = []
        for(var i=0; i<imagesModel.count; i++)
        {
            var el = imagesModel.get(i)
            images.push(el.elementUrl)
            el.elementProcessed = false
            imagesModel.set(i, el)
        }
        processingError = ""
        processedImages = 0
        outputFile = output_file
        qtApp.start_processing(model_name, images, output_file, project_name, project_desc)
    }

    Timer {
        id: timerCheckProgress
        interval: 100
        repeat: true
        onTriggered: {
            var processedImages = qtApp.get_processing_progress()
            for(var i=0; i<processedImages.length; i++)
            {
                var processedImage = processedImages[i]
                qtApp.log("Processed image: " + processedImage)
                for(var j=0; j<imagesModel.count; j++)
                {
                    var el = imagesModel.get(j)
                    if(el.elementUrl == processedImage && !el.elementProcessed)
                    {
                        el.elementProcessed = true
                        imagesModel.set(j, el)
                        theWindow.processedImages += 1
                        break
                    }
                }
            }

            if(!qtApp.processing)
            {
                stop()

                var cancelled = false
                for(var j=0; j<imagesModel.count; j++)
                {
                    var el = imagesModel.get(j)
                    if(!el.elementProcessed)
                    {
                        cancelled = true
                        break
                    }
                }

                if(cancelled)
                {
                    theWindow.state = 3 // cancelled
                    theWindow.processingError = qtApp.get_processing_error()
                }
                else
                {
                    theWindow.state = 2 // finished
                    theWindow.processingError = ""
                }
            }
        }
    }

    ListModel {
        id: imagesModel
    }

    GridLayout {
        id: gridLayout
        anchors.fill: parent
        anchors.margins: 15
        columns: 2
        columnSpacing: 15
        rowSpacing: 15
        Layout.fillWidth: false
        Layout.fillHeight: false

        Label {
            Layout.alignment: Qt.AlignRight
            text: qsTr("Title:")
        }

        TextField {
            id: textFieldProjectName
            placeholderText: qsTr("Enter project title")
            enabled: theWindow.state == 0 // edit
            selectByMouse: true
            Layout.fillWidth: true
        }

        Label {
            id: labelProjectDesc
            Layout.alignment: Qt.AlignRight
            text: qsTr("Description:")
        }

        TextField {
            id: textFieldProjectDesc
            placeholderText: qsTr("Enter project description (optional)")
            enabled: theWindow.state == 0 // edit
            selectByMouse: true
            Layout.fillWidth: true
        }

        Label {
            Layout.alignment: Qt.AlignRight
            text: qsTr("Model:")
        }

        ComboBox {
            id: comboBoxModel
            enabled: theWindow.state == 0 // edit
            Layout.fillWidth: true
            model: qtApp.get_models()
        }

        ColumnLayout {
            id: columnImages
            Layout.minimumWidth: labelProjectDesc.width
            Layout.alignment: Qt.AlignTop
            spacing: 15

            Label {
                id: labelImages
                Layout.alignment: Qt.AlignRight
                text: qsTr("Images:")
            }

            Button {
                enabled: theWindow.state == 0 && comboBoxModel.currentIndex >= 0
                Layout.alignment: Qt.AlignRight
                implicitWidth: labelProjectDesc.width
                implicitHeight: implicitWidth
                text: qsTr("Add")
                onClicked: {
                    fileDialogAddImages.open()
                }
            }

            Button {
                enabled: theWindow.state == 0 && comboBoxModel.currentIndex >= 0
                Layout.alignment: Qt.AlignRight
                implicitWidth: labelProjectDesc.width
                implicitHeight: implicitWidth
                text: qsTr("Clear")
                onClicked: {
                    imagesModel.clear()
                }
            }
        }

        GridView {
            id: imagesView
            Layout.fillWidth: true
            Layout.fillHeight: true
            model: imagesModel
            clip: true
            ScrollBar.vertical: ScrollBar {
                visible: true
            }
            cellHeight: 170
            cellWidth: 170
            delegate: Component {
                Item {
                    width: imagesView.cellWidth - 5
                    height: imagesView.cellWidth - 5
                    Rectangle {
                        anchors.fill: parent
                        anchors.margins: 5
                        color: imageItem.status == Image.Ready ? "black" : (imageItem.status == Image.Error ? "red" : "lightGray")
                        Image {
                            id: imageItem
                            anchors.fill: parent
                            sourceSize.width: 256
                            sourceSize.height: 256
                            source: elementUrl
                            fillMode: Image.PreserveAspectFit
                            asynchronous: true
                            cache: false
                        }
                        Rectangle {
                            visible: theWindow.state == 0 // edit
                            anchors.top: parent.top
                            anchors.right: parent.right
                            anchors.margins: -5
                            width: 30
                            height: width
                            radius: width / 2
                            border.color: "black"
                            border.width: 2
                            color: mouseAreaDelete.containsPress ? "darkRed" : "red"
                            Text {
                                anchors.centerIn: parent
                                text: "X"
                                color: "white"
                                font.bold: true
                                font.pixelSize: 17
                            }
                            MouseArea {
                                id: mouseAreaDelete
                                anchors.fill: parent
                                anchors.margins: 3
                                onClicked: {
                                    imagesModel.remove(index, 1)
                                }
                            }
                        }
                        Rectangle {
                            visible: theWindow.state != 0 // not edit
                            anchors.top: parent.top
                            anchors.right: parent.right
                            anchors.margins: -5
                            width: 30
                            height: width
                            radius: width / 2
                            border.color: "black"
                            border.width: 2
                            color: elementProcessed ? "#00FF00" : "#FFFF66"
                            Text {
                                anchors.centerIn: parent
                                anchors.verticalCenterOffset: elementProcessed ? 4 : 1
                                text: elementProcessed ? "ü" : "6"
                                color: "black"
                                font.family: "Wingdings"
                                font.bold: true
                                font.pixelSize: 26
                            }
                        }
                    }
                }
            }

            DropArea {
                id: imageDropArea
                anchors.fill: parent
                enabled: theWindow.state == 0 && comboBoxModel.currentIndex >= 0
                onEntered: {
                    drag.accept(Qt.LinkAction)
                }
                onDropped: {
                    //qtApp.log("imageDropArea.onDropped")
                    //qtApp.log(drop.urls)
                    qtApp.set_wait_cursor(true)
                    for(var i in drop.urls)
                    {
                        var url = drop.urls[i] + ''
                        imageUrls.push(url)
                    }
                    timerProcessUrls.restart()
                }

                property var imageUrls: []
                Timer {
                    id: timerProcessUrls
                    interval: 1
                    repeat: true
                    onTriggered: {
                        if(parent.imageUrls.length > 0)
                        {
                            var url = parent.imageUrls.shift()
                            if(url.startsWith('file:///'))
                            {
                                var ext = url.split('.').pop().toLowerCase()
                                if(ext == 'jpg' || ext == 'jpeg' || ext == 'png' || ext == 'tif' || ext == 'tiff')
                                {
                                    var found = false
                                    for(var j=0; j<imagesModel.count; j++)
                                    {
                                        if(imagesModel.get(j).elementUrl == url)
                                        {
                                            found = true
                                            break
                                        }
                                    }
                                    if(!found)
                                    {
                                        imagesModel.append({'elementUrl': url, 'elementProcessed': false})
                                    }
                                }
                            }
                        }
                        else
                        {
                            stop()
                            qtApp.set_wait_cursor(false)
                        }
                    }
                }
            }

            Item {
                anchors.fill: parent
                visible: theWindow.state == 3 && theWindow.processingError
                Rectangle {
                    anchors.fill: parent
                    opacity: 0.9
                    color: "white"
                }
                Text {
                    anchors.fill: parent
                    anchors.margins: 50
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    wrapMode: Text.WordWrap
                    color: "black"
                    text: theWindow.processingError
                    font.pixelSize: 26
                }
            }
        }

        Item {
            width: 1
        }

        RowLayout {
            id: buttonRow
            Layout.fillWidth: true
            spacing: 15

            Label {
                text: qsTr("Processed %1 of %2 images (%3%)").arg(theWindow.processedImages).arg(imagesModel.count).arg(Math.round(100 * theWindow.processedImages / imagesModel.count))
                visible: theWindow.state == 1 // processing
                Layout.minimumWidth: 200
            }

            Label {
                text: qsTr("Finished processing")
                visible: theWindow.state == 2 // finished
                Layout.minimumWidth: 200
            }

            Label {
                text: theWindow.processingError ? qsTr("Error processing images") : qsTr("Cancelled processing at %1%").arg(Math.round(100 * theWindow.processedImages / imagesModel.count))
                visible: theWindow.state == 3 // cancelled
                Layout.minimumWidth: 200
            }

            Button {
                Layout.minimumWidth: 200
                text: qsTr("Open report")
                visible: theWindow.state == 2 || theWindow.state == 3
                onClicked: {
                    qtApp.open_report(theWindow.outputFile)
                }
            }

            Button {
                Layout.fillWidth: true
                text: theWindow.state == 0 ? qsTr("Process images") : (theWindow.state == 1 ? qsTr("Cancel processing") : qsTr("Edit project"))
                enabled: theWindow.state != 0 || (imagesModel.count > 0 && textFieldProjectName.text)
                onClicked: {
                    if(theWindow.state == 0) // edit
                    {
                        fileDialogOutputFile.open()
                    }
                    else if(theWindow.state == 1) // processing
                    {
                        qtApp.cancel_processing()
                    }
                    else // finished or cancelled
                    {
                        theWindow.state = 0 // edit
                    }
                }
            }
        }
    }

    FileDialog {
        id: fileDialogAddImages
        title: qsTr("Select images to process")
        fileMode: FileDialog.OpenFiles
        onAccepted: {
            //qtApp.log("fileDialogAddImages.onAccepted")
            //qtApp.log(fileDialogAddImages.selectedFiles)
            qtApp.set_wait_cursor(true)
            for(var i in selectedFiles)
            {
                var url = selectedFiles[i] + ''
                imageDropArea.imageUrls.push(url)
            }
            timerProcessUrls.restart()
        }
    }

    FileDialog {
        id: fileDialogOutputFile
        title: qsTr("Select output file")
        fileMode: FileDialog.SaveFile
        currentFile: textFieldProjectName.text
        defaultSuffix: "html"
        nameFilters: ["HTML Files (*.html *.htm)", "All Files (*.*)"]
        onAccepted: {
            qtApp.log("fileDialogOutputFile.onAccepted")
            qtApp.log(fileDialogOutputFile.currentFile)
            theWindow.start_processing(comboBoxModel.currentText, fileDialogOutputFile.currentFile, textFieldProjectName.text, textFieldProjectDesc.text)
        }
    }
}
