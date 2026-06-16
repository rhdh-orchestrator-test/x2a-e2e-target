# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks demonstrating how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting the Chef InSpec tests to Ansible-native testing solutions while maintaining the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server setup scripts that will need to be replaced with Ansible-based deployment solutions.

**Estimated Timeline**: 1-2 weeks for a single engineer to complete the migration, including testing and documentation.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables TLSv1.2 only

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (STIG)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Sample HTML file used in the website deployment. Can be reused as-is in the Ansible content.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace with Ansible Molecule for infrastructure testing
  - Use ansible-lint for static code analysis
  - Consider pytest-ansible for Python-based testing
  - Alternatively, use Ansible assert modules for inline testing

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/Jenkins for CI/CD pipeline integration
  - Ansible Vault for secrets management

### Security Considerations

- **SSL Configuration**: The migration must maintain the security improvements in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced in the Apache configuration
  - Maintain proper certificate generation and management

- **SSH Hardening**: The SSH security checks in ssh_profile.rb must be preserved
  - Convert the InSpec controls to Ansible assert tasks or Molecule tests
  - Maintain compliance with security standards (STIG)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates should be managed securely
  - Count of credentials detected: 3 (username, password, organization name in setup scripts)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Solution: Use Ansible's assert module with appropriate conditionals to replicate InSpec tests
  - Consider using Molecule's verifier plugins for more advanced testing

- **Chef Automate Functionality**: Replacing Chef Automate's compliance reporting
  - Solution: Implement compliance reporting using AWX/Tower with custom reporting dashboards
  - Consider integration with security tools like OpenSCAP

- **User and Organization Management**: Replacing Chef's user and organization structure
  - Solution: Implement RBAC in AWX/Tower
  - Create Ansible playbooks to manage users and access controls

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they can remain largely unchanged
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible Molecule tests
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Replace with Ansible playbooks for AWX/Tower deployment
4. **Test Kitchen Configuration** (kitchen.yml): Replace with Molecule configuration

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependency while maintaining the same level of compliance testing
2. The existing Ansible playbooks are working correctly and don't require significant changes
3. The target environment will continue to be Ubuntu 20.04 or compatible systems
4. The deployment will continue to use self-signed certificates for HTTPS
5. The organization doesn't require all features of Chef Automate and can transition to AWX/Tower
6. The current setup is for demonstration/learning purposes rather than production use
7. No external data sources or integrations are present that would complicate the migration
8. The SSH hardening profile is applicable to the target environment
9. No custom Chef resources or complex Ruby code exists that would require special handling