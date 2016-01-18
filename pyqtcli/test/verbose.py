import re


def format_msg(msg):
    """
    Format a message from verbose to delete extra spaces and carriage return.

    Args:
        msg (str): Message to format.

    Returns:
        str: Formatted message.
    """
    # TODO: Check case when sentence is cut in a space
    return re.sub("\n\s+", "", msg).strip()
