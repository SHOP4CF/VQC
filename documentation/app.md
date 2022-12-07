## VQC

Main component is a `Flask application` running on `waitress`. It connects to the `MongoDb` to get paths for templates and listens on `/config/` for GET to show configuration or for POST to update it and on `/inspect/` for POST to information about new inference to be performed.

### Short scripts descriptions:
* `__init__.py` - script that creates our app. Initialize all `loggers`, make connection with `db` and register `config` and `inspect` URLs.
* `Analysis.py` - heart of our application it menages the inspection pipeline. It initialize all methods and utils and based on current configuration perform inspection:
    * in `__init__`we initialize all needed stuff **we need to set correct path for configuration!**
    * in `set_config` we just change configuration based on  given config file path.
    * in analyse we:
        * load image to be inspected 
        * load template or get it from dict if it was loaded earlier
        * apply some transformations like `alligning`, `cropping`
        * use chosen method to perform analysis
        * returns decision (Defected/valid)
* `db.py` - methods for communication with db it stores `mongodb Object` and we can write needed queries here, currently it can return either one needed template with `get_template` or all templates with `get_all_templates`. **For db connection to work we need to specify all needed credential in instance/db_config.yaml**
* `config.py` - script that listen on `/config/` to either show or update configuration. It does update using `Analysis` class
* `inspect` - script that listen on `/inspect/` (on this URL we obtain notifications from FIWARE) if it get POST request it checks whether is is valid and if it is it prepare everything for inspection and uses `Analysis` class to do it. It at first stores needed data in `g` object that is flask specific and stores data within one request. Then `@after_request` and `call_on_close` decorators are used to **make sure that analysis is performed after we send response to FIWARE** from which we get subscription it is done not to have problems with timeouts. After analysis is performed we update our `camera` entity in FIWARE so that other scripts that look for changes in our entity can get notifications.

**All warnings are stored inside logs directory in appropriate log file to help debugging**