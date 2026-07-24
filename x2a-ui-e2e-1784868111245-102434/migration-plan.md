# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with shell scripts for Chef Automate and Chef Infra Server deployment. The migration scope is relatively small, focusing on converting the existing Ansible playbooks to a more standardized Ansible structure and integrating the Chef InSpec tests into an Ansible-native testing framework. The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of playbooks and tests.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2 in Apache configuration

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Tests for port 443 listening, HTTPS response, SSL protocol security

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: Tests for SSH root login being disabled, compliance with security standards

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

- `kitchen.yml`: Test Kitchen configuration file that uses Ansible provisioner and InSpec verifier to test the website_https playbook
- `index.html`: Static HTML file for the website

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use ansible-test for integration testing
  - Option 2: Integrate with Molecule for testing
  - Option 3: Convert InSpec tests to equivalent Ansible assert tasks

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality but is more Ansible-native
  - Will require creating a molecule.yml configuration to replace kitchen.yml

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks
  - Create roles for Chef server deployment
  - Use Ansible variables instead of shell script variables
  - Implement idempotent deployment process

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL security configuration that must be preserved
  - Ensure the TLS protocol restrictions are maintained (disabling SSLv3, enabling TLSv1.2)
  - Consider updating to also enable TLSv1.3 for better security

- **SSH Security**: The InSpec tests verify SSH security configurations
  - Create equivalent Ansible tasks to enforce and verify SSH security settings
  - Implement as pre-tasks or separate security role

- **Credentials Management**: The deployment scripts contain hardcoded credentials
  - Replace with Ansible Vault for secure credential storage
  - Identified credentials:
    - User password in deploy-automate.sh and deploy-chef-server.sh
    - Consider using lookup plugins for dynamic credential generation

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing
  - Challenge: InSpec has specific testing syntax that doesn't directly map to Ansible
  - Mitigation: Use Ansible assert modules with appropriate conditionals, or maintain InSpec tests but call them from Ansible

- **Self-signed Certificate Generation**: The playbook uses Ansible's openssl modules
  - Challenge: Ensuring idempotent certificate generation
  - Mitigation: Add proper checks to prevent unnecessary certificate regeneration

- **Apache Configuration**: The playbook uses templates for Apache configuration
  - Challenge: Ensuring proper Apache configuration across different distributions
  - Mitigation: Use Ansible's template module with distribution-specific templates

### Migration Order

1. **website_https.yml** (Priority 1 - low risk, high value)
   - Convert to Ansible role structure with proper variables
   - Implement idempotent certificate management

2. **poodle_fix.yml** (Priority 1 - low risk, high value)
   - Integrate into a security hardening role
   - Ensure idempotent execution

3. **InSpec Tests** (Priority 2 - moderate complexity)
   - Convert to Ansible-native testing or integrate with Molecule
   - Ensure test coverage is maintained

4. **Chef Deployment Scripts** (Priority 3 - high complexity)
   - Create Ansible roles for Chef server deployment
   - Implement secure credential management

### Assumptions

1. The target environment will continue to be Ubuntu 20.04 or compatible systems
2. The migration will maintain the same functionality but improve structure and maintainability
3. The InSpec tests are critical for compliance and their functionality must be preserved
4. The Chef deployment scripts are used for setting up test environments and not production systems
5. No external dependencies or integrations beyond what's visible in the repository
6. The Apache configuration is standard and doesn't have custom modules or configurations
7. The self-signed certificates are for testing only and not production use