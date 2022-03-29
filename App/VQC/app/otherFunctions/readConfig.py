import confuse
import yaml
import logging

from app.otherFunctions import enums, debug_help


"""
In this function we assume that given config is methods and utils config and no any other, we just perform validation of it
so it always need to have some attributes and also those attributes need to have some specific values
"""

logger = logging.getLogger("app")


def read_config(config_path):
    """
    Function validates whole config and then just returns it:
    Args:
        config_path (str): path to our config has to be YAML
    Returns:
        config (dict): configuration as a dictonary object
    """
    try:
        config = confuse.Configuration("testing", __name__)
        config.set_file(config_path)
    except Exception as e:
        msg = f"App.otherFunctions.readConfig: Provided incorrect configuration path! given path is: {config_path}"
        debug_help.log_fiware_resp_exception(
            logger,
            msg,
            "error",
            send_fiware=True,
            fiware_status=enums.Status.Error,
            raise_exception=True,
        )
    try:
        interface = config["interface"]
        interface["method"].as_choice(
            ["difference", "template_matching", "k_means"])
        interface["entity_type"].as_str_seq()
        interface["factory_id"].as_str_seq()
        interface["entity_id"].as_str_seq()
        interface["component_id"].as_str_seq()
        interface["fiware_host"].as_str_seq()
        interface["to_inspect_attr"].as_str_seq()
        interface["template_attr"].as_str_seq()
        interface["histogram_eq"].as_choice([True, False])
        interface["using_cropped"].as_choice([True, False])
        interface["path_for_outcomes"].as_str_seq()
        interface["save_all"].as_choice([True, False])

        methods = config["methods"]
        utils = config["utils"]

        diff = methods["difference"]
        diff["er_shape"].as_choice([0, 1, 2])
        diff["er_size"].as_number()
        diff["kernel_size"].as_number()
        diff["closing"].as_choice([True, False])
        diff["closing_size"].as_number()
        diff["opening"].as_choice([True, False])
        diff["opening_size"].as_number()
        diff["method"].as_choice(["complex", "simple"])
        diff["simple_method_thresh"].as_number()

        temp = methods["template_matching"]
        temp["matching_method"].as_choice([0, 1, 2, 3, 4, 5])
        temp["template_size"].as_number()
        temp["min_difference"].as_number()

        aligner = utils["aligner"]
        aligner["max_features"].as_number()
        aligner["good_match_percent"].as_number()

        box_generator = utils["box_generator"]
        box_generator["er_shape"].as_choice([0, 1, 2])
        box_generator["er_size"].as_number()
        box_generator["closing"].as_choice([True, False])
        box_generator["opening"].as_choice([True, False])
        box_generator["method"].as_choice(["complex", "simple"])
        box_generator["shift"].as_number(),
        box_generator["low_area_thresh"].as_number(),
        box_generator["path"].as_str_seq()

    except confuse.ConfigError as e:
        msg = "App.otherFunctions.readConfig: " + str(e)
        debug_help.log_fiware_resp_exception(
            logger,
            msg,
            "error",
            send_fiware=True,
            fiware_status=enums.Status.Error,
            raise_exception=True,
        )

    with open(config_path) as f:
        config = yaml.safe_load(f)

    return config
