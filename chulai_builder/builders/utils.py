try:
    import ujson as json
except:
    import json


class OutputManager(object):
    IGNORES = (
        "---> ",
        "Removing intermediate container ",
        "Successfully built ",
        "Step ",
        "Pulling from ",
        "Already exists"
    )

    def __init__(self):
        self._logs = []

    def new_log(self, log):
        if isinstance(log, str):
            log = [log]
        for line in log:
            line = line.strip()
            if not line:
                continue
            self._logs.append(line)
            for ign in self.IGNORES:
                if line.startswith(ign):
                    break
            else:
                yield json.dumps(dict(type="log", message=line)) + "\n"

    def new_event(self, *args, **events):
        info = {}
        for current in args:
            info.update(current)
        info.update(events)
        msg = "\n".join("{0}: {1}".format(k, v) for k, v in info.items())
        self._logs.append(msg)
        yield json.dumps(dict(type="event", message=msg)) + "\n"

    def raw_event(self, message):
        self._logs.append("raw event: {0}".format(message))
        yield json.dumps(dict(type="event", **message)) + "\n"

    @property
    def log(self):
        return "\n".join(self._logs) + "\n"
