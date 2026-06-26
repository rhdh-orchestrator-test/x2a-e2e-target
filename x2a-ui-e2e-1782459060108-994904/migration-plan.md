# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting the existing Chef InSpec tests to Ansible-native solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server setup scripts that will need to be replaced with Ansible-based deployment solutions.

**Estimated Timeline**: 1-2 weeks for a single developer, considering the limited scope of the repository.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies the HTTPS website is properly configured
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration verification, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used as a template for the website. Can be preserved as-is or converted to an Ansible template.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, but the setup scripts mention they can be used for on-prem or cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Use Molecule for more comprehensive testing
  - Option 3: Consider integrating with other compliance tools like OpenSCAP or Ansible's built-in `--check` mode

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or Jenkins for pipeline automation
  - Ansible Vault for secrets management

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook that disables vulnerable SSL protocols
- **SSH Hardening**: The SSH compliance checks in ssh_profile.rb need to be implemented in Ansible
- **Vault/secrets management**:
  - Hardcoded credentials in the setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated on the fly in the playbook, which is acceptable for testing but should use proper certificate management for production

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or Molecule tests will require careful mapping of test functionality
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules
  
- **Chef Automate Replacement**: Finding equivalent functionality in Ansible ecosystem
  - Mitigation: Evaluate AWX/Tower features against Chef Automate requirements

- **Compliance Reporting**: Chef InSpec provides rich compliance reporting that needs an equivalent in the Ansible ecosystem
  - Mitigation: Explore integration with compliance tools like OpenSCAP or custom reporting solutions

### Migration Order

1. **website_https.yml and poodle_fix.yml**: These are already Ansible playbooks and require minimal changes
2. **InSpec Tests**: Convert the InSpec tests to Ansible-native testing solutions
3. **Chef Deployment Scripts**: Replace with Ansible playbooks for deploying alternative solutions

### Assumptions

1. The primary purpose of this repository is demonstrating compliance testing alongside configuration management
2. The existing Ansible playbooks are functional and follow best practices
3. There is no dependency on Chef-specific features that cannot be replicated in Ansible
4. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
5. The hardcoded credentials in the setup scripts are for demonstration purposes only
6. The self-signed certificates are acceptable for the demonstration environment
7. The repository is not used in production environments
8. There are no external dependencies or integrations not visible in the repository
9. The migration will preserve the functionality of the existing playbooks and tests
10. The SSH compliance check is a standalone example and not part of a larger compliance framework