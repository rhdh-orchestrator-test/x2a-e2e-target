# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec testing profiles and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. The repository also contains Chef Automate and Chef Infra Server deployment scripts.

The migration scope is relatively small, focusing on:
1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Ensuring existing Ansible playbooks follow best practices
3. Replacing Chef Automate/Infra Server deployment scripts with Ansible equivalents

**Estimated Timeline**: 1-2 weeks for a complete migration, with minimal complexity due to the limited scope of the repository.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, STIG compliance check

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Simple HTML file used for testing web server deployment. Can be reused as-is.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing
  - Option 4: Keep InSpec but manage it via Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible-specific CI/CD pipelines

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for web UI and API
  - GitLab/GitHub for source control
  - Ansible Collections for role management

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains the minimum protocol version
  - Consider updating to also allow TLSv1.3 for improved security

- **SSH Hardening**: Maintain the SSH security controls verified by the InSpec profile
  - Ensure root login remains disabled
  - Consider adding additional SSH hardening parameters

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected: 3 (username, password, and SSL certificates)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of test assertions
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules
  - Consider using Ansible's assert module with appropriate conditionals

- **Maintaining Compliance Validation**: Ensuring the same level of compliance checking with Ansible-native tools
  - Mitigation: Evaluate Ansible Lint rules and custom modules to achieve similar compliance validation

- **Chef Server Functionality**: Replacing Chef Server management functionality
  - Mitigation: Document AWX/Tower setup procedures to replace Chef Server organization and user management

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format, just need review and potential refactoring to follow best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity to convert to Ansible-native testing
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Higher complexity to replace with Ansible equivalents

### Assumptions

1. The primary goal is to move completely away from Chef technologies (InSpec, Automate, Infra Server) to Ansible-only solutions
2. The existing Ansible playbooks are functional and don't require significant rework beyond best practices
3. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
4. The security compliance requirements will remain the same
5. No external dependencies or integrations exist beyond what's visible in the repository
6. The migration will include setting up equivalent functionality for compliance reporting that Chef Automate provides
7. The hardcoded credentials in the deployment scripts are for demonstration purposes only and will be properly secured in the migrated solution