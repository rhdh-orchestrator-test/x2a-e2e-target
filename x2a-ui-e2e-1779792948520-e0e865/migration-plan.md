# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a small set of Chef InSpec tests and Ansible playbooks that demonstrate how Chef InSpec can be used alongside Ansible for compliance automation. The repository also includes shell scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, focusing primarily on converting InSpec tests to equivalent Ansible functionality while maintaining the existing Ansible playbooks. The estimated timeline for this migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-inspec-tests**:
    - Description: Chef InSpec tests for validating HTTPS website configuration and SSH security settings
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: Port listening verification, HTTP response validation, SSL/TLS protocol verification, SSH configuration validation

- **ansible-web-server**:
    - Description: Ansible playbook for deploying an Apache web server with HTTPS support
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration, website deployment

- **ansible-ssl-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL configuration hardening, service restart

- **chef-server-deployment**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used for testing web server deployment. No migration needed as it's a static file.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider migrating to Ansible's built-in test modules or community collections

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook, ensuring TLS 1.2 is enforced and older protocols are disabled.
- **SSH Security**: The SSH root login restrictions tested by the InSpec profile must be preserved in the Ansible implementation.
- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be migrated to Ansible Vault
  - SSL certificate generation should use Ansible's crypto modules with proper secret management

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible assertions or tests may require additional modules or custom scripts. Mitigation: Research Ansible testing frameworks and community modules that provide similar functionality.
- **Chef Automate Deployment**: The Chef Automate deployment scripts need to be replaced with equivalent Ansible roles. Mitigation: Research existing Ansible roles for Chef deployment or create custom roles based on the shell scripts.

### Migration Order

1. Ansible playbooks (website_https.yml, poodle_fix.yml) - Already in Ansible format, just need review and potential refactoring
2. InSpec tests (website_https_verify.rb, ssh_profile.rb) - Convert to Ansible-native testing
3. Chef deployment scripts (deploy-automate.sh, deploy-chef-server.sh) - Convert to Ansible roles

### Assumptions

1. The primary goal is to migrate away from Chef InSpec while maintaining the existing Ansible playbooks
2. The Chef Automate and Chef Infra Server deployment scripts are intended to be replaced with Ansible equivalents
3. The target environment will continue to be Ubuntu 20.04 or compatible systems
4. The security requirements (SSL/TLS configuration, SSH hardening) must be maintained in the migrated solution
5. Test Kitchen will be replaced with an Ansible-native testing framework
6. No external dependencies or modules beyond what's visible in the repository are required
7. The migration does not need to maintain backward compatibility with Chef InSpec
8. The hardcoded credentials in the deployment scripts are for demonstration purposes only and will be properly secured in the migrated solution