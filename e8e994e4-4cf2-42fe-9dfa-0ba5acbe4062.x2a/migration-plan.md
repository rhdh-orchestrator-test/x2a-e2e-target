# MIGRATION FROM CHEF-RELATED EXAMPLES TO ANSIBLE

## Executive Summary

This repository is primarily an Ansible and Chef ecosystem example, not a repository of Chef cookbooks. The supplied tree contains two Ansible playbooks under `chef-and-ansible/`, Chef InSpec verification controls, Test Kitchen/Vagrant configuration, and Bash scripts that bootstrap Chef Automate and Chef Infra Server. It contains no directories with the required Chef cookbook entrypoint `recipes/default.rb`, no Puppet module entrypoint `manifests/init.pp`, and no PowerShell module manifest ending in `.psd1`.

Consequently, there is no one-to-one Chef cookbook migration inventory. The main migration work is to harden and operationalize the existing Ansible HTTPS example, preserve or modernize its compliance tests, and decide whether the Chef server/Automate bootstrap scripts should be retired, retained as legacy tooling, or replaced by a separately designed Ansible platform implementation. The HTTPS work is low-to-moderate complexity and can be completed in approximately 1–2 weeks. Replacing the Chef platform bootstrap and its identity/key lifecycle is a separate moderate-to-high complexity effort, estimated at 2–4 additional weeks after requirements and target platform decisions.

## Module Migration Plan

The repository contains Ansible playbooks and Chef-related support files, but no source modules matching the requested module markers.

### MODULE INVENTORY

**No modules discovered.**

The repository was searched for all required module entrypoint patterns:

- `**/recipes/default.rb` — no Chef cookbooks found.
- `**/manifests/init.pp` — no Puppet modules found.
- `**/*.psd1` — no PowerShell module manifests found.

Therefore, there are no module paths to list in this inventory. In particular, `chef-and-ansible/website_https.yml`, `chef-and-ansible/poodle_fix.yml`, and the scripts under `setup-automate/` are files and are not modules/cookbooks. They are covered below as migration work items rather than module inventory entries.

**CRITICAL PATH VERIFICATION:**
Every path named as a module would need to be a real directory containing one of the required marker files. Because the searches returned no matches, this plan intentionally lists no module paths and does not invent cookbook directories.

### Infrastructure Files

- `README.md`: Repository description identifying the project as Chef-related examples. No deployable module content.
- `chef-and-ansible/README.md`: Explains that the example uses Chef InSpec with Ansible for continuous compliance.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration using Vagrant, the Ansible provisioner, Ubuntu 20.04, and InSpec verification.
- `chef-and-ansible/website_https.yml`: Existing Ansible playbook that installs Apache and TLS dependencies, creates a self-signed certificate, configures an HTTPS virtual host, deploys sample content, enables Apache SSL, and restarts services.
- `chef-and-ansible/poodle_fix.yml`: Existing Ansible playbook that changes Apache's SSL protocol configuration to TLS 1.2 and restarts Apache and SSH.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec acceptance checks for port 443, HTTPS response/content, SSLv3 disabled, and TLS 1.2 enabled.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec control for disabling SSH root login, with an alternative that considers absence of the OpenSSH server compliant.
- `chef-and-ansible/index.html`: Static sample website content. The HTTPS playbook currently embeds similar content inline instead of copying this file.
- `setup-automate/deploy-automate.sh`: Bash bootstrap for Chef Automate plus Chef Infra Server, including user, organization, and PEM key creation.
- `setup-automate/deploy-chef-server.sh`: Bash bootstrap for Chef Infra Server, including user, organization, and PEM key creation.

### Target Details

- **Operating System**: Ubuntu 20.04 is explicitly specified in `kitchen.yml`. The playbooks use Ubuntu/Debian `apt`, Apache paths under `/etc/apache2`, and `a2*` commands. The RHEL 8 STIG identifiers in the SSH InSpec file are control metadata, not evidence that RHEL is the deployment target. Confirm the supported Ubuntu LTS before implementation.
- **Virtual Machine Technology**: Vagrant is the explicitly configured Test Kitchen driver. Production virtualization is not specified.
- **Cloud Platform**: Not specified. The bootstrap comments mention on-premises or cloud VMs, but no AWS, Azure, GCP, or provider-specific resources are present.

## Migration Approach

1. Confirm that the supplied repository is the complete migration scope. Since no cookbook markers exist, check whether cookbooks are maintained in another repository, branch, or dependency source.
2. Treat `website_https.yml` as an existing Ansible baseline, not as a Chef recipe conversion. Refactor it into an Apache HTTPS role with separate tasks for packages, certificates, virtual hosts, content, and handlers.
3. Move inline variables and content into role defaults/vars and Jinja templates. Parameterize hostname, Apache version, certificate source, virtual-host name, and web content.
4. Replace shell-oriented `a2ensite`, `a2dissite`, and `a2enmod` operations with idempotent modules or guarded commands. Add Apache configuration validation before reload/restart.
5. Consolidate the TLS behavior from `poodle_fix.yml` into the HTTPS role or make it a distinct, versioned hardening role. Avoid fragile replacement of an existing directive where a managed configuration fragment is safer.
6. Retain InSpec as an acceptance gate during transition. Add Molecule or equivalent Ansible role testing if the playbook becomes a reusable role.
7. Make an explicit decision about Chef Automate/Infra Server. Retain the scripts only as separately owned legacy tooling, or design and implement an approved Ansible-managed replacement; do not mechanically translate product bootstrap commands without defining the target control plane.

### Key Dependencies to Address

- **Ubuntu 20.04 and `apt`**: Preserve initially, but confirm lifecycle/support status and define package update policy. The Apache package is pinned in the example, so the security and repository implications of that pin must be agreed.
- **Apache HTTP Server**: Manage installation, modules, virtual host, configuration validation, and service state with Ansible.
- **OpenSSL and Ansible crypto modules**: Use supported fully qualified `community.crypto` modules and provide the required Python cryptography/OpenSSL dependencies in the execution environment.
- **Chef InSpec**: Preserve the existing HTTPS and SSH compliance intent during transition; later decide whether to keep InSpec or add equivalent Molecule checks.
- **Vagrant/Test Kitchen**: Retain as a reproducible test harness or migrate to Molecule and a maintained Ubuntu image.
- **Chef Automate/Infra Server CLI**: The scripts download the latest CLI from `packages.chef.io` without a version or checksum. If retained, pin and verify a supported release and document product prerequisites.

### Security Considerations

- **Plaintext password**: Both bootstrap scripts define `userpassword='password'`. Treat this as exposed, remove it, rotate any corresponding credential, and use Ansible Vault, an external secrets manager, or protected CI variables.
- **Chef PEM credentials**: User and organization PEM files are generated locally. Restrict permissions, prevent repository/CI exposure, define rotation and revocation, and securely remove temporary copies.
- **TLS private key**: The HTTPS playbook generates `/etc/apache2/certs/apache.key`. Protect it with restrictive ownership and mode. The certificate directory is created with mode `0640`, which should be reviewed because directory traversal requires execute permission.
- **Self-signed certificate**: Appropriate for a lab example but not normally for production. Define CA issuance, SAN/hostname requirements, renewal, and secret distribution before production use.
- **TLS policy**: Tests require SSLv3 disabled and TLS 1.2 enabled, while the playbook does not establish a complete modern cipher/TLS policy. Validate TLS 1.2/1.3 requirements and effective Apache configuration.
- **SSH and privilege**: The playbooks run as `root` while also enabling `become`, and they restart SSH without configuring `PermitRootLogin`. Use a controlled automation account, explicit sudo policy, and a tested SSH hardening task with rollback access.
- **Remote artifact download**: The bootstrap scripts pipe a remote latest-version download into `gunzip`. Pin versions, verify signatures/checksums, quote shell variables, and use a controlled artifact source.

### Technical Challenges

- **No source cookbooks**: There is no Chef recipe/resource behavior to translate. Missing external repositories or branches would materially change the migration scope.
- **Ansible idempotence**: Raw `command` tasks may not be idempotent and can produce unsafe repeated changes. Refactor them and use handlers only after successful configuration validation.
- **Ubuntu-specific implementation**: Porting to RHEL or another OS requires different package names, paths, service names, and Apache module management.
- **Certificate lifecycle**: Replacing self-signed lab certificates with production certificates requires coordination with security, PKI, and operations teams.
- **Test mismatch**: The SSH control references RHEL 8 STIG IDs while the configured test platform is Ubuntu 20.04. Align controls with the approved OS baseline; clarify whether a missing OpenSSH package should really be considered compliant.
- **Sample content defect**: The inline web content contains a malformed closing title tag. Use the repository's `index.html` or a validated template and align the expected InSpec content.
- **Chef platform scope**: The bootstrap scripts omit HA, backup, upgrade, firewall, persistence, and recovery design. Replacing Chef Automate/Infra Server is a platform project, not a simple playbook conversion.

### Migration Order

1. Confirm repository scope and document that no Chef/Puppet/PowerShell modules were found.
2. Refactor and test the Apache HTTPS playbook as an Ansible role on Ubuntu 20.04.
3. Integrate the TLS hardening behavior and correct certificate/file permissions.
4. Preserve InSpec acceptance tests while adding role-level CI/Molecule coverage and align the SSH control with the target OS.
5. Decide whether Chef Automate and Chef Infra Server remain. If retained, secure and parameterize their bootstrap separately; if retired, implement the approved replacement with identity, key rotation, backup, and upgrade procedures.
6. Pilot in disposable Vagrant/CI hosts, then non-production, then production with rollback and certificate-renewal runbooks.

### Assumptions

- The supplied repository tree is complete for this task.
- No external Chef cookbook repository, branch, submodule, or dependency source is in scope.
- Ubuntu 20.04 is the initial target because it is explicitly declared in `kitchen.yml`.
- Vagrant is a test driver, not necessarily the production VM platform.
- Self-signed certificates are intended for testing only.
- The literal bootstrap password may have been used elsewhere and should be treated as compromised.
- No cloud platform, production inventory, CI system, PKI, secrets manager, HA requirement, or network topology was provided.
- The Chef product versions are unspecified because the scripts download `latest`; compatibility and support must be established before reuse.
- The InSpec files are compliance tests and not Chef cookbooks or modules.
- The migration estimate excludes discovery of missing repositories and a full Chef platform replacement program.

## Coordination Guidance

Assign an Ansible owner for the role and collection versions, a web/platform owner for Apache behavior, a security owner for TLS/SSH and credential rotation, and a Chef platform owner for the Automate/Infra Server disposition. Track scope confirmation, HTTPS role refactoring, test migration, secret remediation, target OS approval, and Chef platform replacement as separate work items. Require CI and disposable-host acceptance tests, peer review for privileged tasks, artifact verification, and a documented rollback procedure before rollout.
