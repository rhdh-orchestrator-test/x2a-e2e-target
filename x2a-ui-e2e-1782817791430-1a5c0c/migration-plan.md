# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used for compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The migration will involve consolidating these technologies into a pure Ansible solution, leveraging Ansible's native testing capabilities or integrating with other testing frameworks.

The migration complexity is relatively low as the repository contains only a few Ansible playbooks and InSpec tests. The estimated timeline for migration is 1-2 weeks, including testing and validation.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2 in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Security hardening for Apache SSL configuration

- **website_https_verify**:
    - Description: Chef InSpec test that verifies the HTTPS website is properly configured and accessible
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

- **automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing approach.
- `index.html`: Sample HTML file used for testing the web server deployment.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's built-in assert module or integrate with Molecule for testing
- **Test Kitchen**: Replace with Molecule for Ansible role testing
- **Vagrant**: Can continue to be used with Molecule for local testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and only enables TLSv1.2
- **SSH Security**: The SSH root login restriction must be preserved in the migrated solution
- **Self-signed Certificates**: The process for generating self-signed certificates should be maintained or improved
- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - No encrypted data bags or Chef Vault usage detected
  - SSL certificate generation should be secured in the Ansible implementation

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible assertions or Molecule tests will require careful mapping of test logic
- **Compliance Reporting**: If compliance reporting is a requirement, consider integrating with Ansible Tower/AWX or another compliance tool to replace Chef Automate functionality
- **Chef Server Replacement**: The Chef Server deployment scripts will need to be replaced with Ansible roles for configuration management

### Migration Order

1. **website_https playbook** (low risk, already in Ansible)
2. **poodle_fix playbook** (low risk, already in Ansible)
3. **InSpec tests** (moderate complexity, requires conversion to Ansible testing framework)
4. **Chef deployment scripts** (high complexity, requires complete rewrite as Ansible roles)

### Assumptions

1. The primary purpose of this repository is for demonstration and educational purposes, as indicated by the README.md mentioning it's related to a white paper.
2. The Chef InSpec tests are used for compliance validation of configurations managed by Ansible.
3. The setup-automate scripts are used for setting up a Chef environment, which may not be needed if fully migrating to Ansible.
4. There are no external dependencies or integrations not visible in the repository.
5. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
6. There is no complex state management or data persistence requirements beyond what's visible in the playbooks.
7. The migration will not require preserving Chef-specific functionality beyond the compliance testing capabilities.