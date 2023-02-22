import pathlib

from ansible.plugins.action import ActionBase


def refresh_ignore_files(target_dir):
    module_utils_directory = pathlib.Path(target_dir +  "/plugins/module_utils") #target_dir / "plugins/module_utils"
    plugin_utils_directory = pathlib.Path(target_dir + "/plugins/plugin_utils")
    module_directory = pathlib.Path(target_dir + "/plugins/modules")
    lookup_directory = pathlib.Path(target_dir + "/plugins/lookup")

    def ignore_file(version):
        return pathlib.Path(target_dir + f"/tests/sanity/ignore-{version}.txt")

    def rp(m):
        # return the relative path (rp) of the file inside the collection
        return pathlib.Path(*pathlib.Path(m).parts[-3:])

    with ignore_file("2.9").open("w") as f:
        f.write(
            "plugins/modules/vcenter_vm_guest_customization.py pep8!skip\n"
        )  # E501: line too long (189 > 160 characters)
        f.write(
            "plugins/modules/appliance_infraprofile_configs.py pep8!skip\n"
        )  # E501: line too long (302 > 160 characters)
        for m in module_directory.glob("*.py"):
            f.write(f"{rp(m)} import-2.6!skip\n")
            f.write(f"{rp(m)} compile-2.6!skip\n")
            f.write(f"{rp(m)} import-2.7!skip\n")
            f.write(f"{rp(m)} compile-2.7!skip\n")
            f.write(f"{rp(m)} import-3.5!skip\n")
            f.write(f"{rp(m)} compile-3.5!skip\n")
            f.write(f"{rp(m)} future-import-boilerplate!skip\n")
            f.write(f"{rp(m)} metaclass-boilerplate!skip\n")
            f.write(f"{rp(m)} validate-modules:missing-if-name-main\n")
            f.write(f"{rp(m)} validate-modules:missing-main-call\n")
        for m in lookup_directory.glob("*.py"):
            f.write(f"{rp(m)} compile-2.6!skip\n")
            f.write(f"{rp(m)} compile-2.7!skip\n")
            f.write(f"{rp(m)} compile-3.5!skip\n")
        for m in module_utils_directory.glob("*.py"):
            f.write(f"{rp(m)} future-import-boilerplate!skip\n")
            f.write(f"{rp(m)} metaclass-boilerplate!skip\n")
            f.write(f"{rp(m)} import-2.6!skip\n")
            f.write(f"{rp(m)} compile-2.6!skip\n")
            f.write(f"{rp(m)} import-2.7!skip\n")
            f.write(f"{rp(m)} compile-2.7!skip\n")
            f.write(f"{rp(m)} import-3.5!skip\n")
            f.write(f"{rp(m)} compile-3.5!skip\n")
        for m in plugin_utils_directory.glob("*.py"):
            f.write(f"{rp(m)} compile-2.6!skip\n")
            f.write(f"{rp(m)} compile-2.7!skip\n")
            f.write(f"{rp(m)} compile-3.5!skip\n")

    with ignore_file("2.10").open("w") as f:
        f.write(
            "plugins/modules/vcenter_vm_guest_customization.py pep8!skip\n"
        )  # E501: line too long (189 > 160 characters)
        f.write(
            "plugins/modules/appliance_infraprofile_configs.py pep8!skip\n"
        )  # E501: line too long (302 > 160 characters)
        for m in module_directory.glob("*.py"):
            f.write(f"{rp(m)} import-2.6!skip\n")
            f.write(f"{rp(m)} compile-2.6!skip\n")
            f.write(f"{rp(m)} import-2.7!skip\n")
            f.write(f"{rp(m)} compile-2.7!skip\n")
            f.write(f"{rp(m)} import-3.5!skip\n")
            f.write(f"{rp(m)} compile-3.5!skip\n")
            f.write(f"{rp(m)} future-import-boilerplate!skip\n")
            f.write(f"{rp(m)} metaclass-boilerplate!skip\n")
            f.write(f"{rp(m)} validate-modules:missing-if-name-main\n")
            f.write(f"{rp(m)} validate-modules:missing-main-call\n")
        for m in lookup_directory.glob("*.py"):
            f.write(f"{rp(m)} compile-2.6!skip\n")
            f.write(f"{rp(m)} compile-2.7!skip\n")
            f.write(f"{rp(m)} compile-3.5!skip\n")
        for m in module_utils_directory.glob("*.py"):
            f.write(f"{rp(m)} future-import-boilerplate!skip\n")
            f.write(f"{rp(m)} metaclass-boilerplate!skip\n")
            f.write(f"{rp(m)} import-2.6!skip\n")
            f.write(f"{rp(m)} compile-2.6!skip\n")
            f.write(f"{rp(m)} import-2.7!skip\n")
            f.write(f"{rp(m)} compile-2.7!skip\n")
            f.write(f"{rp(m)} import-3.5!skip\n")
            f.write(f"{rp(m)} compile-3.5!skip\n")
        for m in plugin_utils_directory.glob("*.py"):
            f.write(f"{rp(m)} compile-2.6!skip\n")
            f.write(f"{rp(m)} compile-2.7!skip\n")
            f.write(f"{rp(m)} compile-3.5!skip\n")

    with ignore_file("2.11").open("w") as f:
        f.write(
            "plugins/modules/vcenter_vm_guest_customization.py pep8!skip\n"
        )  # E501: line too long (189 > 160 characters)
        f.write(
            "plugins/modules/appliance_infraprofile_configs.py pep8!skip\n"
        )  # E501: line too long (302 > 160 characters)
        for m in module_directory.glob("*.py"):
            f.write(f"{rp(m)} import-2.6!skip\n")
            f.write(f"{rp(m)} compile-2.6!skip\n")
            f.write(f"{rp(m)} import-2.7!skip\n")
            f.write(f"{rp(m)} compile-2.7!skip\n")
            f.write(f"{rp(m)} import-3.5!skip\n")
            f.write(f"{rp(m)} compile-3.5!skip\n")
            f.write(f"{rp(m)} future-import-boilerplate!skip\n")
            f.write(f"{rp(m)} metaclass-boilerplate!skip\n")
            f.write(f"{rp(m)} validate-modules:missing-if-name-main\n")
            f.write(f"{rp(m)} validate-modules:missing-main-call\n")
        for m in lookup_directory.glob("*.py"):
            f.write(f"{rp(m)} import-2.6!skip\n")
            f.write(f"{rp(m)} compile-2.6!skip\n")
            f.write(f"{rp(m)} import-2.7!skip\n")
            f.write(f"{rp(m)} compile-2.7!skip\n")
            f.write(f"{rp(m)} import-3.5!skip\n")
            f.write(f"{rp(m)} compile-3.5!skip\n")
        for m in module_utils_directory.glob("*.py"):
            f.write(f"{rp(m)} future-import-boilerplate!skip\n")
            f.write(f"{rp(m)} metaclass-boilerplate!skip\n")
            f.write(f"{rp(m)} import-2.6!skip\n")
            f.write(f"{rp(m)} compile-2.6!skip\n")
            f.write(f"{rp(m)} import-2.7!skip\n")
            f.write(f"{rp(m)} compile-2.7!skip\n")
            f.write(f"{rp(m)} import-3.5!skip\n")
            f.write(f"{rp(m)} compile-3.5!skip\n")
        for m in plugin_utils_directory.glob("*.py"):
            f.write(f"{rp(m)} import-2.6!skip\n")
            f.write(f"{rp(m)} compile-2.6!skip\n")
            f.write(f"{rp(m)} import-2.7!skip\n")
            f.write(f"{rp(m)} compile-2.7!skip\n")
            f.write(f"{rp(m)} import-3.5!skip\n")
            f.write(f"{rp(m)} compile-3.5!skip\n")

    with ignore_file("2.12").open("w") as f:
        f.write(
            "plugins/modules/vcenter_vm_guest_customization.py pep8!skip\n"
        )  # E501: line too long (189 > 160 characters)
        f.write(
            "plugins/modules/appliance_infraprofile_configs.py pep8!skip\n"
        )  # E501: line too long (302 > 160 characters)
        for m in module_directory.glob("*.py"):
            pass
        for m in lookup_directory.glob("*.py"):
            pass

    with ignore_file("2.13").open("w") as f:
        f.write(
            "plugins/modules/vcenter_vm_guest_customization.py pep8!skip\n"
        )  # E501: line too long (189 > 160 characters)
        f.write(
            "plugins/modules/appliance_infraprofile_configs.py pep8!skip\n"
        )  # E501: line too long (302 > 160 characters)
        for m in module_directory.glob("*.py"):
            pass
        for m in lookup_directory.glob("*.py"):
            pass
        for m in module_utils_directory.glob("*.py"):
            pass

    with ignore_file("2.14").open("w") as f:
        f.write(
            "plugins/modules/vcenter_vm_guest_customization.py pep8!skip\n"
        )  # E501: line too long (189 > 160 characters)
        f.write(
            "plugins/modules/appliance_infraprofile_configs.py pep8!skip\n"
        )  # E501: line too long (302 > 160 characters)
        for m in module_directory.glob("*.py"):
            pass
        for m in lookup_directory.glob("*.py"):
            pass
        for m in module_utils_directory.glob("*.py"):
            pass

    with ignore_file("2.15").open("w") as f:
        f.write(
            "plugins/modules/vcenter_vm_guest_customization.py pep8!skip\n"
        )  # E501: line too long (189 > 160 characters)
        f.write(
            "plugins/modules/appliance_infraprofile_configs.py pep8!skip\n"
        )  # E501: line too long (302 > 160 characters)
        for m in module_directory.glob("*.py"):
            pass
        for m in lookup_directory.glob("*.py"):
            pass
        for m in module_utils_directory.glob("*.py"):
            pass


class ActionModule(ActionBase):

    def __init__(self, *args, **kwargs):
        super(ActionModule, self).__init__(*args, **kwargs)
        self._validator_name = None
        self._result = {}

    def _debug(self, name, msg):
        """Output text using ansible's display
        :param msg: The message
        :type msg: str
        """
        msg = "<{phost}> {name} {msg}".format(phost=self._playhost, name=name, msg=msg)
        self._display.vvvv(msg)

    def run(self, tmp=None, task_vars=None):
        """The std execution entry pt for an action plugin
        :param tmp: no longer used
        :type tmp: none
        :param task_vars: The vars provided when the task is run
        :type task_vars: dict
        :return: The results from the parser
        :rtype: dict
        """

        self._result = super(ActionModule, self).run(tmp, task_vars)
        self._task_vars = task_vars

        args = self._task.args
        refresh_ignore_files(target_dir=args.get("target_dir"))

        return self._result
