# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **inspec_tests**:
    - Description: Chef InSpec tests for verifying HTTPS functionality and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol testing, SSH root login security check

- **chef_deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server setup, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework.
- `index.html`: Sample HTML file used for testing the web server setup.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in assert module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Consider maintaining InSpec as a separate testing tool if its capabilities are required

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Consider these alternatives:
  - AWX/Ansible Tower for enterprise automation platform
  - Ansible Semaphore for a lightweight open-source alternative
  - GitLab CI/CD with Ansible for a CI/CD-based approach

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Ensure these security hardening measures are preserved in the migration:
  - Disabling vulnerable SSL protocols (SSLProtocol -all +TLSv1.2)
  - Self-signed certificate generation and configuration

- **SSH Security**: The InSpec tests check for SSH root login being disabled. Ensure this security check is maintained in the Ansible-native testing solution.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates and keys should be managed securely

### Technical Challenges

- **Testing Framework Migration**: Moving from InSpec to Ansible-native testing will require finding equivalent ways to test:
  - Network port listening status
  - HTTP response content and status codes
  - SSL protocol configuration
  - SSH configuration

- **Chef Automate Replacement**: Finding an equivalent Ansible-based solution for the functionality provided by Chef Automate, particularly around compliance reporting.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): These are already in Ansible format and require minimal changes, mainly to align with best practices and integrate with new testing framework.

2. **Testing Framework**: Migrate InSpec tests to Ansible-native testing solutions.

3. **Chef Deployment Scripts**: Replace with Ansible playbooks for deploying alternative solutions (AWX/Tower or other selected alternatives).

### Assumptions

1. The primary goal is to move away from Chef components while maintaining the same functionality.
2. The InSpec tests are essential for compliance verification and equivalent testing capability is required in the Ansible solution.
3. The current setup is used for demonstration/educational purposes rather than production, based on the repository description.
4. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure credential management in production.
5. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
6. The migration will maintain the same level of security hardening present in the original configuration.