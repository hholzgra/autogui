import subprocess
import shlex
import os.path
import re
import os

class ConfigStatus:

    def getConfig(self, dir):
        configStatus = os.path.join(dir, "config.status")

        if not os.path.exists(configStatus):
            return None

        try:
            # config.status from newer autoconf versions can show
            # the original configure options and variables used 
            configureLine = subprocess.check_output([configStatus, "--config"]).decode('utf-8')
        except:
            # on older versions the configure line is contained
            # in a comment near the config.status files head
            # line starts with '^# [not space]+configure
            f = open(configStatus, 'r')

            while True:
                line = f.readline()
                if not re.search("^#", line):
                    # we reached the end of the comment header
                    break
                matches = re.search('^# (\S*)configure(.*)' , line)
                if matches is not None:
                    # found what we're looking for
                    configureLine = matches.group(2)
                    break

            f.close()

        if configureLine is None:
            return None

        configArgs = shlex.split(configureLine)

        return configArgs

foo = ConfigStatus()
#x = foo.getConfig("/home/hartmut/projects/php/dev/5.3")
x = foo.getConfig(".")
print(x)
