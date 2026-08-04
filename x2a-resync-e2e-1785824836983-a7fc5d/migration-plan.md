# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. The repository also contains scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Migrating Chef Automate/Infra Server deployment scripts to Ansible playbooks
3. Ensuring all compliance requirements are maintained during migration

Estimated timeline: 1-2 weeks for a small team, with low complexity due to the limited scope.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration on the web server
- `tests/ssh_profile.rb`: InSpec test to verify SSH security configuration
- `index.html`: Sample HTML file for the web server

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible's built-in `--check` mode for validation

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - Git repositories for playbook/role storage
  - Ansible Collections for role distribution

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure proper SSL/TLS protocols are maintained in the migrated solution.
  - Migration approach: Maintain the same SSL protocol restrictions (TLSv1.2) and disable vulnerable protocols
  
- **SSH Hardening**: InSpec tests verify SSH root login is disabled.
  - Migration approach: Create equivalent Ansible assertions or use ansible-lint security rules

- **Self-signed Certificates**: The current solution generates self-signed certificates.
  - Migration approach: Maintain the same approach or consider integrating with Let's Encrypt for production environments

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Compliance Testing**: Converting InSpec tests to Ansible-native testing solutions while maintaining the same level of compliance validation.
  - Mitigation: Use a combination of Ansible assertions and custom modules to replicate InSpec functionality

- **Chef Automate Replacement**: Finding equivalent functionality in Ansible ecosystem for Chef Automate features.
  - Mitigation: Evaluate AWX/Tower features against Chef Automate requirements and identify any gaps

- **Test Kitchen Integration**: The current setup uses Test Kitchen to orchestrate testing.
  - Mitigation: Replace with Molecule for Ansible role testing and integrate with CI/CD pipeline

### Migration Order

1. **website_https playbook** (low risk, already Ansible)
   - Review and optimize the existing Ansible playbook
   - Add documentation and ensure idempotence

2. **poodle_fix playbook** (low risk, already Ansible)
   - Review and optimize the existing Ansible playbook
   - Add documentation and ensure idempotence

3. **InSpec Tests** (moderate complexity)
   - Convert website_https_verify.rb to Ansible assertions or Molecule tests
   - Convert ssh_profile.rb to Ansible assertions or Molecule tests

4. **Chef Automate/Infra Server Deployment Scripts** (high complexity)
   - Create Ansible playbooks to replace the bash scripts
   - Implement Ansible Vault for credential storage
   - Test deployment in isolated environment

### Assumptions

1. The primary goal is to move all functionality to pure Ansible without relying on Chef components
2. The InSpec tests are critical for compliance and must be replicated in the Ansible solution
3. The deployment scripts for Chef Automate/Infra Server are needed for the application, not just for Chef itself
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. Vagrant will continue to be used for development/testing environments
6. The security requirements (SSL configuration, SSH hardening) must be maintained in the migrated solution
7. No external dependencies or integrations beyond what's visible in the repository
8. The migration will be done in-place without disrupting existing environments