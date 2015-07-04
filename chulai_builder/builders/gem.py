from .env import env


class Gemfile(object):
    # TODO: need better parsing, try porting `gemnasium-parser`

    def __init__(self, gemfile, gemfile_lock):
        self._gemfile = self._parse_gemfile(gemfile)
        self._gemfile_lock = self._parse_gemfile_lock(gemfile_lock)

        dep_gemfile = set(self._gemfile["dependencies"].keys())
        dep_gemfile_lock = set(self._gemfile_lock["dependencies"].keys())
        if dep_gemfile != dep_gemfile_lock:
            raise ValueError("inconsistence dependencies")

        src_gemfile = self._gemfile["source"]
        src_gemfile_lock = self._gemfile_lock["source"]
        if src_gemfile != src_gemfile_lock:
            raise ValueError("inconsistence source!")

    @classmethod
    def _parse_gemfile(cls, gemfile):
        source = None
        dependencies = {}
        for line in gemfile.splitlines():
            if not line:
                continue
            token, content = [part.strip() for part in line.split(maxsplit=1)]
            if token == "source":
                source = content.strip("\"'")
                if not source.endswith("/"):
                    source += "/"
            elif token == "gem":
                gem, sep, opt = content.partition(",")
                gem = gem.strip("\"'")
                opt = opt.strip()
                if sep:
                    dependencies[gem] = opt
                else:
                    dependencies[gem] = None

        return dict(source=source, dependencies=dependencies)

    @classmethod
    def _parse_gemfile_lock(cls, gemfile_lock):
        rough = cls._rouph_parse_lock(gemfile_lock)
        gem = cls._parse_gemfile_lock_gem(rough)

        dependencies = {}
        for dep in rough["DEPENDENCIES"]:
            dep, sep, opt = dep.strip().partition(" ")
            dependencies[dep] = opt or None

        return dict(
            source=gem["remote"],
            specs=gem["specs"],
            platforms=[platform.strip() for platform in rough["PLATFORMS"]],
            dependencies=dependencies
        )

    @classmethod
    def _parse_gemfile_lock_gem(cls, rough):
        """parse gem from rough parsed gemfile lock"""
        gem = {}
        last_padding = -1
        section = None
        for line in rough["GEM"]:
            key, sep, val = line.strip().partition(":")
            val = val.strip()
            if sep:
                # "spec:" or "remote: some-remote"
                section = gem[key] = {}
                if val:
                    gem[key] = val
                continue

            full_len = len(line)
            line = line.strip()
            padding = full_len - len(line)
            if last_padding < 0 or padding <= last_padding:
                last_padding = padding
                sub_section = section[line] = []
            else:
                sub_section.append(line)
        return gem

    @classmethod
    def _rouph_parse_lock(cls, gemfile_lock):
        result = {}
        for line in gemfile_lock.splitlines():
            if line.isupper():
                section = result[line.strip()] = []
            elif line.strip():
                section.append(line.rstrip())
        return result

    @property
    def dependencies(self):
        return list(self._gemfile_dependencies.keys())

    def inject_dependency(self, gem, ver, specs=None):
        if gem in self._gemfile_lock["dependencies"]:
            return

        self._gemfile["dependencies"][gem] = "'= {0}'".format(ver)

        self._gemfile_lock["specs"]["{0} ({1})".format(gem, ver)] = specs or []
        self._gemfile_lock["dependencies"][gem] = "(= {0})".format(ver)

    @property
    def source(self):
        return self._gemfile["source"]

    @source.setter
    def source(self, new_source):
        if not new_source.endswith("/"):
            new_source += "/"
        self._gemfile["source"] = self._gemfile_lock["source"] = new_source
        return new_source

    @property
    def gemfile(self):
        template = env.get_template("rails/gemfile")
        return template.render(self._gemfile)

    @property
    def gemfile_lock(self):
        template = env.get_template("rails/gemfile_lock")
        return template.render(self._gemfile_lock)


if __name__ == "__main__":
    gf = Gemfile(open("Gemfile").read(), open("Gemfile.lock").read())
    gf.inject_dependency("mysql2", "0.3.18", [])
    gf.inject_dependency("puma", "2.11.2", ["rack (>= 1.1, < 2.0)"])
    print(gf.gemfile_lock)
    #print("#" * 20)
    #print(gf.gemfile_lock)
    #print("#" * 20)
    #print(gf.gemfile_lock)
