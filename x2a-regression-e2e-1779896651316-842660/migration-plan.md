# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting the Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Server deployment scripts that will need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Simple HTML file used for testing the web server. Can be preserved as-is or included in Ansible content.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - **Option 1**: Use Ansible's `assert` module for basic testing within playbooks
  - **Option 2**: Use Molecule for more comprehensive testing (recommended)
  - **Option 3**: Use pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Server**: Replace deployment scripts with Ansible playbooks that:
  - Set system parameters (hostname, sysctl values)
  - Install alternative compliance and infrastructure management tools

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening that disables SSLv3 and enables only TLSv1.2
  - Migration approach: Preserve the same Apache configuration settings in the Ansible playbooks

- **SSH Security**: The SSH root login check must be maintained
  - Migration approach: Convert the InSpec control to an Ansible task that verifies the same configuration

- **Self-signed Certificates**: The current implementation uses self-signed certificates
  - Migration approach: Use Ansible's `openssl_*` modules as already implemented in the existing playbook

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Use Ansible Vault to secure these credentials

### Technical Challenges

- **Compliance Testing**: Converting InSpec tests to Ansible-native testing solutions
  - Mitigation: Use Ansible's `assert` module combined with `command`/`shell` modules to perform similar checks
  - For more complex tests, consider using Molecule with testinfra or pytest-ansible

- **STIG Compliance**: The InSpec SSH test includes STIG references and metadata
  - Mitigation: Ensure this metadata is preserved in comments or documentation within the Ansible playbooks

- **Test Kitchen Integration**: Replacing Test Kitchen with Molecule
  - Mitigation: Create equivalent Molecule scenarios that test the same functionality

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk as they can remain largely unchanged
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Convert to Ansible-native testing
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - Convert to Ansible playbooks
4. **Test Infrastructure** (kitchen.yml) - Replace with Molecule configuration

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependencies while preserving the same testing capabilities
2. The existing Ansible playbooks can remain largely unchanged
3. The deployment scripts for Chef Automate and Chef Server will be replaced with equivalent functionality using alternative tools
4. The target environment will continue to be Ubuntu 20.04 running on Vagrant
5. No additional security requirements beyond what's already implemented
6. No integration with external systems beyond what's visible in the repository
7. The hardcoded credentials in the deployment scripts are for demonstration purposes only
8. The self-signed certificates are acceptable for the use case