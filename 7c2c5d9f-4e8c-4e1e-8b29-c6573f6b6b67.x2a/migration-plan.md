# MIGRATION FROM CHEF-RELATED INFRASTRUCTURE TO ANSIBLE

## Executive Summary

This repository is a small Chef-related example repository, but it contains no conventional Chef cookbooks. The implementation under `chef-and-ansible/` is already Ansible, with Chef InSpec used for acceptance testing. The repository contains two Ansible playbooks for Apache HTTPS/TLS configuration, one Test Kitchen/Vagrant configuration, two InSpec checks, and two shell scripts for bootstrapping Chef Infra Server/Automate. The migration is therefore not a recipe-to-role conversion; it is a low-volume Ansible productionization and security-hardening effort, plus a separate decision about retiring or retaining the Chef control plane.

Estimated effort is 3–7 engineering days for refactoring, testing, and documentation on Ubuntu 20.04. Production certificate management, secret rotation, CI integration, multi-OS support, and Chef Server/Automate retirement could extend the work to 1–2 weeks.

## Module Migration Plan

The repository contains Ansible playbooks and Chef InSpec tests, but no Puppet modules, Chef cookbooks, or PowerShell modules requiring module-by-module migration.

### MODULE INVENTORY

**EMPTY — no qualifying source modules were found.**

The supplied repository tree contains no path matching any required module entrypoint:

- No `**/recipes/default.rb` was present, so no Chef cookbook was identified.
- No `**/manifests/init.pp` was present, so no Puppet module was identified.
- No `**/*.psd1` manifest was present, so no PowerShell module was identified.

The files `chef-and-ansible/website_https.yml` and `chef-and-ansible/poodle_fix.yml` are already Ansible playbooks, not Chef cookbook modules. The Ruby files under `chef-and-ansible/tests/` are Chef InSpec verification tests, not Chef cookbook entrypoints. They are therefore documented under Infrastructure Files and testing rather than listed as source modules.

**CRITICAL PATH VERIFICATION:**

No module inventory entries are claimed because no qualifying module entrypoint was found in the supplied repository tree. All paths referenced elsewhere in this plan are paths shown in the supplied tree and are not invented module paths.

### Infrastructure Files

- `README.md`: Repository-level description of Chef examples. It supplies context but no cookbook implementation or dependency declaration.
- `chef-and-ansible/README.md`: Describes using Chef InSpec with Ansible for compliance automation. Use it as the basis for the migration runbook.
- `chef-and-ansible/website_https.yml`: Existing Ansible playbook that updates apt, installs Apache/OpenSSL tooling, creates certificate material, configures an HTTPS virtual host, deploys hello-world content, enables Apache site/SSL functionality, and restarts services.
- `chef-and-ansible/poodle_fix.yml`: Existing Ansible playbook that changes Apache SSL protocol configuration to TLS 1.2 and restarts Apache/SSH through handlers.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration using Vagrant, the Ansible provisioner, Chef InSpec verifier, and Ubuntu 20.04.
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec acceptance checks for port 443, HTTPS status/content, SSLv3 absence, and TLS 1.2 availability.
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec control checking that SSH root login is not enabled, with RHEL 8/STIG control metadata.
- `chef-and-ansible/index.html`: Static example website content; treat as test fixture or role template content.
- `setup-automate/deploy-chef-server.sh`: Shell bootstrap for Chef Infra Server using the Chef Automate CLI, including Chef user and organization creation.
- `setup-automate/deploy-automate.sh`: Shell bootstrap for Chef Automate plus Chef Infra Server, including user and organization creation.

No `Berksfile`, `Policyfile.rb`, cookbook `metadata.rb`, Puppetfile, PowerShell `requirements.psd1`, or Ansible collection requirements file appears in the supplied tree. Consequently, there are no source cookbook dependency manifests to translate.

### Target Details

- **Operating System**: Ubuntu 20.04 is explicitly selected in `chef-and-ansible/kitchen.yml`. The playbooks use Ubuntu/Debian-specific apt and Apache paths and commands. The RHEL 8 identifiers in the SSH InSpec test are compliance references, not proof of RHEL provisioning support.
- **Virtual Machine Technology**: Vagrant is specified for Test Kitchen. The production virtualization platform is not specified.
- **Cloud Platform**: Not specified. The Chef bootstrap comments mention on-premises or cloud VMs, but no provider-specific configuration is present.

## Migration Approach

### Key Dependencies to Address

- **Ansible core**: Pin a supported Ansible version and standardize on fully qualified builtin modules.
- **`community.crypto`**: The OpenSSL key, CSR, and certificate tasks should be backed by a pinned `community.crypto` collection in a new `collections/requirements.yml`.
- **Ubuntu apt repositories and Apache**: The playbook pins `apache2=2.4.41-4ubuntu3.10`. Verify that this package remains available; otherwise make the version an explicit supported variable or use a controlled repository.
- **Apache utilities**: `a2ensite`, `a2dissite`, and `a2enmod` are invoked as commands. Replace them with idempotent modules or guarded commands.
- **Chef InSpec/Test Kitchen/Vagrant**: Retain temporarily for acceptance testing, or migrate the checks to Testinfra/pytest if the target CI standard is Ansible-native.
- **Chef Automate/Infra Server CLI**: The shell scripts download the latest CLI and invoke Chef server commands. If Chef is being retired, replace this control-plane workflow with the organization’s Ansible Automation Platform/control-node process; otherwise retain it as separately owned legacy infrastructure.

### Security Considerations

- **Hardcoded password**: Both `setup-automate` scripts contain `userpassword='password'`. Treat it as compromised, rotate any affected account, remove it from source, and use Ansible Vault or an external secret manager.
- **Chef PEM credentials**: The scripts create user and organization PEM files. Protect, rotate, and control their lifecycle; do not commit generated keys or expose them in logs.
- **TLS private key and certificates**: `website_https.yml` creates `/etc/apache2/certs/apache.key`, CSR, and a self-signed certificate. Define ownership and restrictive key permissions, and replace self-signed certificates with trusted CA-managed certificates in production.
- **Certificate directory mode**: The current directory mode `0640` may prevent directory traversal/search. Use a directory mode appropriate for Apache and a more restrictive separate mode for the private key.
- **TLS policy**: Consolidate the TLS settings from both playbooks. Validate supported TLS versions and ciphers, and avoid broad configuration replacement that could overwrite unrelated Apache settings.
- **SSH access**: The playbooks run as root and restart SSH, but do not configure `PermitRootLogin`. Add staged SSH hardening with a break-glass account, connection safeguards, and pre-restart validation.
- **Privilege escalation**: Prefer a controlled deployment account with `become: true` instead of direct root login where operationally possible.
- **Untrusted/latest download**: The bootstrap scripts pipe a `latest` download from `packages.chef.io` directly into `gunzip`. Pin a version, verify checksums/signatures, and download through a controlled process.
- **TLS identity**: The CSR uses `myhost`, while the bootstrap hostname is `automate.chef.lab`. Define inventory names and certificate SANs explicitly. Keep `ssl_verify: false` limited to test verification.

### Technical Challenges

- **No source cookbooks**: A conventional Chef-to-Ansible cookbook mapping cannot be performed from this repository. Confirm whether cookbooks exist in another repository before closing discovery.
- **Idempotence and maintainability**: Refactor inline YAML content into templates/variables and replace direct commands with idempotent tasks where possible.
- **Configuration ownership**: Both playbooks modify Apache and trigger service restarts. Merge them into one Apache/TLS role and one handler strategy.
- **OS portability**: The implementation is Ubuntu-specific despite RHEL-oriented compliance labels. Establish supported OSes and create OS-specific variables/tasks if RHEL support is required.
- **Certificate lifecycle**: Self-signed demo certificates do not provide production renewal, trust distribution, SAN management, or revocation.
- **Chef control-plane transition**: Inventory Chef clients, organizations, policies, keys, and integrations before disabling Chef Infra Server or Automate.
- **Testing coverage**: Add checks for Apache syntax, certificate validity and SANs, key permissions, HTTP-to-HTTPS behavior, and unintended exposure of port 80.

### Migration Order

1. Confirm the repository boundary and verify whether external Chef cookbooks exist.
2. Decide whether Chef Infra Server/Automate is retained, handed off, or retired separately from the web example.
3. Run the existing Vagrant/Test Kitchen scenario on Ubuntu 20.04 and capture the InSpec baseline.
4. Refactor `website_https.yml` into an `apache_https` role with variables, templates, pinned collections, safe handlers, and explicit file ownership.
5. Fold `poodle_fix.yml` into the Apache/TLS role to eliminate duplicate ownership and restarts.
6. Add explicit SSH hardening only after establishing safe access and rollback procedures.
7. Remove and rotate hardcoded credentials, secure PEM files, pin external artifacts, and establish certificate lifecycle management.
8. Add CI, perform a canary deployment, document rollback, and roll out through the team’s Ansible automation platform.
9. Retire or separately maintain the Chef bootstrap scripts only after Chef dependencies are accounted for.

### Assumptions

- The supplied repository tree is complete for this assessment.
- No external Chef cookbook repository was provided.
- The absence of `recipes/default.rb`, `manifests/init.pp`, and `.psd1` files means the MODULE INVENTORY is intentionally empty.
- The existing YAML playbooks are the implementation being productionized, not Chef source awaiting translation.
- Ubuntu 20.04 is the initial target platform.
- Vagrant is used for testing; the production VM platform and cloud provider are unknown.
- Self-signed TLS is acceptable only for the example unless the owner confirms otherwise.
- `myhost` is an inventory alias and not necessarily a production DNS name.
- The InSpec files are acceptance controls, not provisioning modules.
- Ansible version, collection versions, inventory, CI system, secret backend, PKI, ownership, change windows, rollback procedures, and compliance scope are not supplied.
- The plaintext Chef password may have been used in a real environment and must be handled as exposed.
