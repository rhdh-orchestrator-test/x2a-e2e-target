# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks designed to demonstrate compliance automation with Ansible. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server setup scripts that will need to be replaced with Ansible equivalents.

Estimated timeline: 1-2 weeks for a single engineer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-setup**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-setup**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used as a test page for the web server. Can be preserved as-is or incorporated into Ansible content.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use the `ansible.builtin.assert` module for basic validation
  - Option 2: Implement Ansible Molecule for comprehensive testing
  - Option 3: Use community.general.test_connection module for network connectivity tests

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for orchestration and control
  - Ansible Content Collections for configuration management
  - Ansible Automation Platform for enterprise features

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook that disables SSLv3 and enables only TLSv1.2.
- **SSH Security**: The SSH root login compliance check must be preserved in the Ansible-native solution.
- **Self-signed Certificates**: The current implementation uses self-signed certificates. Consider implementing proper certificate management using Ansible Vault or external certificate management.
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificate handling should use Ansible Vault for private key storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or Molecule tests will require careful mapping of test functionality.
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules
  - Consider using the `assert` module with appropriate conditions to replicate InSpec tests

- **Chef Automate Functionality**: Replacing Chef Automate's compliance reporting with Ansible-native solutions.
  - Mitigation: Evaluate Ansible AWX/Tower compliance capabilities or integrate with third-party compliance tools

- **Test Kitchen to Molecule**: Converting the test infrastructure from Test Kitchen to Molecule.
  - Mitigation: Create a Molecule configuration that mirrors the existing Test Kitchen setup

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format, may need minor adjustments for best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity to convert to Ansible-native testing
3. **Chef Setup Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity, requires replacing Chef-specific functionality with Ansible equivalents

### Assumptions

1. The primary purpose of this repository is to demonstrate compliance automation using Chef InSpec with Ansible, as indicated in the README.
2. The existing Ansible playbooks are functional and follow best practices, requiring minimal changes.
3. The target environment is Ubuntu 20.04, as specified in the kitchen.yml file.
4. The deployment is intended for testing/demonstration purposes rather than production use, given the self-signed certificates and simple configurations.
5. The hardcoded credentials in the setup scripts are for demonstration purposes and would be replaced with secure credential management in a production environment.
6. The repository does not contain actual Chef cookbooks or recipes that need migration, only InSpec tests and setup scripts.
7. The migration will preserve the existing functionality while moving to Ansible-native solutions for testing and compliance.