# MIGRATION FROM CHEF-RELATED EXAMPLES TO ANSIBLE

## Executive Summary

This repository is a small Chef-related examples repository, not a repository containing conventional Chef cookbooks. The tree contains an existing Ansible playbook, Chef InSpec verification controls, Test Kitchen configuration, and Bash scripts that bootstrap Chef Automate or Chef Infra Server. Searches found no qualifying Chef cookbook entrypoints (`recipes/default.rb`), Puppet module entrypoints (`manifests/init.pp`), or PowerShell module manifests (`.psd1`). Therefore, there are no source modules to translate into Ansible roles.

The practical migration is a short consolidation and hardening effort: retain or improve the existing Ansible playbook, decide whether Chef InSpec remains the compliance verifier, address exposed bootstrap credentials, and determine whether Chef Automate/Infra Server is being retained or retired. A focused implementation is estimated at 1–2 weeks after scope confirmation; replacing the Chef platform bootstrap scripts and validating production rollout may require an additional 1–2 weeks.

## Module Migration Plan

This repository contains supporting Chef/Ansible examples, but **no qualifying Puppet modules, Chef cookbooks, or PowerShell modules were discovered**.

### MODULE INVENTORY

**No qualifying modules were discovered.** Specifically, repository searches found:

- No `**/recipes/default.rb` files; therefore no Chef cookbooks can be inventoried.
- No `**/manifests/init.pp` files; therefore no Puppet modules can be inventoried.
- No `**/*.psd1` files; therefore no PowerShell modules can be inventoried.

Consequently, there are no module entries or module paths to migrate, and no separate cookbook/module dependency manifests were found. The following existing directories contain supporting files only and must not be treated as cookbook or module directories:

- `chef-and-ansible/`: Ansible, InSpec, and Test Kitchen example files.
- `chef-and-ansible/tests/`: Chef InSpec verification controls.
- `setup-automate/`: Bash bootstrap scripts for Chef server products.

**CRITICAL PATH VERIFICATION:** Every path named above exists in the supplied repository tree. No nonexistent module paths are asserted, and no module has been inferred solely from a filename or directory name.

### Supporting Components and Files

- `chef-and-ansible/website_https.yml`: Existing Ansible playbook. It targets `myhost` as root with privilege escalation, changes Apache's SSL protocol configuration to TLS 1.2, and notifies Apache and SSH service handlers. This is already Ansible configuration, not a Chef cookbook requiring translation.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration using Vagrant, the Ansible Playbook provisioner, the InSpec verifier, and Ubuntu 20.04. It invokes `website_https.yml` and `tests/website_https_verify.rb`.
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec checks for port 443, an HTTPS 200 response containing `Hello, world!`, disabled SSLv3, and enabled TLS 1.2.
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec control checking that SSH root login is not enabled. It includes STIG/SRG/CCI identifiers and an SSH package assertion.
- `chef-and-ansible/poodle_fix.yml`: Existing YAML file that may contain additional TLS-related scope. It should be reviewed during implementation, but it is not a qualifying module entrypoint.
- `chef-and-ansible/index.html`: Web content present in the example directory. Its deployment relationship to the Ansible playbook should be confirmed.
- `chef-and-ansible/README.md`: Describes use of Chef InSpec alongside Ansible for continuous compliance.
- `README.md`: Describes the repository as Chef examples associated with Chef technical content.
- `setup-automate/deploy-automate.sh`: Bash bootstrap for Chef Automate and Chef Infra Server. It sets hostname/kernel values, downloads the Chef Automate CLI, deploys both products, and creates a Chef user and organization.
- `setup-automate/deploy-chef-server.sh`: Bash bootstrap for Chef Infra Server only, with similar hostname, kernel, download, user, organization, and key-generation behavior.

No `Berksfile`, `Policyfile.rb`, `metadata.rb`, or other cookbook dependency manifest was found in the supplied tree. No Puppet or PowerShell dependency manifest was found either.

### Target Details

- **Operating System:** Ubuntu 20.04 is explicitly specified in `chef-and-ansible/kitchen.yml`. The Apache path `/etc/apache2/mods-available/ssl.conf` and service name `apache2` also indicate a Debian/Ubuntu target. Production OS and supported versions are not specified.
- **Virtual Machine Technology:** Vagrant is specified for Test Kitchen. Production virtualization is not specified.
- **Cloud Platform:** Not specified. The bootstrap comments allow on-premises or cloud VMs, but no provider-specific implementation is present.

## Migration Approach

### Key Dependencies to Address

- **Ansible:** Standardize the Ansible Core version and convert the inline playbook into a role if it will be reused. Parameterize Apache paths, service names, and supported protocols.
- **Apache HTTP Server:** Use Ansible package, service, and configuration modules. Preserve Ubuntu-specific values only if Ubuntu remains the supported target.
- **Chef InSpec:** Either retain InSpec as a transitional compliance verifier or translate its HTTPS and SSH assertions to Molecule/testinfra/Goss. Preserve the existing compliance identifiers and security intent.
- **Vagrant/Test Kitchen:** Decide whether to retain Test Kitchen for this example or migrate convergence and verification to Molecule. Keep an Ubuntu-based integration test while production targets are confirmed.
- **Chef Automate/Infra Server CLI:** The shell scripts download the latest CLI from `packages.chef.io`. If Chef remains, pin a version and verify checksums; if Chef is being retired, remove these scripts from the target provisioning path.
- **Chef PEM credentials:** The scripts generate user and organization validator keys. Treat them as secrets and manage them through a controlled secret-management process.

### Security Considerations

- **Hardcoded password:** Both Bash scripts visibly contain `userpassword='password'`. Treat this as compromised, rotate any corresponding account, remove it from source, and use Ansible Vault or an enterprise secret manager with `no_log: true`.
- **Generated PEM files:** `${username}.pem` and `${orgname}-validator.pem` are written locally by the scripts. Restrict permissions, prevent CI/artifact publication, define rotation and revocation procedures, and avoid storing them in ordinary Ansible variables.
- **Unverified remote executable:** The scripts pipe a remote download through `curl`/`gunzip` and execute it. Pin the CLI version, verify a checksum or signature, and prefer a trusted internal artifact source.
- **TLS configuration:** The playbook attempts to disable all protocols except TLS 1.2 and the InSpec test rejects SSLv3. Confirm whether TLS 1.3 should also be enabled for the target Apache/OpenSSL version.
- **SSH access:** The InSpec check validates `PermitRootLogin`, but the reviewed Ansible playbook does not explicitly manage `sshd_config`. Add SSH hardening carefully, validate configuration before restart, and ensure a non-root administrative path exists to avoid lockout.
- **Privilege:** The playbook runs as root and the scripts use `sudo` and kernel tuning. Limit privileges where possible and test kernel changes on representative systems.
- **Certificate and content handling:** No certificate source or private-key deployment mechanism is visible. Establish a secure certificate workflow and confirm how `index.html` is deployed.
- **Compliance evidence:** Preserve the InSpec control metadata, including severity and STIG/SRG/CCI references, if tests are rewritten.

### Technical Challenges

- **No cookbook source exists:** The requested cookbook migration cannot be performed from this repository because no qualifying cookbook entrypoint is present. Confirm whether additional cookbooks exist outside this repository before declaring the migration complete.
- **Ansible handler mismatch:** The playbook notifies `Restart apache2`, while the declared handler is `Restart apache`. Correct the name mismatch and test a changed configuration path.
- **OS-specific configuration:** The Apache path and service naming are Ubuntu-specific. Either constrain the role to Debian-family hosts or add platform-specific defaults and tasks.
- **Incomplete desired state:** The playbook edits one existing file but does not visibly install Apache, enable SSL, deploy the site, manage certificates, or configure SSH. Define ownership of those concerns before expanding the role.
- **Test mismatch:** The test platform is Ubuntu 20.04, while the SSH control carries RHEL 8 STIG identifiers. Separate control intent from OS-specific implementation and test each supported OS explicitly.
- **Ambiguous additional playbook:** `poodle_fix.yml` may duplicate or extend TLS hardening. Review it before creating final roles so TLS logic is not split across parallel implementations.
- **Hybrid platform decision:** Retaining Chef Automate/Infra Server while moving host configuration to Ansible requires clear ownership, inventory, credential, and compliance boundaries.

### Migration Order

1. **Confirm scope:** Verify whether this repository is the complete source and inspect `poodle_fix.yml` and `index.html` for operational scope.
2. **Decide Chef platform strategy:** Determine whether Chef Automate/Infra Server and its Bash bootstrap scripts remain supported or are to be retired.
3. **Secure credentials:** Rotate the visible password if used, remove hardcoded secrets, and establish Vault/secret-manager handling for PEM files and certificates.
4. **Harden the existing Ansible playbook:** Correct the handler mismatch, add required Apache prerequisites, parameterize Ubuntu-specific values, and implement safe SSH configuration if in scope.
5. **Migrate verification:** Keep InSpec during transition or convert the HTTPS and SSH checks to the selected Ansible-native test framework.
6. **Validate in stages:** Run tests in the existing Ubuntu 20.04 Vagrant environment, then a production-like image, followed by a non-production pilot and phased rollout.
7. **Clean up legacy tooling:** Remove or formally retire obsolete Chef bootstrap and Test Kitchen components only after ownership, rollback, and compliance evidence are documented.

### Assumptions

- The supplied repository tree is complete for this request.
- There are no qualifying Puppet modules, Chef cookbooks, or PowerShell modules because the required entrypoint searches found none.
- The existing Ansible playbook is the primary configuration artifact, rather than a converted Chef recipe.
- Ubuntu 20.04 is a test target; production OS support is not yet confirmed.
- Vagrant is a test driver only; production VM and cloud platforms are unknown.
- Apache is intended to exist on target systems, although installation is not shown in the reviewed playbook.
- `poodle_fix.yml` may add scope and must be reviewed before implementation is finalized.
- The literal password may be a demonstration value, but it must be treated as exposed until proven otherwise.
- Chef InSpec may remain temporarily as a compliance verifier, but the long-term test framework is undecided.
- No cookbook dependency graph can be produced because no cookbook metadata or dependency manifests are present.
- No certificate source, inventory system, secret backend, CI configuration, rollback process, or production topology is visible in the supplied tree.
- Timeline estimates cover the visible repository only; undiscovered external cookbooks or production dependencies will increase effort.
