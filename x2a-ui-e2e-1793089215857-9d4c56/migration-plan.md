# MIGRATION FROM CHEF-RELATED EXAMPLES AND BASH BOOTSTRAP TO ANSIBLE

This repository is a small example and test repository, not a conventional Chef cookbook repository. The supplied tree contains two Ansible playbooks, Chef InSpec checks, Test Kitchen configuration, and two Bash scripts for Chef Automate/Infra Server bootstrap. It contains no Puppet modules, Chef cookbooks, or PowerShell modules: there are no `manifests/init.pp`, `recipes/default.rb`, or `.psd1` module manifests in the provided repository tree. Therefore, the required module inventory is intentionally empty. The practical migration scope is to standardize the existing Ansible examples, decide whether Chef Automate/Infra Server remains necessary, and improve security, testing, and operational packaging.

Estimated effort is approximately 1–2 weeks for a focused refactor and 2–4 weeks including security review, secrets remediation, CI testing, target-platform validation, and team handover. If Chef Automate/Infra Server must also be replaced rather than retired, the schedule will be substantially larger and requires a separate platform migration project.

## Module Migration Plan

This repository does not contain individually packaged Puppet modules, Chef cookbooks, or PowerShell modules. The module inventory is empty because no required module entrypoint was found:

- No Puppet `manifests/init.pp` files
- No Chef `recipes/default.rb` files
- No PowerShell `.psd1` module manifests

### MODULE INVENTORY

**No modules identified.** There are no module entries to migrate. The files under `chef-and-ansible/` are standalone Ansible playbooks and InSpec test files, and the files under `setup-automate/` are Bash bootstrap scripts; none qualifies as a Puppet, Chef cookbook, or PowerShell module under the required entrypoint rules.

**CRITICAL PATH VERIFICATION:**
Only paths present in the supplied repository tree are referenced below. No module paths are invented, and no external dependencies are listed as modules.

### Infrastructure Files

- `README.md`: Repository description identifying the project as Chef examples. Update it to describe the supported Ansible workflow and the disposition of the Chef bootstrap scripts.
- `chef-and-ansible/README.md`: Explains the InSpec-with-Ansible example. Expand it with prerequisites, inventory expectations, supported OS versions, secret handling, and CI commands.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration using Vagrant, the Ansible provisioner, Ubuntu 20.04, and InSpec verification. Preserve as a compatibility test if needed, but consider Molecule or an equivalent CI framework for the maintained Ansible implementation.
- `chef-and-ansible/website_https.yml`: Standalone Ansible playbook that installs Apache, generates a self-signed certificate, configures a Hello World HTTPS virtual host, and enables Apache SSL.
- `chef-and-ansible/poodle_fix.yml`: Standalone Ansible playbook intended to restrict Apache SSL protocols to TLS 1.2.
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec checks for port 443, HTTPS response content, SSLv3 disabled, and TLS 1.2 enabled.
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec control concerning SSH root login and OpenSSH package state.
- `setup-automate/deploy-automate.sh`: Bash script that downloads the current Chef Automate CLI, deploys Automate plus Infra Server, and creates a Chef user and organization.
- `setup-automate/deploy-chef-server.sh`: Bash script that downloads the current Chef Automate CLI, deploys Chef Infra Server, and creates a Chef user and organization.

## Target Details

- **Operating System**: Ubuntu 20.04 is the explicit test target in `chef-and-ansible/kitchen.yml`. The playbooks use Ubuntu/Debian conventions including `apt`, `/etc/apache2`, `apache2`, and `a2enmod`/`a2ensite`. The production OS is not specified. Confirm Ubuntu lifecycle and Chef Automate/Infra Server support independently before selecting a production image.
- **Virtual Machine Technology**: Vagrant is specified as the Test Kitchen driver. The production VM technology is not specified.
- **Cloud Platform**: Not specified. The bootstrap comments allow on-premises or cloud VMs, but no AWS, Azure, or GCP integration is present.

## Migration Approach

Because there are no source modules to convert, use a consolidation and hardening approach:

1. Establish whether the desired end state still needs Chef Automate or Chef Infra Server.
2. Refactor the standalone website and TLS playbooks into reusable Ansible roles or a clearly structured playbook project.
3. Externalize hostnames, package versions, virtual-host content, certificate strategy, and service policy into inventory/group variables.
4. Add pinned Ansible collections, linting, idempotence tests, syntax checks, and CI acceptance tests.
5. Remove or securely replace the Chef bootstrap scripts after the Chef control-plane decision is approved.

### Key Dependencies to Address

- **Ansible**: Pin the Ansible version and use fully qualified module names. Add a project requirements file and a documented inventory.
- **Ubuntu/Debian apt repositories**: `website_https.yml` uses `apt` and pins Apache to `2.4.41-4ubuntu3.10`. Verify repository availability and security support; prefer an approved patched version or a controlled package repository.
- **Apache HTTP Server**: Required by the HTTPS playbook. Manage package, modules, virtual host, configuration validation, and service reload as one tested unit.
- **OpenSSL and Ansible crypto modules**: The playbook uses `openssl_privatekey`, `openssl_csr`, and `openssl_certificate`; pin the collection that supplies these modules and test their behavior on the selected Ansible version.
- **Chef InSpec**: Existing tests use InSpec. Retain them as an acceptance gate if the organization supports Chef InSpec, or translate them to Molecule/Testinfra/Ansible assertions and a central compliance scanner.
- **Test Kitchen and Vagrant**: Used for the current local test lifecycle. Decide whether to maintain them for regression testing or replace them with the team's standard Ansible CI.
- **Chef Automate CLI and Chef Infra Server**: The shell scripts download a moving `current/latest` artifact from `packages.chef.io`. If Chef remains, pin and verify a supported release and manage installation through a controlled Ansible implementation. If Chef is being retired, remove these scripts from the active deployment path.
- **Host utilities**: `curl`, `gunzip`, `hostnamectl`, `sysctl`, Apache, SSH, and OpenSSL are implicit runtime dependencies and must be validated on the target OS.

### Security Considerations

- **Hardcoded password**: Both Bash scripts contain `userpassword='password'`. Treat this as compromised, rotate any corresponding Chef credentials, and remove it from source. Use Ansible Vault, an external secret manager, or short-lived credentials.
- **Chef PEM files**: The scripts generate user and organization `.pem` files in the working directory. Protect them with restrictive permissions, prevent source-control and log exposure, control transfer, and revoke or rotate them during migration.
- **TLS private key**: `website_https.yml` creates `/etc/apache2/certs/apache.key`. Set explicit root ownership and restrictive permissions. Do not use a self-signed certificate for production unless the trust model explicitly requires it; use an approved CA or ACME process and document renewal.
- **TLS protocol policy**: The intended policy disables SSLv3 and enables TLS 1.2. Confirm whether TLS 1.3 should also be enabled and test the effective Apache cipher/protocol policy rather than relying only on file contents.
- **SSH hardening**: The InSpec check references `PermitRootLogin`, but the reviewed Ansible playbooks do not enforce it. Add a separate, carefully tested SSH hardening task or role, validate configuration before reload, and provide console/recovery access to avoid lockout.
- **Privilege escalation**: Both playbooks run as `root` or use `become: yes`. Limit inventory access, use least privilege where possible, and document the required administrative permissions.
- **Unsafe artifact download**: The Bash scripts pipe a live download from a moving URL into `gunzip`. Pin a release, verify checksum/signature, use a trusted mirror, and avoid executing unverified artifacts.
- **Certificate validation in tests**: The InSpec HTTPS test sets `ssl_verify: false`, appropriate only for the self-signed test certificate. Do not use that setting as evidence of production certificate trust.
- **File and directory modes**: The certificate directory is assigned mode `0640`, which is not a normal searchable directory mode. Define directory and private-key modes deliberately and verify them in tests.

### Technical Challenges

- **No source modules exist**: There is no Chef recipe-to-role or Puppet-manifest-to-task conversion. The work is repository restructuring, operational hardening, and lifecycle decisions rather than a direct module translation.
- **Chef control-plane scope**: It is unclear whether Automate/Infra Server is a required dependency or merely part of the examples. Recreating it in Ansible without a business requirement would increase scope unnecessarily.
- **Version drift**: Ubuntu 20.04, the pinned Apache package, the `latest` Chef CLI, and unpinned Ansible components create reproducibility and support risks. Establish a version matrix and test it in CI.
- **Idempotence and handler correctness**: The playbooks use raw `command` calls for `a2dissite`, `a2ensite`, and `a2enmod`. The `poodle_fix.yml` notification refers to `Restart apache2`, while its handler is named `Restart apache`, so the notification does not match the declared handler. Replace fragile commands with idempotent tasks or guarded commands and correct handler names.
- **TLS productionization**: Self-signed certificates are suitable for the example but require CA integration, renewal, secret storage, and expiry monitoring for production.
- **Insufficient test coverage**: Existing tests do not cover Apache syntax validation, file ownership/modes, certificate expiry or renewal, idempotence, rollback, or Chef bootstrap success. Add these before cutover.

### Migration Order

1. **Inventory and decision**: Confirm that the repository contains no modules, identify any deployed consumers, and decide whether Chef Automate/Infra Server is retained, replaced, or retired.
2. **Secrets remediation**: Remove and rotate the hardcoded password and any generated Chef keys; establish the approved secrets-management path.
3. **Ansible project baseline**: Pin Ansible and crypto collections, add linting and syntax checks, and document the Ubuntu test target and inventory contract.
4. **HTTPS refactor**: Convert `website_https.yml` into a reusable role or maintainable playbook with variables, proper certificate handling, Apache config validation, and idempotent service management.
5. **Security hardening**: Refactor `poodle_fix.yml`, correct the handler mismatch, implement explicit SSH policy, and validate TLS and file permissions.
6. **Verification and CI**: Retain or translate the InSpec controls, add idempotence and functional tests, and run them against disposable Ubuntu systems.
7. **Cutover and decommissioning**: Pilot in non-production, perform staged rollout, document ownership and rollback, and archive or remove Chef bootstrap scripts if no longer required.

### Assumptions

- The supplied repository tree is complete for this analysis.
- There are no Puppet `manifests/init.pp`, Chef `recipes/default.rb`, or PowerShell `.psd1` files; therefore the module inventory must remain empty.
- Standalone Ansible playbooks, Bash scripts, and InSpec tests are infrastructure/supporting files, not entries in the required source-module inventory.
- Ubuntu 20.04 is a test target, not confirmed production policy.
- Vagrant is used for testing, while production virtualization and cloud platform are unknown.
- The literal bootstrap password may have been exposed and must not be reused.
- No external CA, DNS, firewall, load balancer, certificate renewal service, inventory, secret manager, or production variable files were supplied.
- Chef Automate and Chef Infra Server may be example dependencies rather than required target services; stakeholders must confirm this.
- Existing InSpec tests are compliance checks, not proof that all desired security controls are implemented.
- The migration estimate assumes a single Apache example and limited environments. Multiple production environments, HA Chef services, regulated evidence requirements, or an enterprise CA integration will increase effort.
- Team coordination should assign owners for Ansible refactoring, secrets/security, Chef control-plane disposition, CI/testing, and rollout approval. The team should agree on variable interfaces, acceptance criteria, escalation paths, and a rollback plan before production deployment.
