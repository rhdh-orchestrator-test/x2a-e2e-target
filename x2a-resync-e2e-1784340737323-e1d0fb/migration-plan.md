# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

Estimated timeline: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Demo environment showing Chef InSpec with Ansible for compliance automation
    - Path: chef-and-ansible
    - Technology: Ansible + Chef InSpec
    - Key Features: HTTPS configuration, SSL hardening, compliance testing

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Chef infrastructure deployment, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - will need to be replaced with Ansible-native testing framework
- `chef-and-ansible/website_https.yml`: Ansible playbook that configures Apache with HTTPS, creates self-signed certificates, and deploys a simple website
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that fixes SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec test that verifies HTTPS configuration, port availability, and content delivery
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec test that verifies SSH root login is disabled according to security standards
- `chef-and-ansible/index.html`: Simple HTML file used as a template
- `setup-automate/deploy-automate.sh`: Bash script to deploy Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script to deploy Chef Infra Server without Automate

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule with Testinfra for testing
  - Option 2: Use the ansible-test framework
  - Option 3: Convert InSpec tests to equivalent Ansible assert tasks

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration

- **Chef Automate/Server**: Replace deployment scripts with Ansible roles that:
  - Configure system requirements (hostname, sysctl parameters)
  - Install alternative compliance and automation tools (options include AWX/Tower)

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in poodle_fix.yml
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain proper certificate generation and management

- **SSH Hardening**: Preserve the SSH security controls verified by ssh_profile.rb
  - Ensure root login remains disabled
  - Maintain compliance with referenced security standards (STIG, CCI)

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected:
    - setup-automate/deploy-automate.sh: 1 username/password pair
    - setup-automate/deploy-chef-server.sh: 1 username/password pair

### Technical Challenges

- **Compliance Testing Framework**: Finding an equivalent to InSpec in the Ansible ecosystem
  - InSpec provides rich compliance-as-code capabilities with security standard mappings
  - Ansible's built-in testing capabilities are more limited for compliance verification
  - Solution: Consider using Ansible Molecule with Testinfra or integrating with OpenSCAP

- **Test Kitchen to Molecule Migration**: 
  - Test Kitchen has specific workflow patterns that need to be mapped to Molecule
  - Solution: Create equivalent Molecule scenarios that match the current Test Kitchen setup

- **Chef Automate Replacement**:
  - Determining appropriate Ansible-based alternatives for Chef Automate functionality
  - Solution: Consider AWX/Tower for orchestration and compliance reporting

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/website_https.yml, chef-and-ansible/poodle_fix.yml) - Low risk as they're already in Ansible format
   - Review and optimize according to current Ansible best practices
   - Update any deprecated modules or syntax

2. **InSpec Tests** (chef-and-ansible/tests/website_https_verify.rb, chef-and-ansible/tests/ssh_profile.rb) - Medium complexity
   - Convert to equivalent Ansible testing framework
   - Ensure all compliance checks are preserved

3. **Test Kitchen Configuration** (chef-and-ansible/kitchen.yml) - Medium complexity
   - Replace with Ansible Molecule configuration
   - Set up equivalent test scenarios

4. **Chef Deployment Scripts** (setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh) - High complexity
   - Convert to Ansible roles for infrastructure deployment
   - Replace Chef-specific components with Ansible alternatives

### Assumptions

1. The primary goal is to consolidate on Ansible as the single automation tool, eliminating Chef dependencies
2. Compliance testing is a critical requirement that must be preserved in the migration
3. The current setup is used for demonstration/educational purposes rather than production
4. No external Chef cookbooks or complex Chef-specific features are in use
5. The target environment will continue to be Ubuntu 20.04 or compatible systems
6. Vagrant will continue to be used for development/testing environments
7. No specific performance requirements are documented that would affect the migration approach
8. The security standards referenced (SRG, STIG, CCI) must continue to be supported in the migrated solution