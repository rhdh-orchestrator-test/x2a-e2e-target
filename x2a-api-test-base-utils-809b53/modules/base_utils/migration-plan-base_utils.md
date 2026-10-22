---
source-path: site-modules/base_utils
---

# Migration Plan: base_utils

**TLDR**: `base_utils` is a host-baseline utility class reached through `role::app_server` → `profile::base::base` when `manage_utils` is enabled. Within the validated `base_utils` scope, it manages an optional `/etc/motd` template and installs OS-specific utility packages. The package values, Hiera mappings, template contents, and custom-component behavior are reported source-data assertions and must be verified against the corresponding files before implementation. Unrelated HAProxy, application, PostgreSQL, Redis, APT, systemd, NTP, and syslog resources are deferred to separate migrations.

## Service Type and Instances

**Service Type**: Host baseline / operating-system utility management

**Configured Instances**:

- **Base utility package set — Debian**
  - Purpose: Install baseline utility packages on Debian-family systems
  - Packages: `vim`, `wget`, `curl`, `jq`, `dnsutils`
  - Package state: installed
  - Ansible mapping: `base_utils_utility_packages`

- **Base utility package set — RedHat**
  - Purpose: Install baseline utility packages on RedHat-family systems
  - Packages: `vim-enhanced`, `wget`, `curl`, `jq`, `bind-utils`
  - Package state: installed
  - Ansible mapping: `base_utils_utility_packages`

- **Message of the day**
  - Purpose: Manage the host MOTD when enabled
  - Location/Path: `/etc/motd`
  - Source template: `base_utils/motd.erb`
  - Owner: `root`
  - Group: `root`
  - Mode: `0644`
  - Render count: 1 when MOTD management is enabled
  - Ansible resource: `ansible.builtin.template`

The Debian, RedHat, and common package values require verification against the supplied Hiera source files. The provided validation analysis confirms only the existence of the `$utility_packages.each` loop, not its resolved values or iteration counts.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

```text
### Manifests

- `site-modules/role/manifests/app_server.pp`
- `site-modules/profile/manifests/base/base.pp`
- `site-modules/base_utils/manifests/init.pp`

### Templates

- `base_utils/motd.erb` — referenced by the manifest through `template('base_utils/motd.erb')`; the file is not present in the supplied directory listing and must be located or recreated before migration.

### Custom components

- `site-modules/base_utils/lib/facter/base_utils_info.rb`
- `site-modules/base_utils/functions/ensure_value.pp`
- `site-modules/base_utils/functions/normalize_port.pp`
- `site-modules/base_utils/types/ensure_value.pp`
- `site-modules/base_utils/types/log_level.pp`
- `site-modules/base_utils/types/port.pp`
- `site-modules/base_utils/plans/health_check.pp`
- `site-modules/base_utils/plans/rolling_restart.pp`
```

The migration scope is limited to the `base_utils` dependency path and its listed custom components. The wider analysis contains 134 files, including HAProxy, application-stack, PostgreSQL, Redis, APT, and systemd manifests and templates. Those files are deferred and require separate migration plans.

## Module Explanation

The module execution path is:

1. **`role::app_server`** (`site-modules/role/manifests/app_server.pp`):
   - Includes `profile::base::base`.
   - Provides the supplied entry point for the `base_utils` dependency path.
   - Does not directly manage `base_utils` resources.
   - Also includes unrelated application-stack, HAProxy, PostgreSQL, and Redis resources, which are outside this migration.

2. **`profile::base::base`** (`site-modules/profile/manifests/base/base.pp`):
   - Evaluates the `manage_utils` condition.
   - Declares `base_utils` when `manage_utils` is true.
   - Separately evaluates NTP and syslog management on Linux.
   - Manages `package['chrony']`, `service['chronyd']`, `package['rsyslog']`, and `service['rsyslog']` outside the `base_utils` class.
   - The NTP and syslog resources are deferred from this role.

3. **`base_utils`** (`site-modules/base_utils/manifests/init.pp`):
   - Resolves `manage_motd`, `motd_template`, and `utility_packages` through first-found Hiera lookup behavior as reported by the source plan.
   - Declares `/etc/motd` before the package loop when `manage_motd` is true.
   - Manages `/etc/motd` with:
     - Ensure: `file`
     - Owner: `root`
     - Group: `root`
     - Mode: `0644`
     - Source: `template('base_utils/motd.erb')`
   - Renders `base_utils/motd.erb` once when MOTD management is enabled.
   - Creates no `/etc/motd` resource when `manage_motd` is false.
   - Iterates over `$utility_packages.each`.
   - The source analysis confirms the loop but does not confirm resolved values. The following expansions are reported by the source plan and require Hiera verification:
     - Debian: `vim`, `wget`, `curl`, `jq`, `dnsutils`
     - RedHat: `vim-enhanced`, `wget`, `curl`, `jq`, `bind-utils`
     - Common default: no packages
   - No explicit `->` or `~>` relationships are declared.
   - No package resource notifies or subscribes to another resource.
   - No service restart is triggered by MOTD changes.
   - Package resources are independent of the MOTD resource in the Puppet relationship graph.

### Reported loop expansions requiring source verification

- **Debian `utility_packages` loop**:
  - Iteration 1: `vim` → package state `installed`
  - Iteration 2: `wget` → package state `installed`
  - Iteration 3: `curl` → package state `installed`
  - Iteration 4: `jq` → package state `installed`
  - Iteration 5: `dnsutils` → package state `installed`

- **RedHat `utility_packages` loop**:
  - Iteration 1: `vim-enhanced` → package state `installed`
  - Iteration 2: `wget` → package state `installed`
  - Iteration 3: `curl` → package state `installed`
  - Iteration 4: `jq` → package state `installed`
  - Iteration 5: `bind-utils` → package state `installed`

- **Common default `utility_packages` loop**:
  - Iteration count: 0
  - Value: `[]`
  - Result: no package resources

## Variables

**Variable Flow Summary**: 3 class parameters across 3 supplied Hiera data files: one common data file and two OS-specific sibling overrides. The reported lookup behavior is first-found rather than a three-level sequential hierarchy. Exact values require verification because the supplied structured analysis does not include Hiera results.

### Variable Definitions

#### `site-modules/base_utils/data/common.yaml` — common defaults

The following values are reported by the source plan and require source-file verification:

- `base_utils::manage_motd`: `true` (type: boolean)
- `base_utils::motd_template`: `base_utils/motd.erb` (type: string)
- `base_utils::utility_packages`: `[]` (type: array of strings)

Ansible mapping in `defaults/main.yml`:

- `base_utils_manage_motd: true`
- `base_utils_motd_template: base_utils/motd.erb`
- `base_utils_utility_packages: []`

Migration note: Base defaults for all nodes when no OS-specific or higher-precedence override applies.

#### `site-modules/base_utils/data/os/Debian.yaml` — Debian OS-specific override

The following value is reported by the source plan and requires source-file verification:

- `base_utils::utility_packages`: `[vim, wget, curl, jq, dnsutils]` (type: array of strings)

Ansible mapping in `group_vars/Debian.yml`:

- `base_utils_utility_packages: [vim, wget, curl, jq, dnsutils]`

Migration note: Debian-family package override selected using `ansible_facts['os_family']`.

#### `site-modules/base_utils/data/os/RedHat.yaml` — RedHat OS-specific override

The following value is reported by the source plan and requires source-file verification:

- `base_utils::utility_packages`: `[vim-enhanced, wget, curl, jq, bind-utils]` (type: array of strings)

Ansible mapping in `group_vars/RedHat.yml`:

- `base_utils_utility_packages: [vim-enhanced, wget, curl, jq, bind-utils]`

Migration note: RedHat-family package override selected using `ansible_facts['os_family']`.

### Variable Migration Summary

- **Common defaults**: 3 variables from `common.yaml`, requiring source verification
- **OS-specific variables**: 1 overridden variable for Debian and 1 overridden variable for RedHat, requiring source verification
- **Environment-specific variables**: 0 supplied variables
- **Host-specific variables**: 0 supplied variables
- **Encrypted variables**: 0 supplied variables

### Cross-Level Overrides

- **`base_utils::utility_packages`**:
  - Defined in `common.yaml`, `Debian.yaml`, and `RedHat.yaml`
  - Structure: one common default plus OS-specific sibling overrides
  - Merge strategy: `first`
  - Reported effective Debian value: `[vim, wget, curl, jq, dnsutils]`
  - Reported effective RedHat value: `[vim-enhanced, wget, curl, jq, bind-utils]`
  - Reported effective fallback value: `[]`
  - All values require source-file verification.

No cross-level overrides were supplied for `base_utils::manage_motd` or `base_utils::motd_template`.

### Merge Strategy Notes

- Variables using `hash` merge: Hash values from multiple levels are merged shallowly.
- Variables using `deep` merge: Hash values are recursively merged.
- Variables using `first` merge: The first value found wins and no merging occurs.
- `base_utils::utility_packages` must replace the complete package list for an OS override; it must not be deep-merged.
- In Ansible, role defaults provide the common values and OS-family variables replace `base_utils_utility_packages` as a complete list.

## Custom Types and Providers

### Custom fact

- **`site-modules/base_utils/lib/facter/base_utils_info.rb`**
  - Reported behavior: Linux-only fact.
  - Checks availability of `curl`, `wget`, `jq`, and `vim` using `rpm` or `dpkg`.
  - Reads `/proc/uptime`.
  - Reports boolean package-availability values and `uptime_seconds`.
  - Is not referenced by resources shown in `site-modules/base_utils/manifests/init.pp`.
  - Behavior requires verification because the supplied structured execution analysis does not include this file.
  - Ansible options:
    - Implement `/etc/ansible/facts.d/base_utils_info.fact`.
    - Use `ansible.builtin.package_facts` and available uptime facts.

### Functions

- **`site-modules/base_utils/functions/ensure_value.pp`**
  - Reported behavior: returns `default_value` when `input` is undefined or exactly `''`; otherwise returns `input`.
  - Behavior requires verification.
  - Ansible equivalent: Jinja2 `default` with boolean handling where required, or a custom filter.

- **`site-modules/base_utils/functions/normalize_port.pp`**
  - Reported behavior: converts a string or integer to an integer and validates the result in the range `1..65535`.
  - Behavior requires verification.
  - Ansible equivalent: custom Jinja2 filter or explicit variable validation.

### Puppet type aliases

The following types are reported by the source plan and require verification:

- **`Base_utils::Ensure_value`**
  - Allowed values: `present`, `absent`, `installed`, `latest`, `purged`
  - Ansible equivalent: `assert` validation or documented variable choices.

- **`Base_utils::Log_level`**
  - Allowed values: `debug`, `info`, `notice`, `warning`, `error`, `critical`, `alert`, `emergency`
  - Ansible equivalent: variable validation.

- **`Base_utils::Port`**
  - Integer range: `1..65535`
  - Ansible equivalent: variable validation.

### Puppet Bolt plans

The following behaviors are reported by the source plan and require verification because they are not represented in the supplied execution-tree analysis:

- **`site-modules/base_utils/plans/health_check.pp`**
  - Reported default service: `sshd`
  - Reported action: runs `base_utils::check_service` against targets.
  - Reported result: identifies targets whose service status is not `running`.
  - Ansible equivalent: playbook using `ansible.builtin.service_facts`, result aggregation, and failure reporting.

- **`site-modules/base_utils/plans/rolling_restart.pp`**
  - Reported action: restarts a specified systemd service sequentially.
  - Reported default delay: `30` seconds.
  - Reported action: checks service health after each restart.
  - Ansible equivalent: `serial: 1`, `ansible.builtin.systemd`, service validation, and `ansible.builtin.pause`.

No custom Puppet resource providers are identified.

## Dependencies

**External module dependencies**:

- `puppetlabs-stdlib` `9.7.0`
- `puppetlabs-concat` `9.0.2`
- `puppetlabs-firewall` `8.1.3`
- `puppetlabs-vcsrepo` `6.1.0`
- `puppet-redis` `11.0.0`
- `puppet-systemd` `7.1.0`
- `puppetlabs-inifile` `6.1.1`
- `puppetlabs-apt` `9.4.0`

`base_utils` does not use an external module resource in the shown manifest. Its direct resources are Puppet `file` and `package` resources.

**System package dependencies**:

- Debian: `vim`, `wget`, `curl`, `jq`, `dnsutils`
- RedHat: `vim-enhanced`, `wget`, `curl`, `jq`, `bind-utils`

These package lists require verification against the Hiera source files.

**Service dependencies**:

- None for `base_utils`
- `chronyd` and `rsyslog` are managed separately by `profile::base::base`
- No service restart or daemon reload is associated with `base_utils`

## Puppet Facts Used

No Puppet facts are referenced directly in `site-modules/base_utils/manifests/init.pp`.

The wider execution context reportedly references:

- `$facts['kernel']`
  - Kernel name.
  - Used by `profile::base::base` for conditional NTP and syslog management.

- `$facts['os']['family']`
  - Operating-system family.
  - Relevant to selecting Debian or RedHat package data.

- `$facts['os']['name']`
  - Operating-system name.
  - Used by dependency modules outside `base_utils`.

- `$facts['environment']`
  - Referenced by unrelated application monitoring resources.
  - Its exact meaning must be verified; it must not be assumed to mean the Puppet environment.

- `$facts['puppet_environment']`
  - Referenced by unrelated HAProxy discovery according to the validation analysis.
  - Its use is outside the `base_utils` scope.

- `$facts['networking']['fqdn']`
  - Host fully qualified domain name.
  - Used by unrelated HAProxy discovery resources.

- `$facts['networking']['ip']`
  - Host IP address.
  - Used by unrelated HAProxy discovery resources.

The Ansible role should use `ansible_facts['os_family']` for package-list selection.

## Template Conversion Notes

### `base_utils/motd.erb`

- Destination: `/etc/motd`
- Reported render count: 1 when `base_utils::manage_motd` is true
- Manifest-supplied parameters: none
- Source file: not present in the supplied directory listing
- Template variables, conditionals, loops, and Ruby expressions: not established
- The supplied execution analysis shows the `/etc/motd` file resource but does not show a corresponding template node.
- Migration actions:
  - Locate and analyze the original template before implementation.
  - Add the template to structured template analysis with its reference and confirmed render count.
  - Convert ERB expressions to Jinja2.
  - Preserve rendered content exactly where possible.
  - Deploy with owner `root`, group `root`, and mode `0644`.

## Checks for the Migration

**Files to verify**:

- `site-modules/role/manifests/app_server.pp`
- `site-modules/profile/manifests/base/base.pp`
- `site-modules/base_utils/manifests/init.pp`
- `site-modules/base_utils/data/common.yaml`
- `site-modules/base_utils/data/os/Debian.yaml`
- `site-modules/base_utils/data/os/RedHat.yaml`
- `base_utils/motd.erb`
- `site-modules/base_utils/lib/facter/base_utils_info.rb`
- `site-modules/base_utils/functions/ensure_value.pp`
- `site-modules/base_utils/functions/normalize_port.pp`
- `site-modules/base_utils/types/ensure_value.pp`
- `site-modules/base_utils/types/log_level.pp`
- `site-modules/base_utils/types/port.pp`
- `site-modules/base_utils/plans/health_check.pp`
- `site-modules/base_utils/plans/rolling_restart.pp`

The wider 134-file repository inventory, including HAProxy, application-stack, PostgreSQL, Redis, APT, systemd, and unrelated templates, is deferred to separate migration plans.

**Service endpoints to check**:

- None managed by `base_utils`
- No ports or sockets are configured by this module

**Templates rendered**:

- `base_utils/motd.erb` → `/etc/motd`
  - Reported render count: 1 when MOTD management is enabled
  - Render count requires confirmation in structured template analysis

**Resource-count scope**:

- Resource-count validation is limited to the `base_utils` branch.
- The visible branch contains one conditional MOTD file resource and one package-loop branch.
- Resource counts for the remaining analyzed manifests are deferred.

## Pre-flight checks

```bash
# Confirm operating-system family
ansible localhost -m ansible.builtin.setup -a 'filter=ansible_facts.os_family'

# Confirm the source Hiera files and reported values
test -f site-modules/base_utils/data/common.yaml
test -f site-modules/base_utils/data/os/Debian.yaml
test -f site-modules/base_utils/data/os/RedHat.yaml

# Confirm the MOTD template exists before migration
test -f base_utils/motd.erb

# Validate Debian package availability individually
ansible debian_hosts -m ansible.builtin.package -a 'name=vim state=present' --check
ansible debian_hosts -m ansible.builtin.package -a 'name=wget state=present' --check
ansible debian_hosts -m ansible.builtin.package -a 'name=curl state=present' --check
ansible debian_hosts -m ansible.builtin.package -a 'name=jq state=present' --check
ansible debian_hosts -m ansible.builtin.package -a 'name=dnsutils state=present' --check

# Validate RedHat package availability individually
ansible redhat_hosts -m ansible.builtin.package -a 'name=vim-enhanced state=present' --check
ansible redhat_hosts -m ansible.builtin.package -a 'name=wget state=present' --check
ansible redhat_hosts -m ansible.builtin.package -a 'name=curl state=present' --check
ansible redhat_hosts -m ansible.builtin.package -a 'name=jq state=present' --check
ansible redhat_hosts -m ansible.builtin.package -a 'name=bind-utils state=present' --check

# Run the role in check mode
ansible-playbook -i inventory site.yml --check --diff

# Verify the MOTD instance when management is enabled
ansible all -m ansible.builtin.stat -a 'path=/etc/motd'

# Verify MOTD ownership, group, and mode individually
ansible all -m ansible.builtin.shell -a "stat -c '%U' /etc/motd"
ansible all -m ansible.builtin.shell -a "stat -c '%G' /etc/motd"
ansible all -m ansible.builtin.shell -a "stat -c '%a' /etc/motd"

# Confirm no base_utils service restart is attempted
ansible-playbook -i inventory site.yml --check --diff | grep -E 'restart|reload' || true

# Confirm no base_utils endpoints are configured
ansible all -m ansible.builtin.shell -a 'ss -ltnup'
```

No credentials or encrypted values are referenced by the supplied `base_utils` data. Wider credential-capable parameters belong to deferred application, HAProxy, Redis, APT, concat, and systemd migrations.