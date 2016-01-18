"""Module regrouping functions to display different kinds of information."""

import os
import click
import textwrap

from enum import Enum


class Message(Enum):
    INFO = "[INFO]: "
    WARNING = "[WARNING]: "
    ERROR = "[ERROR]: "


def format_message(msg, msg_type):
    """Format a message in function of message type and terminal's size.

    Args:
        msg (str): Message to format.
        msg_type (Message): Kind of message.

    Returns:
        str: Return formatted message.

    """

    term_size = os.get_terminal_size()
    return textwrap.fill(msg, width=term_size.columns, initial_indent="",
                         subsequent_indent=" " * len(msg_type.value))


def info(msg, verbose=True):
    """Display information message.

    Args:
        msg (str): Message to display
        verbose (bool): If True the message is displayed.

    Returns:
        str: Return formatted message.

    """
    if not verbose:
        return

    click.secho(Message.INFO.value, fg="green", bold=True, nl=False)

    full_msg = Message.INFO.value + msg
    msg = format_message(full_msg, Message.INFO)[len(Message.INFO.value):]
    click.secho(msg, fg="green")

    return full_msg


def warning(msg):
    """Display warning message.

    Args:
        msg (str): Message to display

    Returns:
        str: Return formatted message.

    """
    click.secho(Message.WARNING.value, fg="yellow", bold=True, nl=False)

    full_msg = Message.WARNING.value + msg
    msg = format_message(full_msg, Message.WARNING)[len(Message.WARNING.value):]
    click.secho(msg, fg="yellow")

    return full_msg


def error(msg):
    """Display error message.

    Args:
        msg (str): Message to display

    Returns:
        str: Return formatted message.

    """
    click.secho(Message.ERROR.value, fg="red", bold=True, nl=False, err=True)

    full_msg = Message.ERROR.value + msg
    msg = format_message(full_msg, Message.ERROR)[len(Message.ERROR.value):]
    click.secho(msg, fg="red", err=True)

    return full_msg
