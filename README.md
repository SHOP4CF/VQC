### Requirements:
* Python 3.9 or newer

##### All experiments should be done within `virtual environment` to configure it:
1. Open **terminal** and run:  
 `python3 -m pip install --user virtualenv`
2. Using **terminal** go to the folder where you downloaded files from repository and run:
  `python3 -m venv <name_of_environment>`
3. Activate environment in the same folder, use command:
  `./<name_of_environment>/Scripts/activate` 
   or if using linux: `source ./<name_of_environment>/bin/activate`
4. Being in folder with the app. Install all dependencies with command:
  `pip install -r VQC/requirements.txt`
    Now you can read instruction below and try to perform some experiments safely.
5. After experiments, to leave virtual environment, simply type:  
  `deactivate`
To read more about installing creating virtual environment and installing packages in it go [here](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/).

## Folder description:
* `config` Folder with yaml config files
  * `configuration.yaml` file with methods and utils configuration
  * `db_config.yaml` file containing credentials for db access
  * `boxes.txt` - file generated by the app with coordinates of boxes to be checked by template matching method
* `documentation` - folders containing more extensive description of everything
* `FIWARE` - Scripts responsible for creating entities, subscriptions etc. and `docker-compose` file are enough to set up the application. FIWARE docker image can be downloaded from [here](https://hub.docker.com/r/fiware/orion)
* `img` - All needed images for testing inside it, we have 3 folders:
    * `template` - folder with some sample templates so that one can test it locally
    * `outcome` - folder where our methods will save outcomes
    * `control` - folder with sample photos of defected pcb our sender send paths to it for VQS
* `sender` - imitation of camera 
* `tests` Folder with all tests
* `TuningMethods` Folder keeping all the tuning methods and functions used by tests
* `VQC` - main component that will perform checking it contains methods and utils folder
    * `app` folder containing all scripts needed to run the application
        * `methods`, `utils`, `otherFunctions` - Folders containing respectively necessary methods, utils and some small miscellaneous functions that do not fit to utils/methods
    * `docker-compose.yaml` special docker file we can use it instead of docker run. This is beneficial if we have a lot of port binding network stuff etc.
    * `Dockerfile` File from which we create a Docker image of our application
    * `requirements.txt` All dependencies
* `pyproject.toml` - File needed for building wheel, and allowing tox to perform tests on multiple python versions. Inspired by [this tutorial](https://packaging.python.org/tutorials/packaging-projects/).
* `pytest.ini` - File that registers marks for tests
* `test_docker_os.py` - File used to test dockers with multiple base OS
* `VQC_setup.py` - A script allowing for the quick and easy setup of the application

**More information about each folder and its content can be found in appropriate markdown files in documentation.**

*If you don't want to use DockerImage or want to run tests/experiment with specific files you need to add VQC folder to your PYTHONPATH. On linux you can do it using*
`export PYTHONPATH=/data/app/VQC` 
*and on windows* 
`set PYTHONPATH=D:\VQC`

## To run  everything we need (Option 1)
### 1. run setup script
Run `python VQC_setup.py`, the script initialises necessary docker containers and allows for additional options which can be seen by running `VQC_setup.py help`

> **_NOTE:_** When running the script for the first time it is necessary to add `-cb`, as `c` creates entities and subscriptions, whereas `b` builds the containers

<br>

## To run  everything we need (Option 2)
### 1.	Set up FIWARE
Go to: https://hub.docker.com/r/fiware/orion-ld
Create and copy the docker-compose.yml

Run `docker-compose up -d` in the same directory 
Check if FIWARE and mongo is up and running with `docker ps`

Try to run: 
`localhost:1026/version`
In your web browser. FIWARE should respond on that. 

### 2.	Create entities and subscriptions for VQC

Go to VQC repository to: `App/FIWARE`
Run following commands:
```
python createEntities.py
python createSubscriptionsv1.py
```

These scripts should be executed with status 201. The entities and subscriptions should be created in FIWARE.


### 3.	Run VQC.
Go to `App/VQC`.
Run `docker-compose up` (to see the logs) or `docker-compose up -d` (to run it in background).

# Troubleshooting

### FIWARE response fails to establish connection:
#### 1. Ensure that the necessary docker containers is running

#### 2. Change configs
In some cases the created docker container for Fiware has a different URL than what is defined in the configs.
This can be fixed by replacing **fiware_host** variable in the `./config/configuration.yaml` with following alternatives:
- host.docker.internal (Windows/Mac)
- localhost (Windows)
- 172.17.0.1 (Linux)

### FIWARE response fails to update entity
#### 1. Run `python VQC_setup.py -c`
The `c` flag creates subscription and entities of fiware and therefore should take care of everything
#### 2. Manually create entities and subscriptions:
To manually crete entities and subscriptions, follow step 1 and 2 of a "**To run everything we need (Option 2)**" section

### No module named 'app'
When this problem occures it generally mean that the evironment variable `PYTHONPATH` hasn't been set.
to set a path variable:
#### Windows
  1. Go to System Properties > Environment Variables
2. If `PYTHONPATH` doesn't exist yet, click `New...` and name it `PYTHONPATH`
3. Edit `PYTHONPATH` and add a path to the VQC (for example: `C:\<path_to_project>\VQC`) at end of the Variable value 
4. Click ok and leave the properties, restart your terminal if you had it open, and it should be fixed

#### Linux
  1. Enter the repository and run ```export PYTHONPATH=`pwd` ```

## Testing the communication
For tests, we recommend using [Postman Application](https://www.postman.com/downloads/). For updates one should set the following configuration:
* `Method`: PATCH
* `URL`: http://localhost:1026/ngsi-ld/v1/entities/urn:ngsi-ld:Device:Bosch:camera1/attrs (or other proper to created Entity in FIWARE)
* `Headers`: <br>
  * `KEY`: Content-Type
  * `Value`: application/json

Finally, body section should contain:
```
{
    "pcb_path":{
        "value":"/imgs/control/02_01.png",
        "type":"Property"
    },
    "value":{
        "type": "Property",
        "value": "/imgs/template/02.png"
    }
}
```

Then you can send it. This should not produce any error and the VQC logs should produce information “GOT NOTIFICATION”.
In the `imgs/outcome` are stored the results of VQC.

## Performing tests with tox
make sure that you have tox installed in your virtual environment, and that the application is set up and running.

if `VQC_setup.py` was used, and no errors occured, both of those things should be assured.

Once done that go to `.\VQC` folder and type:`tox`

this should automatically launch tests for both python 3.9 and 3.10

if you are encountering the `ERROR: InterpreterNotFound: python3.9` or similar, ensure that you have the python installed and added to the system environment variables `PATH`

in case where dependencies were changed/updated, to apply the changes run `tox -r` to force recreation of the virtual environments. 
>_**NOTE:**_ it is not required to recreate virtual environments upon changing the code of the application

to run on specific python version, run `tox -e py39` for python 3.9 or `tox -e py310` for python 3.10