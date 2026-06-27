# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. The repository also contains shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Migrating Chef Automate deployment scripts to Ansible playbooks
3. Ensuring all compliance checks are preserved in the new implementation

Estimated timeline: 1-2 weeks for a small team (1-2 engineers)

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
    - Description: Chef InSpec control that ensures SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used for testing the web server. Can be directly used in Ansible without changes.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Consider using the community.general.test_module for test-driven infrastructure

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that can:
  - Configure system settings (hostname, sysctl parameters)
  - Install and configure alternative compliance and infrastructure management tools

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in poodle_fix.yml that disables SSLv3 and enables only TLSv1.2
- **SSH Security**: The SSH root login check in ssh_profile.rb must be maintained in the Ansible implementation
- **Certificate Management**: Self-signed certificate generation should be preserved or improved with proper certificate management
- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected in deployment scripts

### Technical Challenges

- **Compliance Testing**: Converting Chef InSpec tests to Ansible-native testing solutions while maintaining the same level of compliance validation
  - Mitigation: Research and implement equivalent testing capabilities using Ansible modules or integrate with tools like Molecule

- **Maintaining Test Coverage**: Ensuring that all compliance checks are preserved during migration
  - Mitigation: Create a comprehensive test matrix mapping InSpec tests to their Ansible equivalents

- **Deployment Script Conversion**: Converting the Chef Automate and Chef Infra Server deployment scripts to Ansible
  - Mitigation: Research Ansible roles for deploying alternative compliance and infrastructure management tools

### Migration Order

1. **website_https playbook** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - No actual migration needed, just potential improvements

2. **poodle_fix playbook** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - No actual migration needed, just potential improvements

3. **InSpec tests** (moderate complexity)
   - Convert website_https_verify.rb to Ansible assertions or Molecule tests
   - Convert ssh_profile.rb to Ansible assertions or Molecule tests

4. **Deployment scripts** (high complexity)
   - Convert deploy-automate.sh and deploy-chef-server.sh to Ansible playbooks
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The primary goal is to move away from Chef InSpec while maintaining the same level of compliance testing
2. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are working correctly and don't need significant changes
3. There's no requirement to maintain backward compatibility with Chef Automate or Chef Infra Server
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
5. The deployment scripts are used for setting up test environments and not production systems
6. The hardcoded credentials in the deployment scripts are not used in production environments
7. The repository is primarily for demonstration purposes as indicated by the README.md
8. The migration will focus on maintaining the same functionality rather than adding new features