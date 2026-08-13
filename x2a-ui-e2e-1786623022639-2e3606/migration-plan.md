# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and server configuration. The repository appears to be a demonstration or example repository showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, focusing on:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Ensuring existing Ansible playbooks follow best practices
3. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks

**Estimated Timeline**: 2-3 weeks for a complete migration, with the majority of time spent on converting the Chef InSpec tests to Ansible-native solutions and creating proper Ansible roles for the Chef server deployment scripts.

## Module Migration Plan

This repository contains a mix of Ansible playbooks, Chef InSpec tests, and shell scripts that need individual migration planning:

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
    - Key Features: SSL protocol configuration, service restart

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH configuration for compliance with security standards
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security requirements (STIG)

- **deploy-automate**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization creation

- **deploy-chef-server**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and verifying with InSpec
- `index.html`: Simple HTML file for the website example

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

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
  - AWX/Ansible Tower for enterprise automation platform
  - Ansible Automation Platform for compliance reporting

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should maintain or improve security:
  - Ensure TLS 1.2+ is enforced (already implemented in poodle_fix.yml)
  - Consider using Let's Encrypt instead of self-signed certificates
  - Implement proper certificate management

- **SSH Hardening**: The InSpec profile checks for SSH root login. Migration should:
  - Implement equivalent SSH hardening in Ansible
  - Use ansible.posix.ssh_config module for SSH configuration

- **Credentials Management**: The deployment scripts contain hardcoded credentials:
  - Replace with Ansible Vault for secure credential storage
  - Use variables for all sensitive information
  - Document: 3 credential sets identified (username, password, email)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or Molecule tests will require careful mapping of test logic
  - Mitigation: Create a test mapping document to ensure all compliance checks are preserved

- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible requires understanding of Chef server architecture
  - Mitigation: Create an Ansible role that handles Chef server deployment with idempotent tasks

- **Test Kitchen Integration**: The current setup uses Test Kitchen to orchestrate Ansible and InSpec
  - Mitigation: Replace with Molecule for a more Ansible-native testing approach

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format
   - Review and refactor according to best practices
   - Convert to proper Ansible roles

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity
   - Convert to Ansible assertions or Molecule tests
   - Ensure all compliance checks are preserved

3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity
   - Convert to Ansible roles
   - Implement proper variable management and Ansible Vault for credentials

### Assumptions

1. The repository is primarily for demonstration purposes, showing how Chef InSpec can work alongside Ansible
2. The actual production environment may have more complex configurations not represented in these examples
3. The Test Kitchen setup is for local testing only and may not reflect the production deployment method
4. The deployment scripts are examples and may need customization for actual production use
5. No external dependencies or integrations beyond what's visible in the repository
6. No complex data structures or state management requirements
7. No specific performance requirements for the migrated solution
8. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions