import sys
from subprocess import PIPE, Popen


def in_use(device):
    if "windows" in sys.platform:
        # TODO: use Handle
        # http://stackoverflow.com/questions/18059798/windows-batch-equivalent-of-fuser-k-folder
        # https://technet.microsoft.com/en-us/sysinternals/bb896655
        return False
    pipe = Popen(["fuser", device], stdout=PIPE, stderr=PIPE)
    stdout, stderr = pipe.communicate()
    return stdout != ""


if __name__ == "__main__":
    from decocare.scan import scan

    candidate = (sys.argv[1:2] or [scan()]).pop()
    print(in_use(candidate))
