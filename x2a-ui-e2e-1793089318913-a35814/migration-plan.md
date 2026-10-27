# MIGRATION FROM CHEF/ANSIBLE HYBRID CONFIGURATION TO ANSIBLE

This repository is already partially implemented in Ansible rather than being a conventional Chef cookbook repository. The main configuration workload consists of two Ansible playbooks: one provisions an Apache HTTPS “Hello World” site and the other hardens Apache TLS. The surrounding material uses Chef InSpec for verification and Bash scripts to install Chef Automate and/or Chef Infra Server. There are no Puppet manifests, Chef cookbooks, Chef recipes, Berksfiles, Policyfiles, or module metadata files in the reviewed tree.

The migration is therefore primarily a consolidation and modernization effort: retain or refactor the existing Ansible configuration, replace Chef-specific platform components and InSpec verification where desired, and establish secure Ansible inventories, roles, secrets handling, and CI/CD. A small team should be able to complete a production-ready first iteration in approximately 2–4 weeks, assuming the target hosts and certificate requirements are known. Extending this into a hardened, multi-environment platform with replacement compliance tooling may require 4–8 weeks.

## Module Migration Plan

This repository contains a small Ansible configuration set supported by Chef InSpec tests and Chef platform bootstrap scripts that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only paths present in the supplied repository tree are included below.

- **website_https**:
    - Description: An Ansible playbook for Ubuntu Apache deployment that installs Apache and OpenSSL-related packages, creates a Hello World document root, generates a private key/CSR/self-signed certificate, configures an SSL virtual host, enables the site and SSL module, and restarts services.
    - Path: `chef-and-ansible/website_https.yml`
    - Technology: Ansible
    - Key Features: Apache 2.4 package pinning, HTTPS virtual host, locally generated TLS material, inline virtual-host and HTML content, site/module activation, service handlers

- **poodle_fix**:
    - Description: An Ansible playbook that changes Apache’s SSL protocol configuration to allow TLS 1.2 and remove other protocols, then restarts Apache and SSH.
    - Path: `chef-and-ansible/poodle_fix.yml`
    - Technology: Ansible
    - Key Features: TLS protocol hardening through a configuration replacement, service notifications, legacy POODLE-oriented remediation

- **chef_automate_bootstrap**:
    - Description: A Bash bootstrap script that sets a hostname and kernel parameters, downloads the latest Chef Automate CLI, deploys Chef Automate with Chef Infra Server, and creates a Chef user and organization with generated key files.
    - Path: `setup-automate/deploy-automate.sh`
    - Technology: Bash/Chef Automate/Chef Infra Server
    - Key Features: On-premises or cloud VM bootstrap, Chef platform deployment, organization/user creation, validator and user key generation

- **chef_infra_server_bootstrap**:
    - Description: A Bash bootstrap script that performs the same host preparation and user/organization setup but deploys Chef Infra Server without Chef Automate.
    - Path: `setup-automate/deploy-chef-server.sh`
    - Technology: Bash/Chef Infra Server
    - Key Features: Chef Infra Server installation, hostname and kernel tuning, organization initialization, credential/key-file generation

### Infrastructure Files

- `README.md`: Repository-level description of Chef-related examples. It provides context but no executable configuration.
- `chef-and-ansible/README.md`: Describes the examples as Chef InSpec compliance examples used alongside Ansible; useful context for the verification migration.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration using the Vagrant driver, Ansible Playbook provisioner, Ubuntu 20.04 platform, and InSpec verifier. It is the clearest statement of the current test target and should be converted to an Ansible-native test workflow or retained temporarily as a compatibility harness.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec acceptance checks for HTTPS availability, Hello World content, disabled SSLv3, and enabled TLS 1.2.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec compliance check concerning SSH root login. It is not wired into the shown Kitchen suite and contains an unusual alternative assertion that treats an absent OpenSSH server package as acceptable.
- `chef-and-ansible/index.html`: Repository asset whose exact role is not established by the reviewed files; determine whether it duplicates the inline web content before migration.
- `setup-automate/deploy-automate.sh`: Chef Automate/Infra Server bootstrap entrypoint; migrate only if Chef platform services are still required.
- `setup-automate/deploy-chef-server.sh`: Chef Infra Server-only bootstrap entrypoint; likely removable if Ansible replaces Chef as the control plane.

### Target Details

- **Operating System**: Ubuntu 20.04 is explicitly used by the Test Kitchen platform and the playbook pins `apache2` to `2.4.41-4ubuntu3.10`, so Ubuntu 20.04 is the current target. The InSpec SSH profile references RHEL 8 compliance identifiers, but that does not establish a RHEL deployment target. Validate whether Ubuntu 20.04 remains supported; otherwise parameterize for the approved Ubuntu LTS and/or RHEL 9 equivalents.
- **Virtual Machine Technology**: Vagrant is specified in `kitchen.yml`; the underlying provider is not specified.
- **Cloud Platform**: Not specified. The Chef bootstrap comments say on-premises or cloud VM, but no provider SDK, metadata endpoint, or cloud-specific resource is present.

## Migration Approach

1. Establish the target inventory and supported OS matrix, then run the existing playbooks in a disposable environment to document current behavior.
2. Refactor each playbook into an Ansible role, separating defaults, variables, handlers, templates, certificate tasks, and site content. Use `ansible.builtin` modules wherever available.
3. Replace shell commands such as `a2ensite`, `a2dissite`, and `a2enmod` with idempotent Apache modules or carefully controlled commands, and validate handlers so only necessary services restart.
4. Move certificate generation and deployment into an explicit certificate role. Use environment-specific certificates for production rather than generating self-signed certificates on every host.
5. Convert the InSpec checks into the organization’s chosen Ansible-compatible validation approach, such as Molecule plus Testinfra/pytest, Ansible assertions, or a retained InSpec gate if compliance policy requires it.
6. Decide whether Chef Automate and Chef Infra Server remain required. If not, retire both bootstrap scripts and remove the operational dependency on Chef keys and server-side organizations. If they remain, manage them as a separate platform deployment rather than as part of the Apache role.
7. Add CI checks for YAML syntax, ansible-lint, idempotence, TLS verification, and supported operating systems. Document ownership, rollback, and promotion between environments.

### Key Dependencies to Address

- **Ubuntu 20.04 and APT**: The playbook relies on `apt` and an exact Apache package version. Replace the hard-coded version with a tested variable or repository policy, and define behavior when that version is unavailable.
- **Apache HTTP Server**: Migrate to an Ansible role using package, template, module/site enablement, and service management. Parameterize document root, virtual-host name, ports, and certificate paths.
- **OpenSSL and Python OpenSSL support**: The playbook installs `openssl` and `python3-openssl` and uses `openssl_privatekey`, `openssl_csr`, and `openssl_certificate`. Confirm the installed `community.crypto` collection and use fully qualified, current module names.
- **Vagrant/Test Kitchen**: Current acceptance execution uses Vagrant and the Ansible provisioner. Retain Vagrant for local testing or replace Kitchen with Molecule and a supported driver; do not assume the Vagrant provider from the current files.
- **Chef InSpec**: Existing tests verify HTTPS, page content, SSLv3 disablement, and TLS 1.2. Port these checks to the chosen Ansible test framework or keep InSpec as an external compliance gate during transition.
- **Chef Automate CLI and Chef Infra Server**: The bootstrap scripts download the latest CLI from Chef’s package site and invoke Chef server commands. These are external control-plane dependencies, not application modules; either retire them or pin and separately govern their versions and installation source.
- **Host kernel settings**: The Chef bootstrap scripts set `vm.max_map_count` and `vm.dirty_expire_centisecs`. If Chef services remain, represent these as explicit Ansible `sysctl` tasks with persistence and validation.

### Security Considerations

- **Hard-coded credentials**: Both Chef bootstrap scripts contain a literal user password and personal identity values. Remove these values immediately from source control, rotate any exposed credentials, and use Ansible Vault, an external secret manager, or short-lived provisioning credentials.
- **Generated Chef keys**: The scripts create user and organization `.pem` files. Define their ownership, mode, storage, distribution, rotation, and deletion policy. If Chef is retired, revoke or securely destroy obsolete keys.
- **Untrusted download/install path**: The scripts pipe a download from `packages.chef.io` through `gunzip` and execute the result. Pin a known version, verify checksums/signatures, use a controlled artifact repository, and avoid executing an unverified pipeline.
- **TLS private key handling**: The Apache key is generated on the host, but the directory is created with mode `0640`, which may be too permissive or unusable depending on ownership and the Apache process. Set explicit owner/group and restrictive private-key permissions; protect backups and logs.
- **Self-signed certificates**: The HTTPS playbook creates a self-signed certificate with `common_name: myhost`. This is suitable only for testing. Production migration must use an approved CA, correct SANs, renewal automation, and certificate expiry monitoring.
- **TLS policy**: The intended policy disables SSLv3 and enables TLS 1.2, but it does not address TLS 1.3, cipher suites, headers, certificate validation, or modern Apache defaults. Test the final policy against organizational standards and supported OpenSSL/Apache versions.
- **SSH restart behavior**: The playbooks restart `sshd` while making no SSH configuration change in the reviewed tasks. Remove unnecessary SSH restarts to reduce lockout risk, and use connection-safe validation when SSH hardening is added.
- **Privilege and file permissions**: Both playbooks run as root with `become: yes`; constrain inventory access, use least privilege where practical, and define modes explicitly for configuration, certificates, and web content.
- **Compliance profile gap**: `ssh_profile.rb` checks that root login is not allowed, but it is not included in the shown Kitchen suite and does not itself enforce the setting. Add an explicit Ansible hardening role and a verified test if this requirement is in scope.

### Technical Challenges

- **Existing code is not a standard Chef module inventory**: There are no cookbooks or Chef module entrypoints to translate. The work is a hybrid consolidation rather than a direct recipe-to-role conversion. Establish ownership and intended lifecycle for each script/playbook first.
- **Idempotence and portability**: Raw `command` calls for Apache site/module activation and broad `replace` operations may not be fully idempotent or portable across distributions. Replace them with native modules, templates, and distribution-specific variables, then run repeated convergence tests.
- **Version drift**: `ansible_version: latest`, an exact Ubuntu Apache package, and a “latest” Chef CLI create non-reproducible builds. Pin supported Ansible collections, OS images, package repositories, and any retained Chef artifacts.
- **Apache configuration correctness**: Inline configuration includes legacy directives such as `allow from all` alongside `Require all granted`, and the HTML contains a malformed closing `</head>` tag. Validate Apache syntax and migrate configuration/content into reviewed templates/files.
- **Certificate lifecycle**: Moving from test self-signed certificates to production CA certificates introduces issuance, renewal, SAN, trust-chain, and rollback requirements. Assign certificate ownership before implementation.
- **Testing mismatch**: The test platform is Ubuntu 20.04 while the SSH profile cites RHEL 8 STIG identifiers. Define whether the compliance target is Ubuntu, RHEL, or both and build an OS-specific test matrix.
- **Control-plane retirement decision**: Removing Chef Infra Server/Automate may affect existing users, organizations, keys, policy, or reporting outside this repository. Inventory external consumers before deleting the bootstrap path.

### Migration Order

1. **Baseline and security containment**: Remove/rotate hard-coded credentials, inventory any exposed Chef keys, pin test dependencies, and capture current behavior in Vagrant.
2. **`website_https` role**: Refactor the existing Apache installation, content, virtual host, and certificate tasks into an idempotent role. This is the main functional workload and provides the migration baseline.
3. **`poodle_fix` hardening**: Integrate TLS policy into the Apache role or a reusable web-security role, correcting handler names and validating configuration before reload/restart.
4. **Verification migration**: Port `website_https_verify.rb` checks and the relevant SSH control into Molecule/Testinfra or the selected compliance pipeline. Add syntax, idempotence, and negative TLS tests.
5. **Platform bootstrap decision**: If Chef is being retired, decommission and document the two Chef bootstrap scripts after external dependency review. If retained, create a separately owned Ansible role/playbook for Chef platform deployment with secure secrets and pinned artifacts.
6. **Multi-environment rollout**: Promote from disposable Vagrant instances to staging and production, with change approval, rollback procedures, and team handoff documentation.

### Assumptions

- The supplied tree is complete; no omitted cookbooks, Berksfiles, Policyfiles, inventories, or secrets repositories are assumed.
- `website_https.yml` and `poodle_fix.yml` are the only configuration modules requiring direct Ansible migration.
- The repository’s purpose is example/demo content, although the embedded credentials and bootstrap scripts require production-grade handling if ever executed.
- Ubuntu 20.04 is the intended current test OS because it is explicitly declared in Kitchen; target OS support beyond that must be confirmed.
- Vagrant is used for local test VMs, but its provider and production virtualization platform are unknown.
- No cloud provider is selected.
- The Apache version pin may become unavailable from current Ubuntu repositories and must be validated before rollout.
- The exact Ansible version and collection versions are not pinned; compatibility with the current crypto modules must be tested.
- The intended certificate authority, DNS name, SAN requirements, and renewal process are unspecified.
- It is unclear whether Chef Automate/Infra Server are migration targets to retain or legacy demonstration artifacts to remove.
- It is unclear whether `index.html` is used by any workflow because the playbook embeds its own page content.
- `ssh_profile.rb` is not referenced by the displayed Kitchen suite, so its enforcement status is unknown.
- No inventory, group variables, environment separation, CI pipeline, rollback plan, or secret backend is present in the reviewed files.
- Timeline estimate assumes access to target hosts, authority to rotate credentials, and a team familiar with Ansible, Apache, TLS, and the existing Chef platform.

