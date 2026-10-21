# MIGRATION FROM MIXED ANSIBLE/CHEF AUTOMATION TO ANSIBLE

This repository is primarily an Ansible example project, not a conventional Chef cookbook repository. It contains two Ansible playbooks for an Ubuntu Apache HTTPS example, Chef InSpec verification controls, and Bash scripts that install and bootstrap Chef Infra Server/Chef Automate. There are no discovered Chef cookbooks (`recipes/default.rb`), Puppet modules (`manifests/init.pp`), PowerShell module manifests, Berksfiles, Policyfiles, or Chef cookbook metadata files.

The Ansible migration is therefore a consolidation and hardening effort rather than a direct cookbook-to-playbook rewrite. The web-server automation is already close to an Ansible target, while the Chef platform deployment scripts require a decision: retire them as part of the Chef-to-Ansible migration, or preserve them as a separately managed legacy/bootstrap capability. A small proof of concept should take approximately 1–2 weeks; a production-ready migration with validation, secret redesign, platform decisions, and team rollout is more realistically 3–6 weeks.

## Module Migration Plan

This repository contains Ansible playbooks, shell-based Chef platform bootstrap scripts, and InSpec tests that need individual migration planning. No reusable Chef cookbook modules were identified.

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only paths present in the supplied repository tree or confirmed by repository searches are listed below.

- **website_https**:
    - Description: An Ansible playbook for provisioning a pinned Apache 2.4 package, creating a Hello World site, generating a local private key/CSR/self-signed certificate, configuring an HTTPS virtual host, enabling SSL, and restarting services.
    - Path: `chef-and-ansible/website_https.yml`
    - Technology: Ansible YAML playbook
    - Key Features: Ubuntu apt package installation, Apache virtual-host configuration, OpenSSL key/CSR/certificate generation, static content deployment, site/module activation, service handlers
    - Migration Complexity: Low to moderate; it is already Ansible but needs role structure, idempotence improvements, platform validation, and TLS/secret policy changes.

- **poodle_fix**:
    - Description: An Ansible remediation playbook intended to restrict Apache SSL protocols to TLS 1.2 and restart Apache and SSH after the configuration change.
    - Path: `chef-and-ansible/poodle_fix.yml`
    - Technology: Ansible YAML playbook
    - Key Features: Apache SSL configuration replacement, TLS protocol hardening, service notifications
    - Migration Complexity: Low, but the notification name does not match the declared Apache handler (`Restart apache2` versus `Restart apache`), so the playbook requires functional correction before reuse.

- **chef_platform_bootstrap**:
    - Description: Bash automation that downloads Chef Automate CLI, deploys Chef Automate plus Chef Infra Server, sets kernel parameters and hostname, and creates a Chef user and organization.
    - Path: `setup-automate/deploy-automate.sh`
    - Technology: Bash and Chef Automate/Chef Infra Server CLI
    - Key Features: On-premises/cloud VM bootstrap, Chef platform deployment, user and organization creation, PEM key generation
    - Migration Complexity: High if Chef is to be retired; the deployment must be replaced with an approved Ansible-managed platform or removed. Medium if retained as an explicitly isolated legacy bootstrap component.

- **chef_server_bootstrap**:
    - Description: Bash automation for deploying Chef Infra Server without Automate, setting host/kernel parameters, and creating the initial Chef user and organization.
    - Path: `setup-automate/deploy-chef-server.sh`
    - Technology: Bash and Chef Infra Server CLI
    - Key Features: Chef server deployment, initial account/org provisioning, generated user and validator PEM files
    - Migration Complexity: High if replacing Chef Infra Server; otherwise it should be documented as out-of-scope legacy infrastructure and protected from accidental execution.

- **ssh_profile**:
    - Description: Chef InSpec compliance control that verifies SSH root login is disabled, with a fallback assertion concerning the OpenSSH package.
    - Path: `chef-and-ansible/tests/ssh_profile.rb`
    - Technology: Chef InSpec/Ruby
    - Key Features: `PermitRootLogin` compliance check, STIG/CAT I metadata
    - Migration Complexity: Low; retain as InSpec validation or translate the policy into Ansible Molecule/testinfra/Ansible assertions. Note that this control is not currently referenced by `kitchen.yml`.

- **website_https_verify**:
    - Description: Chef InSpec verification for HTTPS availability, expected Hello World content, disabled SSLv3, and enabled TLS 1.2.
    - Path: `chef-and-ansible/tests/website_https_verify.rb`
    - Technology: Chef InSpec/Ruby
    - Key Features: Port 443 listening check, HTTPS response/content check, protocol checks
    - Migration Complexity: Low; it can remain a black-box compliance test during transition and later move to Molecule/testinfra or an external security test suite.

### Infrastructure Files

- `README.md`: Repository-level description of Chef examples; update to state the supported Ansible target, lifecycle, and what remains legacy.
- `chef-and-ansible/README.md`: Describes the InSpec-with-Ansible compliance example; expand with supported OS, execution instructions, role variables, and security warnings.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration using the Vagrant driver, Ansible playbook provisioner, Ubuntu 20.04, and InSpec verifier. Replace or supplement Kitchen with Ansible-native Molecule if the project is being standardized.
- `chef-and-ansible/tests/`: InSpec test suite used for acceptance/compliance validation. Keep as a transition gate or port to the selected Ansible testing framework.
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server bootstrap; requires an explicit retirement, replacement, or exception decision.
- `setup-automate/deploy-chef-server.sh`: Chef Infra Server-only bootstrap; same platform lifecycle decision applies.

### Target Details

- **Operating System:** The test configuration explicitly targets Ubuntu 20.04. The playbooks use `apt`, `/etc/apache2`, `a2ensite`, and `a2enmod`, so Debian/Ubuntu is the demonstrated target family. The InSpec SSH control contains RHEL 8 STIG identifiers, but that is compliance metadata rather than proof that RHEL is the provisioning target. Do not default this implementation to RHEL 9 without a separate Apache layout/package validation effort.
- **Virtual Machine Technology:** Vagrant is specified in `kitchen.yml`; the underlying Vagrant provider is not specified.
- **Cloud Platform:** Not specified. The Chef bootstrap comments allow on-premises or cloud VMs, but no AWS, Azure, or GCP implementation is present.

## Migration Approach

First establish whether the goal is only to standardize the existing Apache automation or also to eliminate Chef Automate/Infra Server. Refactor the web configuration into an Ansible role with variables for Apache package/version, server name, document root, certificate source, TLS policy, and service name. Use `ansible.builtin.apt`, `template`, `copy`, `file`, `community.crypto` modules, and `ansible.builtin.service`; replace shell commands such as `a2ensite`/`a2enmod` with idempotent modules where practical. Add a supported inventory and CI test matrix before changing production hosts.

For the Chef platform scripts, inventory any existing Chef organizations, nodes, cookbooks, keys, Automate data, and integrations. If Chef is being retired, migrate the managed node configuration—not Chef Server itself—into Ansible inventories, roles, and Vault-backed variables, and define a separate replacement for dashboards/compliance reporting. If Chef Server must remain, isolate these scripts from the Ansible project, pin the CLI artifact, and manage them through an approved bootstrap pipeline rather than treating them as Ansible modules.

### Key Dependencies to Address

- **Ansible latest / Ansible Playbook provisioner:** Pin a tested `ansible-core` version and collection versions in a requirements file; avoid `latest` in repeatable CI.
- **Vagrant and its provider:** Retain for local testing only, document the provider, or replace with Molecule drivers suitable for CI.
- **Ubuntu 20.04 and apt:** Confirm lifecycle support and decide whether the target should move to a currently supported Ubuntu LTS. Validate Apache package availability before retaining the exact `2.4.41-4ubuntu3.10` pin.
- **Apache HTTP Server and OpenSSL:** Use distribution packages or approved repositories; model TLS policy centrally and test it against the actual Apache/OpenSSL version.
- **`community.crypto` functionality / PyOpenSSL:** Install and pin the required Ansible collection and Python dependencies. Prefer the current supported crypto modules over unqualified legacy module names.
- **Chef Automate CLI and Chef Infra Server:** Either remove as retired dependencies or pin and obtain them from a trusted, approved artifact source. Ansible does not provide a drop-in replacement for Chef Automate.
- **Chef InSpec:** Keep during transition for acceptance/compliance checks, or migrate checks to Molecule/testinfra while preserving equivalent evidence and control IDs.

### Security Considerations

- **Hardcoded credentials:** Both Chef bootstrap scripts contain a plaintext `userpassword='password'`, user identity data, organization data, and a hostname. Remove these values from source immediately; use Ansible Vault or an enterprise secret manager, rotate any exposed credentials, and use short-lived/bootstrap credentials where possible.
- **Generated private keys:** The scripts generate user and organization PEM files locally. Define protected storage, file permissions, backup, rotation, revocation, and transfer procedures. Do not commit generated keys or leave them in working directories.
- **Unsafe download/execution:** The scripts pipe a live download from `packages.chef.io` into `gunzip` and execute the resulting binary without a checksum/signature verification or version pin. Replace with a verified, pinned artifact and controlled repository.
- **TLS certificates:** The web playbook creates a self-signed certificate and stores a private key under `/etc/apache2/certs`. Self-signed certificates are appropriate only for a lab; production should use an enterprise CA or approved ACME flow, with private keys supplied through protected secret handling. Review certificate and directory permissions—the directory mode `0640` is not a conventional searchable directory permission.
- **TLS protocol policy:** `poodle_fix.yml` disables legacy protocols only by replacing a single configuration line and explicitly enables TLS 1.2. Define a complete supported TLS policy, include modern TLS where supported, test cipher suites, and avoid relying on a fragile regex.
- **SSH service changes:** The playbooks restart SSH unnecessarily during web/TLS changes, creating availability risk. The InSpec control should be implemented as an Ansible hardening role with safe validation and rollback, not inferred from package absence.
- **Privilege and access:** Playbooks run as `root` with `become: yes`. Use least privilege where feasible, controlled deployment identities, host-key verification, and audited CI credentials.
- **Application content:** The example site is intentionally static, but validate ownership, modes, and Apache directory restrictions before adapting it to real content.

### Technical Challenges

- **Mixed technology boundaries:** The repository does not contain Chef cookbooks to translate; it mixes already-Ansible playbooks, InSpec tests, and Chef platform shell installers. Establish scope and ownership before implementation.
- **Non-idempotent commands:** `a2dissite`, `a2ensite`, and `a2enmod` are invoked with `command`; repeated runs may report changes or fail in unexpected states. Replace with idempotent abstractions or guarded commands and verify enabled-site state.
- **Handler correctness:** `poodle_fix.yml` notifies a handler name that is not declared. Add automated playbook syntax/lint and acceptance tests to catch this class of defect.
- **Platform drift:** The configuration is Ubuntu-specific, while compliance tags reference RHEL 8. Choose an OS support matrix and implement separate platform defaults only if both families are required.
- **Chef platform replacement:** Automate/Infra Server contains state, identities, keys, policy history, and possibly compliance data. Migration requires discovery and export planning, not merely rewriting shell commands as Ansible tasks.
- **Testing gap:** `ssh_profile.rb` is present but not referenced in the Kitchen suite. Add it to the intended test run or explicitly track it as a separate compliance profile. Validate HTTPS using a real certificate policy rather than `ssl_verify: false` for production-like tests.
- **Configuration quality:** The inline HTML has a malformed closing title tag, and TLS/site activation assumptions are not parameterized. Move content and Apache configuration to templates with validation and handler notifications.

### Migration Order

1. **Baseline and decisions:** Inventory Chef platform usage, rotate exposed credentials, define supported OS/provider, and freeze the current acceptance criteria.
2. **`website_https` refactor:** Convert the existing playbook into a reusable Apache HTTPS role, parameterize host/site/certificate settings, fix permissions and idempotence, and pin dependencies.
3. **`poodle_fix` hardening:** Merge its TLS policy into the Apache role where appropriate, correct handler names, and add protocol/configuration regression tests.
4. **Compliance validation:** Run the InSpec profiles in CI, add the SSH profile to the test plan, and decide whether InSpec remains the compliance verifier or is ported to Ansible-native testing.
5. **Chef platform disposition:** If retiring Chef, migrate node responsibilities and integrations, then decommission Chef Server/Automate after a controlled parallel run. If retaining it, isolate and secure the bootstrap scripts rather than embedding them in the Ansible role set.
6. **Operational rollout:** Pilot on disposable Vagrant hosts, then staging, then production with rollback instructions, ownership handoff, documentation, and monitoring.

### Assumptions

- The supplied tree is complete; no hidden cookbooks, roles, inventories, Berksfiles, Policyfiles, metadata, or secret stores were identified.
- The two YAML files are the only configuration automation for the Apache example and are already intended to run with Ansible.
- Ubuntu 20.04 is the demonstrated target, although its support status and production suitability must be confirmed.
- Vagrant is used for local testing; the actual production virtualization/cloud provider is unknown.
- `myhost` is an inventory host alias and is not a confirmed DNS name or production hostname.
- The self-signed certificate and Hello World site are lab examples, not production certificate/content requirements.
- The Chef bootstrap scripts may be examples rather than currently deployed infrastructure; their execution status and retained Chef data are unknown.
- No Chef cookbook metadata or external cookbook dependencies exist in this repository; dependencies listed above are inferred from the files actually reviewed.
- The exact Ansible version, collection versions, Vagrant provider, and Python runtime are not pinned by the repository.
- It is unknown whether Apache is expected to serve additional sites, whether certificates are externally issued, or whether IPv6, firewall, SELinux/AppArmor, logging, monitoring, and backup requirements exist.
- The InSpec SSH control's RHEL/STIG references do not establish a RHEL target and need policy-owner confirmation.
- Any credentials, PEM files, or Chef organization data already generated outside the repository require separate incident/rotation and migration handling.
- Team coordination should assign owners for the Apache role, security/compliance controls, Chef platform disposition, test/CI pipeline, secrets management, and production release approval; migration should not proceed on filename inference alone.
