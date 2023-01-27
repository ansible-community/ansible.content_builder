#!/usr/bin/env python3

import argparse
import pathlib


def refresh_ignore_files(target_dir):
    module_utils_directory = target_dir / "plugins/module_utils"
    plugin_utils_directory = target_dir / "plugins/plugin_utils"
    module_directory = target_dir / "plugins/modules"
    lookup_directory = target_dir / "plugins/lookup"

    def ignore_file(version):
        return target_dir / f"tests/sanity/ignore-{version}.txt"

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


def main():
    parser = argparse.ArgumentParser(
        description="Refresh the ignore files of the vmware_rest collection."
    )
    parser.add_argument(
        "--target-dir",
        dest="target_dir",
        type=pathlib.Path,
        default=pathlib.Path("."),
        help="location of the target repository (default: ./vmware_rest)",
    )

    args = parser.parse_args()
    refresh_ignore_files(target_dir=args.target_dir)


if __name__ == "__main__":
    main()
