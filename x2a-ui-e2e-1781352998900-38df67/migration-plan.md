# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that demonstrate compliance automation with Ansible. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, considering the limited scope and complexity.

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
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Simple HTML file used for testing the web server. Can be preserved as-is or incorporated into Ansible templates.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis and best practices enforcement

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality to Test Kitchen but is designed specifically for Ansible

- **Chef Automate/Infra Server**: Replace with Ansible automation platform
  - Consider AWX/Ansible Tower for web UI and REST API
  - Use Ansible collections for configuration management

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains enabled and older protocols remain disabled
  - Consider updating to also include TLSv1.3 support

- **SSH Security**: The SSH root login check must be preserved in the Ansible testing framework
  - Convert the InSpec control to an equivalent Ansible assert or Molecule verification

- **Credentials Management**: 
  - The Chef deployment scripts contain hardcoded credentials that should be moved to Ansible Vault
  - Identified credentials:
    - User password in deploy-automate.sh and deploy-chef-server.sh
    - Consider using lookup plugins or external secret management

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's domain-specific language to Ansible's testing capabilities
  - InSpec provides rich, declarative testing syntax that may require multiple Ansible assertions to replicate
  - Solution: Use Ansible's assert module with carefully crafted conditions or consider community modules that extend testing capabilities

- **Test Kitchen to Molecule**: Ensuring test environments remain consistent
  - Test Kitchen and Molecule have different configuration formats and capabilities
  - Solution: Create equivalent Molecule scenarios that match the current Test Kitchen configuration

- **Chef Server Deployment**: Converting Chef server deployment scripts to idempotent Ansible playbooks
  - The current scripts are linear and not idempotent
  - Solution: Create proper Ansible roles with appropriate conditionals to ensure idempotence

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format
   - Review and update to current Ansible best practices
   - Ensure idempotence and add proper documentation

2. **Testing Framework**: Moderate complexity
   - Set up Molecule testing infrastructure
   - Convert InSpec tests to Ansible assertions or Molecule verifiers

3. **Chef Deployment Scripts**: High complexity
   - Create Ansible roles for Chef Automate and Chef Infra Server deployment
   - Implement proper secret management with Ansible Vault
   - Ensure idempotence and proper error handling

### Assumptions

1. The current Ansible playbooks are compatible with Ansible 2.9+ and don't require significant updates
2. The InSpec tests are primarily used for validation and not for continuous compliance monitoring
3. There are no external dependencies or integrations not visible in the repository
4. The deployment scripts are used for initial setup only and not for ongoing management
5. No custom Chef resources or complex Ruby code exists that would require special handling
6. The target environment will continue to be Ubuntu 20.04 or compatible systems
7. The migration doesn't need to preserve Test Kitchen functionality if replaced with equivalent Molecule testing
8. No external data sources or dynamic inventory is being used
9. The Apache configuration doesn't have environment-specific settings that would need parameterization