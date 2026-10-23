# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository is a **demonstration/examples repository** that already combines Ansible playbooks with Chef InSpec testing profiles. It does not contain traditional Chef cookbooks requiring migration. Instead, it showcases a hybrid approach where:

- **Ansible** is used for infrastructure provisioning and configuration management
- **Chef InSpec** is used for compliance testing and verification
- **Bash scripts** deploy Chef infrastructure components (Automate and Infra Server)

**Migration Scope**: MINIMAL - This repository is already primarily Ansible-based. The only migration considerations involve:
1. Replacing Chef InSpec tests with Ansible-native testing solutions (if desired)
2. Converting bash deployment scripts to Ansible playbooks (if desired)

**Complexity**: LOW - No Chef cookbooks exist to migrate

**Timeline Estimate**: 1-2 weeks (if choosing to migrate InSpec tests and deployment scripts)

**Key Finding**: This is a "chef-examples" repository that demonstrates compliance automation patterns, not a production Chef infrastructure requiring migration.

## Module Migration Plan

This repository does NOT contain Chef cookbooks or traditional modules requiring migration. It contains:

### MODULE INVENTORY

**No Chef Cookbooks Found**

The repository structure analysis revealed:
- No `metadata.rb` or `metadata.json` files (Chef cookbook metadata)
- No `recipes/` directories with `.rb` files
- No `Berksfile` or `Policyfile.rb` (Chef dependency management)
- No traditional Chef cookbook structure

### Infrastructure Files

The repository contains the following components:

#### Ansible Playbooks (Already Migrated)
- **`chef-and-ansible/website_https.yml`**: Complete Ansible playbook that configures Apache web server with HTTPS/SSL support on Ubuntu 20.04. Includes certificate generation, virtual host configuration, and service management. This playbook is production-ready Ansible code.
  - Installs Apache 2.4.41-4ubuntu3.10
  - Generates self-signed SSL certificates using OpenSSL
  - Configures SSL virtual host on port 443
  - Deploys "Hello, world!" test website
  - Uses handlers for service restarts

- **`chef-and-ansible/poodle_fix.yml`**: Ansible playbook that remediates the POODLE SSL vulnerability by enforcing TLS 1.2 only in Apache configuration. Modifies `/etc/apache2/mods-available/ssl.conf` to disable older SSL protocols.
  - Uses `replace` module for configuration file updates
  - Restarts Apache2 and SSH services via handlers

#### Chef InSpec Test Profiles
- **`chef-and-ansible/tests/website_https_verify.rb`**: InSpec profile that validates HTTPS website deployment
  - Verifies port 443 is listening
  - Tests HTTP 200 response from localhost
  - Validates "Hello, world!" content
  - Ensures SSLv3 is disabled
  - Confirms TLS 1.2 is enabled

- **`chef-and-ansible/tests/ssh_profile.rb`**: InSpec compliance profile for SSH hardening
  - Validates PermitRootLogin is disabled
  - Mapped to STIG requirements (RHEL-08-000227, V-38607)
  - CAT I severity control
  - CCI-000774 compliance mapping

#### Test Kitchen Configuration
- **`chef-and-ansible/kitchen.yml`**: Test Kitchen configuration using Vagrant driver with Ansible provisioner
  - Provisions Ubuntu 20.04 VMs
  - Uses Ansible playbook provisioner (not Chef)
  - Uses InSpec verifier for compliance testing
  - Modern testing workflow combining Ansible + InSpec

#### Deployment Scripts
- **`setup-automate/deploy-automate.sh`**: Bash script that deploys Chef Automate and Chef Infra Server
  - Installs chef-automate CLI
  - Deploys both Automate and Infra Server products
  - Creates admin user and organization
  - Hardcoded credentials: username 'jtonello', password 'password', org 'lab'
  - **Security Risk**: Contains plaintext credentials

- **`setup-automate/deploy-chef-server.sh`**: Bash script that deploys standalone Chef Infra Server
  - Similar to above but without Automate component
  - Same credential management issues
  - **Security Risk**: Contains plaintext credentials

#### Static Content
- **`chef-and-ansible/index.html`**: Simple HTML test page with "Hello, world!" content

### Target Details

Based on the existing Ansible playbooks and test configurations:

- **Operating System**: Ubuntu 20.04 LTS (explicitly specified in kitchen.yml and playbooks)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - designed for local development/testing with potential for cloud deployment
- **Package Manager**: APT (Ubuntu/Debian)
- **Web Server**: Apache 2.4.41-4ubuntu3.10 with SSL/TLS support
- **Python Version**: Python 3.x (uses python3-openssl package)

## Migration Approach

### Key Dependencies to Address

**No Chef Cookbook Dependencies** - The repository does not use Chef for configuration management.

However, the following tools are currently in use:

- **Chef InSpec (Ruby-based)**: Currently used for compliance testing
  - **Migration Strategy**: Consider replacing with Ansible-native testing tools:
    - Option 1: Keep InSpec (it works well with Ansible as demonstrated)
    - Option 2: Migrate to `ansible-lint` + `molecule` for testing
    - Option 3: Use `testinfra` (Python-based pytest plugin)
    - Option 4: Native Ansible assertions with `assert` module

- **Test Kitchen**: Infrastructure testing framework
  - **Migration Strategy**: Replace with Molecule (Ansible's native testing framework)
  - Molecule provides similar functionality with better Ansible integration

- **chef-automate CLI**: Used in deployment scripts
  - **Migration Strategy**: If migrating deployment scripts to Ansible, no replacement needed
  - If keeping Chef infrastructure, retain as-is

### Security Considerations

#### Critical Security Issues Found

1. **Hardcoded Credentials in Deployment Scripts**
   - **Location**: `setup-automate/deploy-automate.sh` and `deploy-chef-server.sh`
   - **Issues**: 
     - Plaintext password: 'password'
     - Username: 'jtonello'
     - Email: 'jtonello@chef.lab'
   - **Migration Approach**: 
     - Convert to Ansible playbook using `ansible-vault` for credential encryption
     - Use Ansible variables with vault-encrypted values
     - Implement proper secret management (HashiCorp Vault, AWS Secrets Manager, etc.)

2. **Self-Signed SSL Certificates**
   - **Location**: Generated by `website_https.yml` playbook
   - **Issue**: Suitable for testing but not production
   - **Migration Approach**: 
     - For production: Integrate Let's Encrypt via `certbot` or ACME protocol
     - Use Ansible `community.crypto` collection for certificate management
     - Consider certificate rotation automation

3. **SSH Root Login Remediation**
   - **Current State**: Tested via InSpec profile but not enforced by playbooks
   - **Migration Approach**: 
     - Add Ansible tasks to explicitly disable PermitRootLogin in `/etc/ssh/sshd_config`
     - Use `lineinfile` or `template` module
     - Ensure idempotency

4. **SSL/TLS Protocol Configuration**
   - **Current State**: POODLE fix playbook enforces TLS 1.2 only
   - **Migration Approach**: 
     - Consider updating to support TLS 1.2 and 1.3 (disable 1.0, 1.1, and SSLv3)
     - Template-based approach for more comprehensive SSL configuration
     - Add cipher suite hardening

### Technical Challenges

#### Challenge 1: InSpec Test Migration Decision
**Description**: The repository uses Chef InSpec for compliance testing, which is a mature and well-supported tool that works seamlessly with Ansible.

**Mitigation Strategy**:
- **Recommendation**: KEEP Chef InSpec for compliance testing
- **Rationale**: 
  - InSpec is technology-agnostic and works with any configuration management tool
  - Industry-standard for compliance-as-code
  - Extensive library of pre-built compliance profiles (CIS, STIG, etc.)
  - No need to rewrite working compliance tests
- **Alternative**: If organization policy prohibits Chef tools, migrate to Molecule + Testinfra
  - Timeline: 1 week to rewrite existing InSpec controls
  - Risk: Loss of STIG mapping metadata

#### Challenge 2: Test Kitchen vs. Molecule
**Description**: Repository uses Test Kitchen with Ansible provisioner, but Molecule is the Ansible-native testing framework.

**Mitigation Strategy**:
- Convert `kitchen.yml` to Molecule scenarios
- Maintain same test flow: provision → verify
- Keep InSpec as verifier or switch to Testinfra
- Timeline: 2-3 days
- Low risk - both frameworks have similar concepts

#### Challenge 3: Bash Script Automation
**Description**: Deployment scripts for Chef Automate/Server are written in Bash with hardcoded credentials.

**Mitigation Strategy**:
- Create Ansible playbook: `deploy_chef_infrastructure.yml`
- Use roles: `chef_automate`, `chef_server`
- Externalize all variables to group_vars/host_vars
- Encrypt secrets with ansible-vault
- Timeline: 3-4 days
- Risk: Medium - requires testing Chef Automate deployment process

#### Challenge 4: Repository Purpose Clarification
**Description**: This is an examples/demonstration repository, not production infrastructure.

**Mitigation Strategy**:
- Clarify whether actual migration is needed or if this is educational
- If educational: Focus on improving existing examples
- If production use is intended: Harden security, externalize configs
- Document that this repo already uses Ansible (no Chef cookbook migration needed)

### Migration Order

Given that this repository is already Ansible-based, the following improvements are recommended in priority order:

#### Phase 1: Security Hardening (Priority: CRITICAL)
1. **Vault-encrypt deployment credentials** (1 day)
   - Create ansible-vault encrypted files for all secrets
   - Remove hardcoded credentials from bash scripts

2. **SSH hardening playbook** (1 day)
   - Add Ansible tasks to disable root login
   - Align playbook with InSpec compliance tests

#### Phase 2: Testing Framework Modernization (Priority: HIGH)
3. **Migrate Test Kitchen to Molecule** (2-3 days)
   - Create Molecule scenarios for each playbook
   - Maintain InSpec as verifier
   - Document testing workflow

#### Phase 3: Deployment Automation (Priority: MEDIUM)
4. **Convert deployment scripts to Ansible** (3-4 days)
   - Create `roles/chef_automate` and `roles/chef_server`
   - Parameterize all configurations
   - Add idempotency checks

#### Phase 4: Documentation & Knowledge Transfer (Priority: MEDIUM)
5. **Update documentation** (2 days)
   - Clarify repository purpose
   - Document Ansible + InSpec workflow
   - Add architecture diagrams

### Assumptions

1. **Repository Purpose**: This repository is assumed to be a demonstration/examples repository for educational purposes, not production infrastructure. If this is production infrastructure, additional hardening and testing would be required.

2. **Chef InSpec Retention**: It is assumed that Chef InSpec can be retained for compliance testing, as it is technology-agnostic and works well with Ansible. If organizational policy prohibits any Chef tooling, additional migration effort is required.

3. **Chef Infrastructure Requirement**: The deployment scripts suggest a need for Chef Automate and/or Chef Infra Server. The purpose of these servers (demo environment, production Chef infrastructure, compliance scanning) is unclear and should be clarified.

4. **Target Audience**: The repository appears to target users evaluating Chef InSpec for compliance automation with Ansible. If the actual use case differs, migration priorities may change.

5. **No Legacy Chef Cookbooks**: It is confirmed that no Chef cookbooks exist in this repository. Any legacy Chef cookbooks would be in a separate repository and would require traditional Chef-to-Ansible migration.

6. **Testing Environment**: The Test Kitchen configuration assumes local Vagrant/VirtualBox testing. Production deployment targets are not specified.

7. **SSL Certificate Strategy**: Self-signed certificates are acceptable for demo/testing purposes. Production deployments would require a proper PKI or ACME/Let's Encrypt integration.

8. **Compliance Requirements**: InSpec profiles reference DISA STIG controls, suggesting DoD/government compliance requirements may apply. If true, additional compliance controls beyond those demonstrated may be necessary.

9. **Network Connectivity**: Deployment scripts download packages from the internet (chef.io, packages.ubuntu.com). Air-gapped or restricted network environments would require additional mirror/repository configuration.

10. **Version Currency**: The playbooks specify specific package versions (Apache 2.4.41-4ubuntu3.10, Ubuntu 20.04). These may be outdated and should be updated to current stable versions before production use.

11. **Access to Chef Packages**: The deployment scripts assume unrestricted access to Chef package repositories. Licensing and access credentials for Chef commercial products (Automate) are not addressed.

12. **Idempotency**: While Ansible playbooks are generally idempotent, the bash deployment scripts are not. Re-running them may cause failures or inconsistent state.

## Conclusion

**This repository does NOT require Chef-to-Ansible migration** because it is already Ansible-based. The repository demonstrates a modern compliance automation pattern using Ansible for configuration management and Chef InSpec for compliance verification.

**Recommended Action**: Focus on security hardening (vault encryption), testing framework modernization (Molecule), and documentation improvements rather than a traditional "migration."

**If actual Chef cookbooks exist elsewhere**: A separate migration effort would be required following traditional Chef-to-Ansible migration patterns (recipes → tasks, attributes → variables, templates → templates, etc.). This repository provides no cookbooks to migrate.
