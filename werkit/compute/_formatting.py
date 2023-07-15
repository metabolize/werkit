def format_time(seconds: float) -> str:
    minutes, seconds = divmod(seconds, 60)
    if minutes > 0:
        return "{} min, {} sec".format(minutes, seconds)
    else:
        return "{} sec".format(seconds)
