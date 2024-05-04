import datetime
import discord
from discord.ext import commands

class Logger(commands.Cog):
    """
    A simple logging class that can be used to print messages to the console.
    """

    @staticmethod
    def get_current_time():
        return datetime.datetime.now().strftime("%H:%M:%S")

    log_formats = {
        'INFO': "\x1b[32m[INFO] {}" + "\x1b[90m" + " , " + "\x1b[0m" + "{}" + "\x1b[0m",
        'WARNING': "\x1b[33m[WARN] {}" + "\x1b[90m" + " , " + "\x1b[0m" + "{}" + "\x1b[0m",
        'ERROR': "\x1b[31m[ERROR] {}" + "\x1b[90m" + " , " + "\x1b[0m" + "{}" + "\x1b[0m",
        'CRITICAL': "\x1b[31m[CRITICAL] {}" + "\x1b[90m" + " , " + "\x1b[0m" + "{}" + "\x1b[0m",
    }

    @classmethod
    def log(cls, message, log_type='INFO'):
        if log_type not in cls.log_formats:
            log_type = 'INFO'

        formatted_message = cls.log_formats[log_type].format(cls.get_current_time(), message)
        print(formatted_message)