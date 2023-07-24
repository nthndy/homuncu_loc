// Batch Convert VSI to TIF ImageJ Macro (Saving TIFs in the same directory)

// Set the input directory path
inputDir = getDirectory("Choose the input directory");

// Process files in the input directory and its subdirectories
processFiles(inputDir);

// Function to process files recursively
function processFiles(dirPath) {
    list = getFileList(dirPath);
    for (i = 0; i < list.length; i++) {
        file = list[i];
        filePath = dirPath + file;
        if (endsWith(file, ".vsi")) {
            // Use Bio-Formats Importer with specified options
            run("Bio-Formats Importer", "open=[" + filePath + "] color_mode=Default rois_import=[ROI manager] view=Hyperstack stack_order=XYCZT use_virtual_stack");

            // Get the current image title (without extension)
            title = getTitle();
            extIndex = title.lastIndexOf(".");
            if (extIndex >= 0) {
                title = title.substring(0, extIndex);
            }

            // Check if the TIF file already exists
            tifFilePath = dirPath + title + ".tif";
            if (File.exists(tifFilePath)) {
                print("TIF file already exists: " + tifFilePath);
            } else {
                // Save the image as TIF in the same directory
                saveAs("Tiff", tifFilePath);
            }

            // Close the image to free memory
            close();
        } else if (File.isDirectory(filePath)) {
            // Recursively process subdirectories
            processFiles(filePath + "/");
        }
    }
}
