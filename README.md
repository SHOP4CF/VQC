# Visual Quality Check (VQC)
This is repository of VQC. This component was created within SHOP4CF project. The main goal is to perform visual inspection for quality control using standard image processing methods.

# Fast start (recommended)

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

### 4.	Test the communication

Run postman and create the following configuration:
```
KEY: Contetnt-Type
VALUE: application/json
```
And Json (you can also find it in FIWARE/m.json)

```
{
    "pcb_path":{
        "value":"/imgs/control/01_01.png",
        "type":"Property"
    },
    "value":{
        "type": "Property",
        "value": "/imgs/template/01.png"
    }
}
```


Then you can send it. This should not produce any error and the VQC logs should produce information “GOT NOTIFICATION”.
 In the `imgs/outcome` are stored the results of VQC.
We recommend Postman tool for sending the test request.


## Local installation with `virtual environment`:
1. Open **terminal** and run:  
 `python3 -m pip install --user virtualenv`
2. Using **terminal** go to the folder where you downloaded files from repository and run:
  `python3 -m venv <name_of_environment>`
3. Activate environment, beeing in the same folder, use command:
  `./<name_of_environment>/Scripts/activate`
4. Being in folder with the app. Install all dependencies with command:
  `pip install -r VQC/requirements.txt`
    Now you can read instruction below and try to perform some experiments safely.
5. After experiments, to leave virtual environment, simply type:  
  `deactivate`
To read more about installing creating virtual encironment and installing packages in it go [here](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/).

# Folder description:
* `VQC` - main component that will perform checking it contains methods and utils folder
    * `app` folder containing all scripts needed to run the application
        * `methods`, `utils`, `otherFunctions` - Folders containing respectively necessary methods, utils and some small miscellaneous functions that do not fit to utils/methods  
    * `configuration` Folder with yaml config files
        * `configuration.yaml` file with methods and utils configuration
        * `db_config.yaml` file containing credentials for db access
        *  `boxes.txt` - file generated by the app with coordinates of boxes to be checked by template matching method
        *  `db_config_atlas.yaml` - some credentials for connecting to cloud based Atlas db
    * `docker-compose.yaml` special docker file we can use it instead of docker run. This is beneficial if we have a lot of port bingidns network stuff etc.
    * `Dockerfile` File from which we create a Docker image of our application
    * `tests` Folder with all tests
    * `requirements.txt` All dependencies
* `sender` - imitation of camera 
* `FIWARE` - Scripts responsible for creating entities, subscriptions etc. and minimalistic `docker-compose` file that seems to be enough for our application and which I've taken from [there](https://hub.docker.com/r/fiware/orion)
* `img` - All needded images for testing inside it we have 3 folders:
    * `template` - folder with some sample templates so that one can test it locally
    * `outcome` - folder where our methods will save outcomes
    * `control` - folder with sample photos of defected pcb our sender send paths to it for VQS
* `config_send.py` -  Python script for sending HTTP request to our app
* `pyproject.toml` and `setup.cfg` - Files needed for building wheel. Inspired by [this tutorial](https://packaging.python.org/tutorials/packaging-projects/).
* `db.json` - database containing templates and paths to them.
* `documentation` - folders containing more extensive description of everything
**More information about each folder and its content can be found in appropriate markdown files in documentation.**

*If don't want to use DockerImage or want to run tests/experiment with specific files you need to add VQC folder to your PYTHONPATH. On linux you can do it using*
`export PYTHONPATH=/data/app/VQC` 
*and on windows* 
`set PYTHONPATH=D:\VQC`

# Citation
The sample dataset to develop and test the method was used from:
* Weibo Huang, Peng Wei - A PCB Dataset for Defects Detection and Classification (https://arxiv.org/abs/1901.08204)


