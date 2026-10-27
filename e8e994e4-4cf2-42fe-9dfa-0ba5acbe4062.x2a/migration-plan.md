# MIGRATION FROM CHEF-BASED AUTOMATION AND AD HOC ANSIBLE TO ANSIBLE

## Executive Summary

This repository is a small Chef example repository, but the infrastructure configuration under review is not implemented as Chef cookbooks. The `chef-and-ansible` directory contains two Ansible playbooks, Molecule/Test Kitchen-style execution metadata, and Chef InSpec verification tests. The `setup-automate` directory contains shell scripts that bootstrap Chef Automate or Chef Infra Server. No Chef cookbook entrypoints (`recipes/default.rb`), `metadata.rb`, Berksfile, Policyfile, Chef recipes, Puppet manifests, Salt states, or PowerShell modules were found.

The migration is therefore primarily a hardening and productionization exercise: preserve the existing Apache HTTPS demonstration in a maintainable Ansible role/playbook, replace shell-driven Chef server bootstrap if Chef is being retired, and retain or port the compliance checks. The demonstrated application stack is small and should require approximately 3–5 engineering days for a controlled proof of concept, or 1–2 weeks including secret remediation, cross-platform validation, CI integration, documentation, and team handoff. The Chef platform bootstrap scripts represent a separate and higher-risk decision: either retain Chef Automate/Infra Server as a managed dependency or remove it entirely rather than attempting a direct cookbook migration that has no source cookbooks to translate.

## Module Migration Plan

This repository contains a mixed Ansible demonstration and Chef supporting automation rather than a conventional collection of Chef cookbooks. The individually migratable configuration units are listed below.

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only paths present in the supplied repository tree and reviewed files are listed below. No cookbook module is inferred from filenames alone.

- **website_https**:
    - Description: An Ansible playbook that installs and pins Apache on Ubuntu, installs OpenSSL tooling, generates a private key/CSR/self-signed certificate, publishes a Hello World site, configures an HTTPS virtual host, enables SSL, and restarts services.
    - Path: `chef-and-ansible/website_https.yml`
    - Technology: Ansible
    - Key Features: Ubuntu `apt` package installation, Apache 2.4.41 package pin, self-signed TLS certificate generation, virtual-host configuration, site enablement, and service handlers.
    - Migration Complexity: Low to moderate; the functional configuration is already Ansible, but it should be refactored into an idempotent role with templates, variables, and fully qualified modules.

- **poodle_fix**:
    - Description: An Ansible remediation playbook that changes Apache SSL protocol configuration to allow TLS 1.2 only and restarts Apache and SSH.
    - Path: `chef-and-ansible/poodle_fix.yml`
    - Technology: Ansible
    - Key Features: Regex-based SSL configuration replacement and service restart handlers.
    - Migration Complexity: Low, with a security-sensitive validation requirement. The handler naming is inconsistent with the declared notification and should be corrected during refactoring.

- **chef_inspec_compliance_checks**:
    - Description: Chef InSpec verification content that checks SSH root-login policy and validates the HTTPS endpoint, response content, and TLS protocol exposure.
    - Path: `chef-and-ansible/tests/ssh_profile.rb`, `chef-and-ansible/tests/website_https_verify.rb`
    - Technology: Chef InSpec
    - Key Features: SSH configuration/package assertions, HTTPS port and HTTP response checks, SSLv3 prohibition, and TLS 1.2 enablement.
    - Migration Complexity: Low to moderate. These can remain as independent InSpec tests alongside Ansible, or be ported to Ansible assertions plus a separate security/compliance framework if Chef is being removed.

- **chef_automate_bootstrap**:
    - Description: Shell bootstrap for deploying Chef Automate with Chef Infra Server, then creating a Chef user and organization and writing PEM credentials.
    - Path: `setup-automate/deploy-automate.sh`
    - Technology: Bash and Chef Automate/Infra Server CLI
    - Key Features: Host kernel tuning, remote CLI download, Automate and Infra Server deployment, user/org creation, and credential-file generation.
    - Migration Complexity: High if Chef is to be retired; this is platform provisioning rather than a cookbook and requires an architectural replacement or an explicit decision to retain Chef services.

- **chef_infra_server_bootstrap**:
    - Description: Shell bootstrap for deploying Chef Infra Server without Automate and creating the initial Chef user and organization.
    - Path: `setup-automate/deploy-chef-server.sh`
    - Technology: Bash and Chef Infra Server CLI
    - Key Features: Hostname and kernel tuning, Chef Automate CLI download, Infra Server deployment, and PEM credential generation.
    - Migration Complexity: High if removed; low as a retained legacy dependency, provided its insecure parameter handling is corrected.

### Infrastructure Files

- `README.md`: Repository-level description of Chef examples. Update it to describe the actual Ansible-based demonstration and migration status.
- `chef-and-ansible/README.md`: Explains that the examples use Chef InSpec with Ansible for continuous compliance. Preserve this conceptual boundary in the target documentation.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration using Vagrant, an Ansible playbook provisioner, Ubuntu 20.04, and Chef InSpec verification. Migrate to an agreed Ansible-native CI/test workflow or retain it temporarily as an integration harness.
- `chef-and-ansible/index.html`: Static Hello World content also represented inline in `website_https.yml`. Decide whether the target playbook should deploy this file with `copy` or use a managed template.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec SSH compliance check. Retain or port as part of the target compliance pipeline.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec HTTPS functional and TLS verification check.
- `setup-automate/deploy-automate.sh`: Chef platform bootstrap and a major migration boundary; do not embed its behavior in the web-server role.
- `setup-automate/deploy-chef-server.sh`: Chef Infra Server-only bootstrap and a major migration boundary.

### Target Details

- **Operating System**: Ubuntu 20.04 is explicitly specified in `chef-and-ansible/kitchen.yml`. The playbooks use `apt`, Debian/Ubuntu Apache paths (`/etc/apache2`), and the `apache2` service. The InSpec SSH check includes RHEL 8 compliance identifiers, but that is a control reference rather than evidence that the playbook targets RHEL. Validate whether Ubuntu 20.04 remains supported; otherwise define a current Ubuntu LTS target.
- **Virtual Machine Technology**: Vagrant is specified as the Test Kitchen driver. The production VM platform is not specified.
- **Cloud Platform**: Not specified. The bootstrap comments state that Chef can be deployed on an on-premises or cloud VM, but no provider-specific resources or SDKs are present.

## Migration Approach

### Key Dependencies to Address

- **Apache 2.4.41 Ubuntu package**: Replace the hard-coded package version with a tested variable or distribution-supported version policy. Use `ansible.builtin.apt` and verify repository availability on the selected Ubuntu release.
- **OpenSSL and Python OpenSSL bindings**: Use `ansible.builtin.openssl_privatekey`, `openssl_csr`, and `openssl_certificate` from the supported `community.crypto` collection, with collection versions pinned in `collections/requirements.yml`.
- **Chef InSpec**: Decide whether InSpec remains the independent compliance verifier. If Chef is retired, port the essential checks to an approved Ansible-compatible compliance tool while preserving the SSH and TLS acceptance criteria.
- **Vagrant/Test Kitchen**: Keep temporarily for reproducible validation or replace with Molecule, CI-managed ephemeral VMs, or the organization’s standard Ansible test platform.
- **Chef Automate and Chef Infra Server**: These are external platform dependencies, not cookbook dependencies. Either document them as retained services and secure their bootstrap, or replace their functions with Ansible Automation Platform/AWX, a secrets manager, and a separate compliance/reporting solution.
- **Chef CLI download endpoint**: Replace unauthenticated “latest” downloads with a pinned, checksum-verified artifact from an approved repository if the scripts remain in use.

### Security Considerations

- **Hard-coded credentials**: Both Chef bootstrap scripts visibly assign `userpassword='password'` and pass it to `chef-server-ctl`. Remove this immediately. Obtain credentials from Ansible Vault, an external secrets manager, or an interactive/short-lived provisioning mechanism; never commit them to source.
- **Generated PEM credentials**: The scripts generate user and organization PEM files. Define secure ownership and mode, prevent them from entering artifacts/logs, rotate them, and migrate existing credentials if these scripts have been executed.
- **Private key and certificate handling**: The web playbook creates `/etc/apache2/certs/apache.key`, CSR, and self-signed certificate. Use restrictive key permissions (the current certificate directory mode `0640` is not a suitable directory mode), separate public and private material, and use an enterprise CA or ACME workflow for production rather than a self-signed certificate.
- **TLS policy**: The intended policy disables SSLv3 and permits TLS 1.2. Confirm whether TLS 1.3 is required, use a distribution-supported Apache SSL configuration, and test the resulting cipher/protocol policy. Avoid broad regex edits without validating the effective configuration.
- **SSH service disruption**: The playbooks notify a restart of `sshd` while changing web SSL settings. This is unnecessary for the Apache change and creates avoidable access risk. Remove the SSH restart unless an SSH configuration change is actually managed and use safe restart/reload behavior.
- **Privilege and file modes**: Playbooks run as root/become root. Limit escalation, define owners/groups/modes explicitly, and use `ansible.builtin.command` only where no idempotent module exists. Replace `a2ensite`, `a2dissite`, and `a2enmod` commands with idempotent Ansible modules or carefully guarded commands.
- **Transport and supply chain**: The bootstrap scripts pipe a remote “latest” download through `curl`/`gunzip`. Pin versions, verify checksums/signatures, and use an internal artifact mirror.
- **Verification gap**: The SSH InSpec check allows a package absence as an alternative assertion and should be reviewed for intent. Ensure the target test actually proves the desired `PermitRootLogin no` policy rather than passing because a package is missing.

### Technical Challenges

- **No Chef cookbook source exists**: There are no recipes or cookbook metadata to translate. The migration team must avoid inventing cookbook behavior and instead treat the existing Ansible playbooks as the functional baseline.
- **Inline configuration duplication**: Apache virtual-host content and website HTML are embedded as variables, while equivalent HTML also exists in `index.html`. Consolidate these into role templates/files and define a single source of truth.
- **Idempotency and module modernization**: Raw `command` tasks for site/module activation and a compact `replace` task can produce fragile or non-obvious behavior. Refactor, check changed status, validate Apache configuration before reload, and use handlers consistently.
- **OS/version drift**: Ubuntu 20.04 and the exact Apache package version may no longer be available or appropriate. Test on the selected supported LTS and define behavior for Debian-family variants.
- **Certificate lifecycle**: Self-signed certificates are suitable for a lab demonstration but not production. Establish CA issuance, renewal, trust distribution, and rollback before promoting the role.
- **Chef platform scope**: Removing Chef Infra Server/Automate is not equivalent to converting a web playbook. Inventory any external users, organizations, nodes, policies, compliance reports, and PEM consumers before decommissioning.
- **Test framework transition**: Kitchen metadata combines Vagrant, an Ansible provisioner, and InSpec. The team needs an agreed CI path that tests both convergence and security assertions without depending on deprecated or unpinned tooling.

### Migration Order

1. **Inventory and security containment**: Confirm that the repository contains no hidden cookbooks or external dependencies, remove/rotate the visible bootstrap password if used, and decide whether Chef services are retained.
2. **Website HTTPS baseline**: Refactor `website_https.yml` into an Ansible role with variables, templates, package/version policy, certificate handling, Apache validation, and safe handlers. This is the lowest-risk functional unit and establishes the target conventions.
3. **TLS hardening**: Integrate the `poodle_fix` behavior into the web role or a dedicated security role, correct handler notifications, and validate effective TLS behavior with the existing InSpec tests.
4. **Compliance test transition**: Keep InSpec as an acceptance gate during the transition, then port or standardize the SSH and HTTPS controls in the selected Ansible compliance pipeline.
5. **Bootstrap platform decision**: If Chef Automate/Infra Server remains, secure and parameterize the scripts. If it is being retired, design replacements for node orchestration, secrets, compliance reporting, and identity before decommissioning either bootstrap path.
6. **CI and operational handoff**: Replace or formalize Kitchen/Vagrant testing, pin Ansible collections and runtime versions, document inventories and secret inputs, and run staged deployment against disposable and then representative hosts.

### Assumptions

- The supplied tree is complete; no nested Chef cookbook directories, `metadata.rb`, Berksfile, Policyfile, or Chef recipes are present outside the listed paths.
- The user’s request refers to Chef examples, but the web configuration itself is already Ansible and is not a Chef cookbook migration.
- Ubuntu 20.04 is the intended lab target because it is the only explicit platform declaration.
- Vagrant is used for testing; the production virtualization/cloud platform is unknown.
- The self-signed certificate and Hello World content are demonstration assets, not production requirements.
- The Chef Automate and Chef Infra Server scripts may be examples rather than actively used production provisioning. Execution history, generated PEM files, and external consumers must be checked separately.
- The visible placeholder password may have been used as a real credential; credential rotation is required unless proven otherwise.
- No external inventory, variable files, Ansible Vault files, CI definitions, or secret stores were included in the reviewed tree.
- The final target may retain Chef InSpec for compliance verification; a decision is required before removing Chef tooling.
- Apache configuration syntax, package availability, certificate policy, and SSH service naming must be validated on the actual target image before production rollout.
- Timeline estimates assume one engineer familiar with Ansible and access to disposable Ubuntu test hosts; security review, platform replacement, or unknown external Chef consumers can extend the schedule substantially.
