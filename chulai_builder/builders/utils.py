try:
    import ujson as json
except:
    import json


class OutputManager(object):
    IGNORES = (
        "---> ",
        "Removing intermediate container ",
        "Successfully built ",
        "Step "
    )

    def __init__(self):
        self._logs = []

    def new_log(self, log):
        if isinstance(log, str):
            log = [log]
        for line in log:
            line = line.strip()
            self._logs.append(line)
            for ign in self.IGNORES:
                if line.startswith(ign):
                    break
            else:
                yield json.dumps(dict(type="log", message=line)) + "\n"

    def new_event(self, **event):
        msg = "\n".join("{0}: {1}".format(k, v) for k, v in event.items())
        self._logs.append(msg)
        yield json.dumps(dict(type="event", message=msg)) + "\n"

    @property
    def log(self):
        return "\n".join(self._logs) + "\n"
