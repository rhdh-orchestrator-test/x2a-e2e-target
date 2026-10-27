# MIGRATION FROM CHEF EXAMPLES TO ANSIBLE

## Executive Summary

The repository is a small Chef-related demonstration repository, not a Chef cookbook collection. The content under `chef-and-ansible/` is already Ansible-based, with Chef InSpec used for verification. The `setup-automate/` directory contains Bash bootstrap scripts for Chef Automate and Chef Infra Server.

Repository verification found **zero qualifying Chef cookbooks**: no `recipes/default.rb`, `metadata.rb`, `Berksfile`, or `Policyfile.rb` files exist. It also found no Puppet `manifests/init.pp` files and no PowerShell `.psd1` module manifests. Consequently, there are no cookbook/module entries to mechanically translate into Ansible. The migration is instead a small Ansible standardization, security remediation, testing, and possible Chef control-plane replacement effort.

For the existing host configuration examples, estimate 1–2 weeks for one small team, including refactoring and tests. Add approximately 1–2 weeks if replacing or operationalizing the Chef Automate/Infra Server bootstrap is in scope. Production use requires additional decisions about certificates, secrets, supported Ubuntu versions, and the target Ansible control plane.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests, but no qualifying Chef cookbooks or Puppet/PowerShell modules.

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**

The required module-entrypoint searches were performed against the repository:

- `**/recipes/default.rb`: no files found; therefore there are no Chef cookbooks to list.
- `**/manifests/init.pp`: no files found; therefore there are no Puppet modules to list.
- `**/*.psd1`: no files found; therefore there are no PowerShell modules to list.

Accordingly, the MODULE INVENTORY is intentionally empty. No invented cookbook/module paths are included. The following are existing **directories** confirmed in the repository tree, but neither is a qualifying module directory:

- `chef-and-ansible/` — contains already-Ansible playbooks, Test Kitchen configuration, and InSpec tests.
- `setup-automate/` — contains Bash scripts for bootstrapping Chef services.

The following implementation units are documented below for migration planning, but are not listed as modules because their paths are files and they do not contain a required cookbook/module entrypoint:

- `chef-and-ansible/website_https.yml`: Ansible playbook for Ubuntu Apache HTTPS, a self-signed certificate, a virtual host, and a Hello World site.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that restricts Apache SSL protocols to TLS 1.2 and notifies service handlers.
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec checks for port 443, HTTPS response/content, disabled SSLv3, and enabled TLS 1.2.
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec control checking that SSH root login is disabled, with RHEL 8 STIG/SRG metadata.

### Infrastructure Files

- `README.md`: Describes the repository as Chef examples. Update it to accurately explain the Ansible/InSpec demonstration and migration scope.
- `chef-and-ansible/README.md`: Describes using Chef InSpec alongside Ansible for continuous compliance. Retain as context, but document the target Ansible workflow.
- `chef-and-ansible/kitchen.yml`: Uses Vagrant, the Ansible playbook provisioner, Ubuntu 20.04, and the InSpec verifier. It is the primary test-environment definition.
- `setup-automate/deploy-automate.sh`: Bash bootstrap for Chef Automate plus Chef Infra Server; creates a Chef user, organization, and PEM files.
- `setup-automate/deploy-chef-server.sh`: Bash bootstrap for Chef Infra Server only; creates a Chef user, organization, and PEM files.

## Target Details

- **Operating System:** Ubuntu 20.04 is explicitly configured in `chef-and-ansible/kitchen.yml`. The playbooks use `apt`, `/etc/apache2`, `a2ensite`, and `a2enmod`, confirming Debian/Ubuntu assumptions. RHEL 8 references in the InSpec control are compliance identifiers, not deployment evidence.
- **Virtual Machine Technology:** Vagrant is the local test driver. Production VM technology is not specified.
- **Cloud Platform:** Not specified. The bootstrap comments allow on-premises or cloud VMs but contain no AWS, Azure, or GCP-specific implementation.

## Migration Approach

### Key Dependencies to Address

- **Ansible and ansible-core:** Keep the current Ansible approach, select and pin a supported version, and use fully qualified module names.
- **Ubuntu/apt and Apache:** Convert the playbooks into an `apache_https` role with variables, templates, handlers, tags, and explicit package policy. The Apache package is pinned to `2.4.41-4ubuntu3.10`; verify availability and security, or make the version configurable.
- **OpenSSL modules:** The HTTPS playbook uses private-key, CSR, and certificate modules. Declare and pin the `community.crypto` collection, and test certificate generation on the selected Ansible version.
- **Vagrant/Test Kitchen:** Vagrant/Test Kitchen can remain for compatibility, but Molecule is recommended for role convergence and idempotence testing.
- **Chef InSpec:** Retain during transition if compliance evidence is required. Alternatively, supplement it with Ansible assertions, `ansible.builtin.uri`, package/service checks, and external TLS scanners.
- **Chef Automate/Infra Server CLI:** The scripts download the latest Chef Automate CLI and invoke Chef server commands. If retained, pin a release and verify downloads. If the objective is Chef removal, replace this separate control-plane function with Ansible Automation Platform/AWX or the organization’s approved automation service.

### Security Considerations

- **Hardcoded credentials:** Both deployment scripts contain a literal password and user identity values. Remove them, rotate any exposed credentials, and use Ansible Vault, a secrets manager, or protected CI variables.
- **PEM credentials:** User and organization PEM files are generated by the bootstrap scripts. Protect them with restrictive permissions, controlled storage, rotation/revocation procedures, and no source-control commits.
- **Unsafe CLI download:** The scripts pipe a remote `curl` response into `gunzip` and use an unpinned latest artifact. Replace with a pinned, checksum-verified artifact from a trusted repository.
- **Private TLS key:** `website_https.yml` creates `/etc/apache2/certs/apache.key`. Use restrictive key ownership/mode, protect backups, and use an approved CA or ACME process for production instead of a self-signed certificate.
- **Certificate directory mode:** The configured directory mode `0640` is inappropriate for normal directory traversal. Define directory, certificate, and private-key permissions separately.
- **TLS policy:** The examples disable SSLv3 and enable TLS 1.2, but do not establish a complete current cipher/TLS 1.3 policy. Define and externally test an approved baseline.
- **SSH changes:** Do not restart SSH as a side effect of Apache TLS changes. Implement SSH hardening separately, validate configuration before restart, and preserve rollback access.
- **Privilege:** The playbooks use `remote_user: root` and `become: yes`. Replace with controlled administrative access and least privilege where feasible.

### Technical Challenges

- **No cookbook source to translate:** There are no Chef recipes or cookbook metadata. Confirm that this repository is the complete migration scope before declaring the Chef migration complete.
- **Already-Ansible implementation:** The work is refactoring rather than Chef-to-Ansible conversion. Avoid creating duplicate roles or claiming the existing playbooks are migrated cookbooks.
- **Idempotence:** `a2ensite`, `a2dissite`, raw `command`, and replacement operations need guards or purpose-built modules. Add convergence and second-run idempotence tests.
- **Configuration ownership:** `website_https.yml` owns the virtual host while `poodle_fix.yml` owns a related SSL setting. Consolidate ownership and ensure one controlled Apache reload/restart.
- **Certificate lifecycle:** Self-signed certificates are acceptable for a lab but require CA issuance, renewal, deployment, and safe reload design in production.
- **Test coverage:** InSpec validates outcomes but does not fully test idempotence, Apache syntax, or recovery. Add Molecule/CI checks and `apachectl configtest` validation.
- **Control-plane scope:** Replacing Chef Automate/Infra Server is a larger platform migration than the web-server examples. It requires an explicit decision, ownership model, data migration plan, and rollback plan.

### Migration Order

1. Confirm repository scope and verify whether external Chef cookbooks exist elsewhere.
2. Remove/rotate hardcoded credentials and secure the Chef bootstrap artifacts.
3. Establish supported Ansible, collection, Ubuntu, and Apache versions.
4. Refactor `website_https.yml` into a reusable Apache HTTPS role with templates, variables, certificate handling, and idempotent site/module management.
5. Merge or explicitly sequence `poodle_fix.yml` with the Apache role and implement the approved TLS baseline.
6. Implement SSH hardening independently and preserve the InSpec compliance control or replace it with equivalent tested checks.
7. Add Molecule/CI, configuration syntax checks, TLS acceptance tests, documentation, and rollback runbooks.
8. Decide whether `setup-automate` is retained, retired, or replaced by an Ansible control plane; execute that as a separate workstream.

### Assumptions

- The supplied repository tree is complete for this assessment.
- The absence of all three required entrypoint patterns means there are no qualifying Chef, Puppet, or PowerShell modules in this repository.
- `chef-and-ansible/website_https.yml` and `poodle_fix.yml` are already Ansible assets, not Chef cookbooks.
- The repository is a demonstration project rather than the complete production Chef estate.
- Ubuntu 20.04 and Vagrant describe the test target, not necessarily the production platform.
- The self-signed certificate and Hello World content are lab examples.
- InSpec may remain during a transition for compliance evidence.
- Credentials visible in the shell scripts must be treated as exposed until rotated.
- The desired future state of Chef Automate and Chef Infra Server is not specified.
- Production inventory, CA, secrets manager, CI system, Ansible control plane, and ownership boundaries must be supplied by the migration team.
