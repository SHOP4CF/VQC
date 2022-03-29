from app.otherFunctions import fiware_response
import datetime

fiware_statuses = {0: "Waiting", 1: "Working", 2: "Error"}


def log_fiware_resp_exception(
    logger, msg, level="info", send_fiware=False, fiware_status=1, raise_exception=False
):
    """Function for sending any notification to user, it may save log, update fiware entity or raise exception

    Args:
        logger (logging.logger): logger obtained with function logging.getLogger()
        msg (str): [message to be sent]
        level (str, optional): [Level for logger]. Defaults to "info".
        send_fiware (bool, optional): [either to send fiware notification or not]. Defaults to False.
        fiware_status (int, optional): [what status should be sent to fiware]. Defaults to 1.
        raise_exception (bool, optional): [whether to raise an exception or not]. Defaults to False.

    Raises:
        SystemExit: No matter what caused an exception we always send SystemExit with appropriate message it does nut shut down entire server just current query

    Returns:
        [int]: returns status returned by Fiware as sometimes it may reject our query and we need to react
    """
    if level == "error":
        logger.error(msg)
    elif level == "warning":
        logger.warning(msg)
    else:
        logger.info(msg)
    fiware_status_code = None
    if send_fiware:
        # It is important to change some attribute every time, so that subscription is always send! we use time.time() for this purpose
        fiware_status_code = fiware_response.respond(
            fiware_statuses[fiware_status], str(datetime.datetime.utcnow()), msg
        )

    if raise_exception:
        raise SystemExit(msg)

    if fiware_status_code is not None:
        return fiware_status_code
