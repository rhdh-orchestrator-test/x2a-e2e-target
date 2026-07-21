# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mixed environment with Chef InSpec tests and Ansible playbooks. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The repository also includes scripts for deploying Chef Automate and Chef Infra Server.

After thorough analysis, no traditional Chef cookbooks (with recipes/default.rb), Puppet modules (with manifests/init.pp), or PowerShell modules (.psd1) were found in the repository. The repository primarily consists of Ansible playbooks with Chef InSpec tests and deployment scripts for Chef infrastructure.

The migration scope is relatively small, as the repository primarily contains Ansible playbooks already, with Chef InSpec being used for testing. The migration will focus on replacing Chef InSpec tests with Ansible-native testing solutions while preserving the existing Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium

## Module Migration Plan

This repository contains a mix of Ansible playbooks, Chef InSpec tests, and deployment scripts that need individual migration planning:

### MODULE INVENTORY

Note: No traditional Chef cookbooks (with recipes/default.rb), Puppet modules (with manifests/init.pp), or PowerShell modules (.psd1) were found in this repository. The following components were identified:

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance tagging (STIG, CCI)

- **automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Static HTML content for the website. Can be preserved as-is or converted to a template.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - For basic tests: Use Ansible's `assert` module and `command`/`shell` modules with `register` and conditional checks
  - For more complex compliance testing: Consider Ansible Lint, Molecule, or Ansible's built-in `--check` mode
  - For comprehensive compliance: Consider migrating to OpenSCAP with Ansible integration

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality for testing Ansible roles with different drivers (Vagrant, Docker, etc.)
  - Existing Vagrant configuration can be adapted to Molecule

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure the same security settings are maintained in the migrated Ansible roles.
  - The POODLE fix specifically disables SSLv3 and enables only TLSv1.2, which should be preserved.

- **SSH Security**: The SSH compliance profile checks for root login restrictions. Ensure this security check is maintained in the Ansible-based testing.

- **Vault/secrets management**:
  - Hardcoded credentials in the deployment scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated on the fly; consider using Ansible Vault for pre-generated certificates or sensitive key material

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require understanding the compliance requirements and implementing equivalent checks.
  - Challenge: InSpec has built-in resources for checking services, ports, and configurations that may require custom implementation in Ansible.
  - Mitigation: Use Ansible's `assert` module with appropriate modules like `command`, `shell`, or specialized modules like `uri` to perform equivalent checks.

- **Chef Automate/Server Deployment**: The deployment scripts for Chef Automate and Chef Server will need to be completely rewritten as Ansible playbooks.
  - Challenge: Ensuring all configuration options and settings are properly translated.
  - Mitigation: Create Ansible roles for Chef server deployment if still needed, or replace with Ansible AWX/Tower for similar functionality.

### Migration Order

1. **website_https.yml** and **poodle_fix.yml** (low risk, already Ansible)
   - Convert to proper Ansible roles with variables, templates, and handlers
   - Improve idempotence where needed

2. **InSpec Tests** (moderate complexity)
   - Convert website_https_verify.rb to Ansible assertions or Molecule tests
   - Convert ssh_profile.rb to Ansible security checks or OpenSCAP integration

3. **Deployment Scripts** (high complexity)
   - Convert deploy-automate.sh and deploy-chef-server.sh to Ansible playbooks
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment.
2. The deployment scripts for Chef Automate and Chef Server are examples and not actively used in production.
3. The security compliance requirements (STIG, CCI) mentioned in the InSpec tests are important and must be maintained in the Ansible migration.
4. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs.
5. There are no external dependencies or integrations not visible in the repository.
6. The migration will completely replace Chef components with Ansible equivalents rather than maintaining a hybrid approach.