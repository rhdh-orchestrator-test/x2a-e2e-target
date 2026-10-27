# MIGRATION FROM CHEF AND CHEF-ADJACENT EXAMPLES TO ANSIBLE

## Executive Summary

The repository does not contain Chef cookbooks to migrate. It contains two Ansible playbooks, Chef InSpec verification controls, a Test Kitchen configuration, and shell scripts that bootstrap Chef Infra Server and Chef Automate. No `recipes/default.rb`, `manifests/init.pp`, or PowerShell `.psd1` module manifests were found. The infrastructure implementation is therefore already partly in Ansible; the practical migration is to productionize the existing playbooks, preserve or port their compliance tests, and decide whether the Chef control-plane bootstrap scripts should be retired or replaced.

The demonstrated scope is low-to-moderate complexity: approximately 1–2 weeks for an engineer to refactor and test the web/TLS automation, assuming no undocumented Chef consumers. Chef Server/Automate retirement, data migration, certificate lifecycle, and enterprise rollout should be estimated as a separate workstream.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests. It contains no discoverable Chef cookbook, Puppet module, or PowerShell module.

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**

The repository tree and recursive searches confirm that there are no paths matching:

- `**/recipes/default.rb`
- `**/manifests/init.pp`
- `**/*.psd1`

Therefore, the required module inventory is intentionally empty: there are no Chef cookbook modules, Puppet modules, or PowerShell modules that qualify for separate inventory entries. No nonexistent module paths are invented below. The Ansible playbooks are cataloged under Infrastructure Files because they are files, not module directories.

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: An Ansible playbook for Ubuntu that updates apt, installs a pinned Apache package and OpenSSL-related packages, creates a certificate directory, generates a private key/CSR/self-signed certificate, writes a test HTTPS virtual host and Hello World page, enables the site and SSL module, and restarts Apache. Refactor this into a reusable Ansible role with defaults, templates, explicit collection dependencies, and idempotent site/module enablement.
- `chef-and-ansible/poodle_fix.yml`: An Ansible playbook intended to replace Apache's SSL protocol configuration with a TLS 1.2-only setting and restart Apache/SSH. Correct the handler notification mismatch (`Restart apache2` versus the declared `Restart apache`) before use, and validate the resulting Apache configuration.
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec acceptance checks for port 443, an HTTPS 200 response containing `Hello, world!`, SSLv3 disabled, and TLS 1.2 enabled. Keep during transition or port to Molecule/Testinfra/OpenSCAP according to the target governance model.
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec control checking that SSH root login is not enabled, with STIG/SRG metadata and an additional OpenSSH package assertion. Retain as a compliance gate or translate to the selected Ansible-native test framework; verify that its package fallback expresses the intended policy on Ubuntu.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration using Vagrant, the Ansible provisioner, Ubuntu 20.04, and Chef InSpec verification. Decide whether to retain it temporarily or replace it with Ansible Molecule and CI.
- `chef-and-ansible/index.html`: Static Hello World content used by the HTTPS scenario. Manage it as an Ansible role file/template rather than embedding long content in playbook variables.
- `chef-and-ansible/README.md`: Describes the example as Chef InSpec used alongside Ansible for continuous compliance. Update it with role structure, supported systems, test commands, and ownership.
- `README.md`: Repository-level description of Chef examples. Update it after the migration scope and any Chef control-plane retirement decision are finalized.
- `setup-automate/deploy-chef-server.sh`: Shell bootstrap that downloads the Chef Automate CLI, deploys Chef Infra Server, creates a Chef user and organization, and writes PEM keys. Treat as legacy control-plane automation; replace or isolate it only after inventorying its users and data.
- `setup-automate/deploy-automate.sh`: Similar bootstrap for Chef Automate plus Chef Infra Server. Treat Chef control-plane replacement/decommissioning as a separately governed migration.

### Target Details

- **Operating System**: Ubuntu 20.04 is explicitly selected in `chef-and-ansible/kitchen.yml`; `apt`, `/etc/apache2`, and `apache2` service conventions confirm a Debian/Ubuntu target. The InSpec control contains RHEL 8 STIG identifiers, but those are compliance references and do not establish a RHEL deployment target.
- **Virtual Machine Technology**: Vagrant is specified by Test Kitchen. The provider is not specified.
- **Cloud Platform**: Not specified. The shell comments mention on-premises or cloud VMs, but contain no provider-specific implementation.

## Migration Approach

### Key Dependencies to Address

- **Ansible/ansible-core**: Define a supported version, inventory conventions, linting, check-mode expectations, CI pipeline, and role layout.
- **OpenSSL modules**: The playbook uses short names such as `openssl_privatekey`, `openssl_csr`, and `openssl_certificate`. Declare and pin the appropriate `community.crypto` collection rather than relying on implicit resolution.
- **Apache and Ubuntu packages**: The exact `apache2=2.4.41-4ubuntu3.10` pin may not exist on newer repositories. Parameterize package versions and establish a supported OS baseline.
- **Apache site/module management**: Replace imperative `a2dissite`, `a2ensite`, and `a2enmod` commands with idempotent Ansible patterns or guarded commands, and add configuration syntax checks before restart.
- **Vagrant/Test Kitchen**: Either retain the current test harness during transition or move to Molecule with a supported driver and CI execution.
- **Chef InSpec**: Continue using InSpec as a temporary acceptance verifier, or port the controls to Testinfra/Molecule/OpenSCAP if removing Chef tooling is a requirement.
- **Chef Infra Server/Automate**: The scripts depend on Chef Automate CLI, Chef server commands, Chef users/organizations, and PEM credentials. Inventory policies, nodes, keys, reporting, and integrations before replacing the control plane with Ansible Automation Platform/AWX or another approved execution service.

### Security Considerations

- **Hardcoded credentials**: Both shell scripts contain a visible plaintext password (`password`) and identity/organization values. Treat it as compromised if it was ever used, rotate it, remove it from source, and use Ansible Vault or an enterprise secrets manager.
- **Chef PEM keys**: User and organization validator PEM files are generated by the scripts. Control their permissions, storage, rotation, distribution, and destruction; audit history and artifact storage for copies.
- **Unsafe binary download**: The scripts pipe a remote `curl` download into decompression and execution. Pin a known release, verify checksum/signature, use an approved artifact repository, and avoid unreviewed executable content.
- **TLS private keys and certificates**: The web playbook creates a private key and self-signed certificate under `/etc/apache2/certs`. Use restrictive key permissions, keep key material out of logs, and define a production CA/ACME or certificate-manager process. `common_name: myhost` is suitable only for a test scenario.
- **TLS policy**: Preserve the SSLv3-disabled and TLS 1.2-enabled checks, but decide whether TLS 1.3 and approved cipher suites are required. A self-signed certificate must not be treated as production trust.
- **SSH and privilege**: The playbooks use root/become access and the InSpec control checks root SSH login. Use dedicated deployment identities, controlled sudo/become, audit logging, and staged rollout to avoid administrative lockout.
- **Permissions and restarts**: Review the certificate directory mode, key mode, configuration modes, and restart notifications. Run Apache syntax validation before service changes and use rolling or maintenance-window deployment.

### Technical Challenges

- **No cookbook source is present**: Any actual Chef recipes may live outside this repository. Confirm the repository is complete and identify external cookbooks, roles, environments, data bags, policyfiles, node attributes, and Chef Server consumers.
- **The implementation is already partly Ansible**: The work is refactoring proof-of-concept playbooks into tested roles, not translating Chef recipes line by line.
- **Handler mismatch**: `poodle_fix.yml` notifies `Restart apache2` while defining `Restart apache`; this must be corrected and covered by tests.
- **Imperative commands and idempotence**: Site/module enablement commands may report changes repeatedly or fail on reruns. Use state-aware modules or explicit guards.
- **OS ambiguity**: Ubuntu paths conflict with RHEL-oriented compliance identifiers. Decide whether Ubuntu only or multi-platform support is required and implement platform variables accordingly.
- **Certificate lifecycle**: Self-signed test certificates do not solve issuance, renewal, trust distribution, revocation, or rollback for production.
- **Control-plane transition**: Chef Automate/Infra Server may contain policy, identity, key, compliance, and reporting data not represented in these scripts. Do not decommission it until dependencies and retention requirements are signed off.

### Migration Order

1. **Discovery and containment**: Confirm the repository is complete, identify external Chef consumers, and rotate/remove the exposed sample credentials.
2. **Target standards**: Agree on supported Ubuntu/other OS versions, ansible-core and collection versions, inventory model, secrets platform, certificate authority, and execution platform.
3. **HTTPS role**: Convert `website_https.yml` into a reusable Apache HTTPS role with templates, variables, secure permissions, certificate handling, and idempotent module/site management.
4. **TLS hardening**: Integrate or retain `poodle_fix.yml`, correct its handler, add Apache validation, and define the approved TLS/cipher policy.
5. **Compliance tests**: Run the existing InSpec tests in parallel, then port them to the selected Ansible-compatible validation framework if required.
6. **CI and rollout**: Add ansible-lint, secret scanning, Molecule or equivalent integration tests, check-mode testing, TLS scans, and staged deployment/rollback procedures.
7. **Chef control-plane decision**: Migrate any required Chef data, keys, policies, nodes, and reporting integrations; obtain operational sign-off before retiring Chef Server/Automate bootstrap and services.

### Assumptions

- The supplied repository tree is complete for this analysis; no external cookbook source, Berksfile, Policyfile, metadata, roles, inventories, or encrypted data bags are included.
- The user’s request refers to Chef cookbooks, but this checkout contains no qualifying cookbook directories; its infrastructure examples are already Ansible.
- `myhost` is the intended test host and root/become access is available in the test environment.
- Ubuntu 20.04 is the demonstrated target, not necessarily the final production baseline.
- The Vagrant provider, production OS matrix, cloud provider, DNS, network topology, and certificate authority are unspecified.
- The Chef bootstrap scripts may be examples rather than active production automation; their retirement impact cannot be determined from this repository.
- The plaintext script values may be examples, but must be treated as secrets if they were used or exposed.
- The InSpec controls represent demonstrated acceptance/security checks, not a complete compliance profile.
- The estimate excludes undocumented integration discovery, Chef data migration, production approvals, and organization-wide training.
