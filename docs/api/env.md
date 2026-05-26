<a id="environment"></a>

# Environment

Environment management subcommands and supporting operations.

<a id="module-architekta.env.commands"></a>

<a id="commands"></a>

## Commands

CLI commands for environment management.

<a id="architekta.env.commands.install_editable"></a>

### architekta.env.commands.install_editable(packages=<typer.models.ArgumentInfo object>, all=<typer.models.OptionInfo object>, path=<typer.models.OptionInfo object>, include_tests=<typer.models.OptionInfo object>, env=<typer.models.OptionInfo object>, force=<typer.models.OptionInfo object>, dry_run=<typer.models.OptionInfo object>)

<a id="module-architekta.env.operations"></a>

<a id="operations"></a>

## Operations

Pure domain operations for environment management.

<a id="architekta.env.operations.EditableInstallRequest"></a>

### *class* architekta.env.operations.EditableInstallRequest(workspace_root, site_packages, package_names=<factory>, use_all=False, custom_path=None, include_tests=False, force=False, active_env=None, conda_prefix=None, target_env=None)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Explicit configuration for planning editable installs.

<a id="architekta.env.operations.EditableInstallRequest.workspace_root"></a>

#### workspace_root *: [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path)*

<a id="architekta.env.operations.EditableInstallRequest.site_packages"></a>

#### site_packages *: [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path)*

<a id="architekta.env.operations.EditableInstallRequest.package_names"></a>

#### package_names *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[str](https://docs.python.org/3/library/stdtypes.html#str), ...]*

<a id="architekta.env.operations.EditableInstallRequest.use_all"></a>

#### use_all *: [bool](https://docs.python.org/3/library/functions.html#bool)* *= False*

<a id="architekta.env.operations.EditableInstallRequest.custom_path"></a>

#### custom_path *: [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path) | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

<a id="architekta.env.operations.EditableInstallRequest.include_tests"></a>

#### include_tests *: [bool](https://docs.python.org/3/library/functions.html#bool)* *= False*

<a id="architekta.env.operations.EditableInstallRequest.force"></a>

#### force *: [bool](https://docs.python.org/3/library/functions.html#bool)* *= False*

<a id="architekta.env.operations.EditableInstallRequest.active_env"></a>

#### active_env *: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

<a id="architekta.env.operations.EditableInstallRequest.conda_prefix"></a>

#### conda_prefix *: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

<a id="architekta.env.operations.EditableInstallRequest.target_env"></a>

#### target_env *: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

<a id="architekta.env.operations.InstallPlan"></a>

### *class* architekta.env.operations.InstallPlan(package, pth_file, lines, skipped=False, skip_reason='')

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

A single editable-install action to execute.

<a id="architekta.env.operations.InstallPlan.package"></a>

#### package *: [PackageSpec](#architekta.env.utils.PackageSpec)*

<a id="architekta.env.operations.InstallPlan.pth_file"></a>

#### pth_file *: [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path)*

<a id="architekta.env.operations.InstallPlan.lines"></a>

#### lines *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[str](https://docs.python.org/3/library/stdtypes.html#str), ...]*

<a id="architekta.env.operations.InstallPlan.skipped"></a>

#### skipped *: [bool](https://docs.python.org/3/library/functions.html#bool)* *= False*

<a id="architekta.env.operations.InstallPlan.skip_reason"></a>

#### skip_reason *: [str](https://docs.python.org/3/library/stdtypes.html#str)* *= ''*

<a id="architekta.env.operations.InstallResult"></a>

### *class* architekta.env.operations.InstallResult(plans, site_packages)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Result of planning an editable install.

<a id="architekta.env.operations.InstallResult.plans"></a>

#### plans *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[InstallPlan](#architekta.env.operations.InstallPlan), ...]*

<a id="architekta.env.operations.InstallResult.site_packages"></a>

#### site_packages *: [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path)*

<a id="architekta.env.operations.plan_editable_install"></a>

### architekta.env.operations.plan_editable_install(request)

Plan editable installs without performing I/O.

* **Raises:**
  * [**CondaEnvNotFound**](#architekta.env.exceptions.CondaEnvNotFound) – If target_env is specified but not the active environment.
  * [**InvalidPackagePath**](#architekta.env.exceptions.InvalidPackagePath) – If a package path is invalid.

<a id="architekta.env.operations.execute_install_plans"></a>

### architekta.env.operations.execute_install_plans(result)

Execute planned editable installs by writing .pth files.

<a id="module-architekta.env.utils"></a>

<a id="utilities"></a>

## Utilities

Utilities for explicit editable-install environment planning.

<a id="architekta.env.utils.PackageSpec"></a>

### *class* architekta.env.utils.PackageSpec(name, path)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

A resolved package with its name and path.

<a id="architekta.env.utils.PackageSpec.name"></a>

#### name *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

<a id="architekta.env.utils.PackageSpec.path"></a>

#### path *: [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path)*

<a id="architekta.env.utils.get_site_packages"></a>

### architekta.env.utils.get_site_packages()

<a id="architekta.env.utils.is_current_conda_env"></a>

### architekta.env.utils.is_current_conda_env(name, active_env)

<a id="architekta.env.utils.is_base_conda_env"></a>

### architekta.env.utils.is_base_conda_env(conda_prefix)

<a id="architekta.env.utils.resolve_package_paths"></a>

### architekta.env.utils.resolve_package_paths(workspace_root, package_names, use_all, custom_path)

<a id="module-architekta.env.exceptions"></a>

<a id="exceptions"></a>

## Exceptions

<a id="architekta.env.exceptions.EnvError"></a>

### *exception* architekta.env.exceptions.EnvError

Bases: [`Exception`](https://docs.python.org/3/library/exceptions.html#Exception)

<a id="architekta.env.exceptions.InvalidPackagePath"></a>

### *exception* architekta.env.exceptions.InvalidPackagePath

Bases: [`EnvError`](#architekta.env.exceptions.EnvError)

<a id="architekta.env.exceptions.CondaEnvNotFound"></a>

### *exception* architekta.env.exceptions.CondaEnvNotFound

Bases: [`EnvError`](#architekta.env.exceptions.EnvError)
