# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

This repository contains a mix of Ansible playbooks, Chef InSpec tests, and Chef deployment scripts that need to be migrated to a pure Ansible solution.

## Module Migration Plan

This repository contains the following technologies that need individual migration planning:

### MODULE INVENTORY

No traditional modules (Puppet manifests/init.pp, Chef recipes/default.rb, or PowerShell .psd1 files) were found in this repository. The repository contains:

- **website_https**:
    - Description: Ansible playbook that configures Apache with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3, enables TLSv1.2

- **InSpec Tests**:
    - Description: Compliance tests for web server and SSH configuration
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSH security compliance

- **Chef Deployment Scripts**:
    - Description: Scripts to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash/Chef
    - Key Features: Chef infrastructure setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible and InSpec integration
- `index.html`: Static web content template

### Target Details

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible testing frameworks (assert module or Molecule)
- **Test Kitchen**: Replace with Ansible Molecule for testing
- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower

### Security Considerations

- **SSL Configuration**: Maintain TLSv1.2 enforcement, consider Let's Encrypt integration
- **SSH Security**: Convert InSpec SSH tests to Ansible assertions
- **Vault/secrets management**: Replace hardcoded credentials in deployment scripts with Ansible Vault

### Technical Challenges

- **InSpec Test Conversion**: Converting compliance tests to Ansible format
- **Chef Automate Replacement**: Finding equivalent Ansible solution for compliance reporting

### Migration Order

1. **Ansible Playbooks**: Already in Ansible format, minor updates needed
2. **InSpec Tests**: Convert to Ansible-compatible testing
3. **Chef Deployment Scripts**: Replace with Ansible AWX/Tower deployment

### Assumptions

- Repository is for demonstration purposes
- InSpec tests verify systems managed by Ansible
- Target environment is Ubuntu 20.04 on Vagrant VMs
- No complex external dependencies exist