# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, including testing and documentation.
**Complexity**: Low to Medium - The repository contains a limited number of files with straightforward functionality.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website-https-verification**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh-security-profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled according to security standards
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checking with STIG references

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file used for testing web server deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible's `assert` module for basic validation
  - Option 2: Molecule for more comprehensive testing
  - Option 3: Integration with other testing frameworks like Serverspec or Testinfra

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing Ansible roles and playbooks
  - Or continue using Test Kitchen with Ansible provisioner if preferred

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for enterprise automation platform
  - GitLab CI/CD or Jenkins for pipeline automation
  - Compliance automation can be handled by OpenSCAP integration with Ansible

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the POODLE fix playbook
  - Maintain the restriction to TLSv1.2 protocol
  - Ensure proper restart of services after configuration changes

- **SSH Security Controls**: The SSH security profile must be converted to equivalent Ansible checks
  - Consider using Ansible's `assert` module to validate SSH configuration
  - Maintain compliance with security standards (STIG references)

- **Vault/secrets management**:
  - Hardcoded credentials in the Chef deployment scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Use Ansible's `assert` module with appropriate conditionals or adopt Molecule with Testinfra

- **Compliance Validation**: Maintaining the compliance validation capabilities currently provided by InSpec
  - Mitigation: Integrate with OpenSCAP or use Ansible's built-in security modules

- **Chef Server Functionality**: Replacing Chef Server's organization and user management
  - Mitigation: Use Ansible AWX/Tower for team-based access control and inventory management

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they can remain largely unchanged
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible-native testing
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible roles/playbooks
4. **Test Kitchen Configuration** (kitchen.yml): Replace with Molecule or update for Ansible-only testing

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependency while maintaining the same level of compliance validation
2. The existing Ansible playbooks are functioning correctly and don't require significant changes
3. The deployment environment will continue to be Ubuntu 20.04 or compatible Linux distributions
4. The team has or will develop expertise in Ansible testing methodologies
5. There are no additional Chef cookbooks or resources not visible in the provided repository structure
6. The hardcoded credentials in deployment scripts are for demonstration purposes only and will be properly secured in the migrated solution
7. The migration will maintain the same level of security compliance validation currently provided by InSpec
8. The Chef Automate and Chef Server deployment scripts are used for setting up test environments and not production systems