# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks designed to demonstrate compliance automation with Ansible. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native solutions while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, including testing and documentation.
**Complexity**: Low to Medium - The repository primarily contains Ansible playbooks already, with Chef InSpec tests and Chef server deployment scripts being the main migration targets.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (STIG)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script with Chef commands
    - Key Features: Chef Automate installation, Chef Infra Server setup, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script with Chef commands
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - will need to be replaced with Ansible-native testing framework like Molecule
- `index.html`: Simple HTML file used as a test page - can be preserved as-is or included as a template in Ansible

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but the setup scripts suggest they could be used in cloud environments

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace InSpec tests with Ansible's built-in `assert` module
  - Consider using Ansible Lint for static analysis
  - Implement Molecule for testing Ansible roles and playbooks

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule supports multiple drivers including Vagrant
  - Provides a complete testing workflow for Ansible roles

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or alternative solutions:
  - Convert deployment scripts to Ansible playbooks
  - Consider using AWX/Ansible Tower as an alternative to Chef Automate
  - Use Ansible Vault for secrets management instead of Chef's encrypted data bags

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache - ensure this is preserved in the migration
  - Current configuration disables vulnerable protocols (SSLv3) and enables TLSv1.2
  - Consider updating to also enable TLSv1.3 for better security

- **SSH Hardening**: The InSpec test verifies SSH root login is disabled
  - Implement equivalent checks using Ansible's assert module
  - Consider expanding SSH hardening with Ansible security roles

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected: 3 (username, password, and email in deployment scripts)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions
  - Challenge: InSpec provides a domain-specific language for compliance testing
  - Mitigation: Use Ansible's assert module combined with command/shell modules to gather system state information

- **Compliance Reporting**: InSpec provides rich compliance reporting
  - Challenge: Replicating compliance reporting capabilities in Ansible
  - Mitigation: Consider integrating with tools like OpenSCAP or using Ansible Tower's reporting features

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk as they're already in Ansible format
   - Review and update as needed for best practices
   - Add documentation and comments

2. **Chef InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Medium complexity
   - Convert to Ansible assertions or Molecule tests
   - Ensure equivalent coverage and reporting

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - Higher complexity
   - Convert to Ansible playbooks
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, as indicated in the README.
2. The existing Ansible playbooks are functioning correctly and don't require significant changes.
3. There are no external dependencies or integrations not visible in the repository.
4. The target environment will continue to be Ubuntu 20.04 or compatible systems.
5. The self-signed certificates are for demonstration purposes and not production use.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure alternatives.
7. There may be additional Chef InSpec profiles or tests referenced but not included in this repository.
8. The migration will maintain the same level of compliance checking and security validation.