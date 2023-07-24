# _homunculoc_: single-cell segmentation and tracking for the Lung-on-a-Chip project

![temp logo: Immunofluorescence staining of the apical iLoC on AX Lung-on-chip memebrane after iLoC assembly; DAPI (cyan), mature SP-C (magenta), PDPN (yellow) and ZO-1 (red).](loc_landing.gif)

Welcome to the _*homunculoc*_ project repository. This project aims to study host-pathogen interactions using a Lung-on-a-Chip platform at the Francis Crick Institute in collaboration with Alveolix. The repository provides tools for single-cell segmentation and tracking of lung-on-a-chip samples, enabling quantification of cell type and behavior. This README will guide you through the project and its components.

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
- [Dependencies](#dependencies)
- [License](#license)
- [Contributing](#contributing)
- [Contact](#contact)

## Introduction

The Lung-on-a-Chip project aims to replicate and study the complex interactions between host cells and pathogens in a controlled microfluidic environment. This repository contains code and resources to perform single-cell segmentation and tracking, facilitating the analysis and quantification of cellular behavior within the lung-on-a-chip system.

The repository is currently split into two major parts: labelling and quantification. The labelling section contains a notebook(s) to segment and track cells over 3 dimensions whilst the quantification section uses the previously generated tracks to quantify cell type and behaviour. Each section contains an archive (`arx`) that contains the previously created work-in-progress code that went into forming the final polished notebooks.

## Installation

To install and set up the project, please follow these steps:

1. Clone the repository to your local machine:

`git clone https://github.com/your-username/homuncu_loc.git`

2. Install the required dependencies listed in the [Dependencies](#dependencies) section or install the provided conda environment `environment.yml`:

``cd homonucu_loc  
conda env create -f environment.yml  
conda activate loc  
``

This environment has been tested on `x86_64` `macos>=11` and `ubuntu>=20.04`.

3. Install the native modules and check if all other dependencies are met:

``pip install -e .``

Every necessary component should now be installed.

## Usage

To use the Lung-on-a-Chip project, follow these guidelines:

1. Open the project directory and navigate to the relevant Jupyter Notebook(s).
2. Launch Jupyter Notebook: `jupyter notebook`


3. Execute the notebooks sequentially, following the instructions and guidelines provided within them.
4. Customize and modify the code as needed to adapt to your specific experiments and requirements.

Please note that the repository is organized into directories based on different aspects of the project, such as data preprocessing, analysis, and visualization. Explore the directories and choose the relevant notebooks for your needs.

## Dependencies

The Lung-on-a-Chip project relies on the following dependencies:

- Python (version 3.9.12)
- btrack (version 0.6.3)
- Other Python packages listed in the `environment.yml` file

Ensure that these dependencies are installed and configured correctly before running the project.

## License

This project is licensed under the **Private License**. For more information, please see the [LICENSE](LICENSE.md) file.

## Contributing

We welcome contributions to the Lung-on-a-Chip project! If you find any issues, have suggestions for improvements, or would like to add new features, please feel free to submit a pull request or open an issue. We appreciate your contributions.

## Contact

For any inquiries or further information about the project, please contact:

- Project Lead: [Jakson Luk](mailto:jakson.luk@crick.ac.uk)
- Image Analyst/Software: [Nathan Day](mailto:nathan.day@crick.ac.uk)
- Laboratory Research Scientist/Legal Specialist with a focus on copyright law: [Gabriel Conway](mailto:gabriel.conway@crick.ac.uk)
- Francis Crick Institute: [Website](https://www.crick.ac.uk)
- Alveolix: [Website](https://www.alveolix.com)

---
