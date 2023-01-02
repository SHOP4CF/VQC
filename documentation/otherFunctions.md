## Other Functions:

`enums.py` - Contains only definition of enums for more readability. For example when previously we written `vqc_status=0` now we can write `vqc_status = enums.Status.Waiting`

`create_logger.py`:
* `setup_logger.py` - makes it available to create wanted logger for later use. 
* `create_loggers.py` - given list of names and destinations create loggers

`debug_help.py`:
* `log_fiware_resp_exception` - functions that make it possible to log some information to given logger, update status of our fiware entity and raise an exception with given message. We can select which operations we want to perform
* `get_control_sum` - This is just for being sure that after updating our entity some parameter will change for sure so that if someone is subscribing to our changes they will be notified.

`fiware_response.py` - function that sends PATCH request to FIWARE that will update our entity

`read_config.py` - script that validates given configuration file, if something is wrong in config then our application will break so we raise an exception
