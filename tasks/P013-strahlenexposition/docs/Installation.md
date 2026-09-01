# Datenanalyse Strahlenexposition

## Getting Started

### Prerequisites
- Python 3.10 or higher (and pip)
- installation of *Visual Studio Code* is recommended
- installation of VS Code extension *Database Client* is recommended

### Installation on Windows
1. Create a folder that will contain both the repository and the KI-Labor_strukturiert data folder.
2. Clone Repository or download and unzip source code
3. Open repository folder in VS Code
4. In VS Code open Terminal (CMD) and run following commands
    ```
    # Create virtual environment
    python -m venv venv

    # Activate it (CMD)
    .\venv\Scripts\activate

    # Install Poetry and dependencies from .lock file
    pip install poetry
    poetry install

    # Remove WeasyPrint (only on Windows)
    poetry remove weasyprint
    ```
5. weasyprint (used for pdf report generation) requires additional setup on Windows. This approach translates unix source code to windows binary and is also documented [here](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html). **Steps**:
    1. Download and install MSYS2 from [here](https://www.msys2.org/#installation)
    2. open MSYS2’s shell (search for "MSYS2 MINGW64" in your Start Menu) and install Pango by executing: 
        ```
        pacman -S mingw-w64-x86_64-pango
        ``` 
        Close the MSYS2 terminal.
    3. Open a new terminal in VS Code (Make sure your virtual environment is activated). Install weasyprint using pip.
        ```
        pip install --force-reinstall weasyprint==64.1
        ```
#### Common issues:
step 4:
- If the venv activation command raises ```windows running scripts is disabled on this system``` Open a power shell as administrator and run ```Set-ExecutionPolicy RemoteSigned```
- if you run the commands in a PowerShell instead CMD, activate the environment by running ```.\venv\Scripts\Activate.ps1```
- if ```python -m venv venv``` returns "python not found" try to run ```py -m venv venv```

### Run the application

#### Excel processing
To create the database and read/process the original excel files you can open the file pipeline.py (stored in src/strahlenexposition_uba/pipeline.py) and click run. A folder named *logs* should have been created with a log file. Check the log file for any errors and warnings when you process new data. 

#### Inspect the data 
Inspect database after excel files have been processed successfully:
1. open Database extension on the left sidebar
2. Click add connection
3. Select SQLite, type any name, and in Database Path field select the created database file (.db) in folder *database* which was created in the same folder where repository and data is stored.
4. Click save and connect. You can open data tables in the Tables section now. 

#### Create a report
To create a pdf report for selected years open terminal with activated Python environment and run e.g. for years 2018-2020
- in CMD terminal 
    ```
    python src\strahlenexposition_uba\pipeline.py --skip-read-original-excel --pdf-report-years 2018 2019 2020
    ```
- or if you are using PowerShell 
    ```
    python .\src\strahlenexposition_uba\pipeline.py --skip-read-original-excel --pdf-report-years 2018 2019 2020
    ```
This might take a minute. Created reports (both	pseudonymized and not pseudonymized) are saved to output folder. See next section for details how to provide pseudonyms.

#### Folder structure

The minimal folder structure in the base path is the following. Some of the folder names are unfortunately hardcoded within the code. If you change the folder structure, you need to make sure, that the code is adjusted accordingly. `<placeholder>` is used when precise folder names are not relevant.

```
KI-Labor_strukturiert/
├── 241216_R-Skripte_Vorlagen_U-Codes_und_Berichte/
│   └── 02-Untersuchungscodes_und_DRW.xlsx
└── 250122_Originalmeldungen/
    └── <all_data_one_folder_per_year>
```

#### Pseudonyms for pseudonymized report
To generate a report with pseudonymized "aerztliche_stelle", create a file "pseudonym_mapping.csv" somewhere inside the "KI-Labor_strukturiert" data directory. It must contain all aerztliche stellen formatted as
```
Aerztl_Stelle,pseudonym
name_aerztl_stelle,as_01
name_2_aerztl_stelle,as_02
```

then run the same command as above to create the report with pseudonymization applied.

#### Database info
The schema of the database (tables, columns) is defined in './sql/schema.sql'

When you run the pipeline to read excel file, it will only create a new database and new tables if no database file './database/raw_strahlenexposition.db' exists. An Excel sheet that have been successfully processed already (db entry in table 'eingelesene_dateien' with success=1) will not be processed again. Removed UCodes from Untersuchungscode excel will not automatically be removed from db table Untersuchungscodes if you run the pipeline again.
- if you manually changed data in the excel files and want to replace the existing data in the database, delete file './database/raw_strahlenexposition.db' and rerun pipeline.py
- if you want to exclude a specific UCode from reports you can remove the UCode from the Untersuchungscode excel file, delete the file './database/raw_strahlenexposition.db' and rerun the pipeline
- if you change database schema or processing logic in python code delete/rename './database/raw_strahlenexposition.db' and then run the pipeline

#### General information for running pipeline.py
- If there are any issues with acticated environment try to run ```.\venv\Scripts\python.exe .\src\strahlenexposition_uba\pipeline.py --pdf-report-years 2018 2019 2020``` instead.
- To see doc for all parameters and flags in pipeline.py run:
    ```
    python src\strahlenexposition_uba\pipeline.py --help
    ```

#### Start interactive Dash
- in CMD terminal 
    ```
    python src\strahlenexposition_uba\pipeline.py --skip-read-original-excel --start-dash
    ```
Click on url in terminal to open local dash app in browser.

#### Data Science and Heatmaps
For data science tasks and heatmap visualisation, the following arguments can (but don't have to) be applied:
- the years for which the data science shall be performed (if no years are provided, all data are used)
- the path to the base directory (if no path is provided, the grandparent folder is selected)
- the threshold for outlier detection, i.e. multiples of the DRW. e.g. --threshold 3 will mark all doses above 
3x DRW as outliers. 

For outlier analysis and clustering, run data_science.py. 
Example: 
```
python src/strahlenexposition_uba/data_science.py --years 2018 2019 2020 --path <path/where/kilaborstrukturiert/is/stored> --threshold 4
```

For data visualization as heatmaps, run heatmaps.py. Example:  
```
python src/strahlenexposition_uba/heatmaps.py --years 2018 2019 2020 --path <path/where/kilaborstrukturiert/is/stored> --threshold 4
```


## Install and run via python wheel (.whl)
A Wheel (.whl) is a standard built distribution format for Python packages. It lets you install Python software quickly without needing to compile anything.
### 1. Install the package
Open terminal and run:
```
pip install path/to/wheel/strahlenexposition_uba-1.0.0-py3-none-any.whl
```
**On windows**, you can ignore the warning about the kaleido version. Be sure to follow step 5 in  *Installation on Windows*:
- 5.1 and 5.2: Only if not done before
- 5.3: Mandatory (```pip install --force-reinstall weasyprint==64.1```)
### 2. Run the Application
You can now execute the pipeline to:
- Read Excel files
- Write to a database
- Generate reports

The application will create subfolders (database/, output/, logs/) inside your base path (=argument passed to --path parameter) if they don’t exist.



**Usage**

View available options
```
python -m strahlenexposition_uba --help
``` 
Example: Read Excel files and create PDF reports
```
python -m strahlenexposition_uba --pdf-report-years 2018 2019 2020 --path <path/where/kilaborstrukturiert/is/stored> 
```
You will find:
- Reports in: basepath/output/ (basepath=argument passed to --path parameter)
- Logs in: basepath/logs/


Example: Outlier analysis and clustering
```
python -m strahlenexposition_uba.data_science --years  2018 2019 2020 --path <path/where/kilaborstrukturiert/is/stored> --threshold 4
```

Example: Heatmaps
```
python -m strahlenexposition_uba.heatmaps --years  2018 2019 2020 --path <path/where/kilaborstrukturiert/is/stored> --threshold 4
```

## Setup for Development
This project uses ```poetry``` for Dependency management, virtual environments, building packages and publishing to PyPI, ```ruff``` for formatting and linting and ```sphinx``` for documentation. See pyproject.toml for details.

```
python3 -m venv venv
source venv/bin/activate
pip install poetry
poetry install
pre-commit install
```

Optional: Install Ruff extension in VSCode [https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff).

### SQLite Database
Optional: To explore the database tables you can use the *Database Client* extension in VSCode. To connect, select the database file located at */database/<db_name>.db*. If prompted, install SQLite on your system. Alternatively, you can use any other SQLite-compatible tool for database inspection.