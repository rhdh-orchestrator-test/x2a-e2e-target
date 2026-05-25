# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that will need to be replaced with Ansible equivalents.

Estimated timeline: 1-2 weeks for a single developer, with minimal complexity due to the limited scope of Chef components that need migration.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-deployment**:
    - Description: Ansible playbook for deploying a secure Apache web server with HTTPS configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-vulnerability-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **https-compliance-tests**:
    - Description: Chef InSpec tests for validating HTTPS configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh-security-profile**:
    - Description: Chef InSpec profile for SSH security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check with STIG compliance metadata

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Sample HTML content for the web server. Can be preserved as-is.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic validation
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Consider integrating with DISA STIG Ansible content for compliance checks

- **Test Kitchen**: Replace with Ansible-native testing frameworks:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Simple Vagrant or Docker-based testing scripts

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks:
  - For compliance scanning functionality in Chef Automate, consider:
    - OpenSCAP with Ansible integration
    - Ansible Automation Platform with built-in compliance capabilities

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Approach: Maintain the same configuration parameters in the Ansible playbooks
  
- **SSH Security Controls**: The SSH security profile needs to be converted to Ansible checks
  - Approach: Convert InSpec controls to Ansible assert tasks or use ansible-lint rules

- **Vault/secrets management**:
  - Hardcoded credentials detected in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Use Ansible's assert module with careful conditional logic to match InSpec's behavior
  
- **Compliance Metadata**: Preserving STIG compliance metadata from InSpec tests
  - Mitigation: Document compliance requirements separately or use Ansible tags and variables to store metadata

- **Test Kitchen Integration**: Replacing the Test Kitchen workflow
  - Mitigation: Implement Molecule testing framework with similar workflow patterns

### Migration Order

1. Convert Chef InSpec tests to Ansible tests (low risk, preserves functionality)
2. Replace Test Kitchen configuration with Ansible-native testing framework (moderate complexity)
3. Create Ansible playbooks to replace Chef Automate/Infra Server deployment scripts (higher complexity)

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) will be preserved as-is
2. The primary goal is to eliminate Chef dependencies while maintaining the same functionality
3. The deployment scripts for Chef Automate and Chef Infra Server need to be replaced with equivalent Ansible functionality
4. The repository is primarily used for demonstration/example purposes rather than production deployment
5. No external Chef cookbooks or complex Chef-specific features are in use
6. The InSpec tests are relatively simple and can be converted to Ansible assertions
7. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs