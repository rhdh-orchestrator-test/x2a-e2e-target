# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks designed to demonstrate compliance automation with Ansible. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that need to be migrated to Ansible.

Estimated timeline: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server setup, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Simple HTML file used as a template for the website

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, but the deployment scripts suggest they could be used in cloud environments

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - For website_https_verify.rb: Use Ansible's uri module and assert module to verify HTTPS functionality
  - For ssh_profile.rb: Use Ansible's assert module with lineinfile or template module to verify SSH configuration

- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks

- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower or other Ansible-native management solutions

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Migration approach: Preserve the existing Ansible task that disables SSLv3 and enables TLSv1.2

- **SSH Security**: The SSH root login check must be maintained
  - Migration approach: Convert the InSpec control to an Ansible task that verifies the SSH configuration

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password)
  - Migration approach: Use Ansible Vault to securely store credentials

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing
  - Mitigation: Use Ansible's assert module combined with command/shell modules to perform similar checks
  - Consider using Ansible's built-in testing capabilities or integrating with a CI/CD pipeline

- **Compliance Reporting**: InSpec provides structured compliance reporting
  - Mitigation: Consider integrating with tools like Ansible AWX/Tower for compliance reporting or use community modules for generating compliance reports

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format
   - Review and update as needed for best practices
   - Ensure idempotency and proper error handling

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity
   - Convert to Ansible-native testing using assert module
   - Ensure all compliance checks are maintained

3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity
   - Convert to Ansible roles for deploying alternative infrastructure management solutions
   - Ensure secure credential management

### Assumptions

1. The existing Ansible playbooks are functioning correctly and follow best practices
2. The InSpec tests are currently used for compliance validation only and not for active remediation
3. The deployment scripts are used for setting up Chef infrastructure that will be replaced with Ansible-native solutions
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. There are no additional dependencies or integrations not visible in the provided files
6. The migration will maintain the same level of security and compliance checking
7. The HTML content and Apache configurations will remain unchanged in the migration