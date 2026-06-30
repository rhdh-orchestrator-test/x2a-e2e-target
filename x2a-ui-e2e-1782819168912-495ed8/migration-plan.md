# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Ansible playbooks and Chef InSpec tests that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on two main components:

1. Ansible playbooks for configuring a secure web server
2. Chef InSpec tests for verifying compliance and security

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on replacing Chef InSpec tests with equivalent Ansible testing solutions while maintaining the existing Ansible playbooks.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook for configuring Apache web server with HTTPS support
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook for remediating SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website-https-verify**:
    - Description: Chef InSpec test for verifying HTTPS website functionality
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh-profile**:
    - Description: Chef InSpec control for verifying SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for the web server

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for testing
  - Option 2: Use ansible-test framework
  - Option 3: Implement custom test scripts using Python and Ansible modules

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks for setting up alternative compliance and configuration management solutions:
  - Option 1: Ansible AWX/Tower for centralized management
  - Option 2: Ansible with GitLab CI/CD for pipeline-based deployment

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced
  - Disable vulnerable SSL protocols

- **SSH Security**: Maintain the SSH root login restrictions verified by the InSpec test
  - Create equivalent Ansible assertion or verification

- **Certificate Management**: The self-signed certificate generation should be maintained or improved
  - Consider integrating with Let's Encrypt for production environments

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be migrated to Ansible Vault
  - No encrypted data bags or Chef Vault usage detected
  - Count of credentials detected: 2 (username/password in deployment scripts)

### Technical Challenges

- **Compliance Testing**: Chef InSpec provides rich compliance testing capabilities
  - Challenge: Finding equivalent functionality in Ansible
  - Mitigation: Evaluate Ansible Molecule, ansible-test, or custom Python scripts with pytest

- **Test Reporting**: InSpec provides structured compliance reporting
  - Challenge: Replicating compliance reporting in Ansible
  - Mitigation: Implement custom reporting using Ansible callbacks or integrate with tools like Prometheus/Grafana

- **Deployment Scripts**: The Chef Automate and Chef Server deployment scripts need replacement
  - Challenge: Determining the appropriate replacement for compliance management
  - Mitigation: Evaluate AWX/Tower, GitLab CI/CD, or other compliance management tools

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk, already in Ansible format
   - Review and optimize existing playbooks
   - Update any deprecated syntax or modules

2. **Test Infrastructure** (kitchen.yml) - Moderate complexity
   - Replace Test Kitchen with Ansible Molecule
   - Set up equivalent test environments

3. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - High complexity
   - Convert InSpec tests to Ansible-native testing solutions
   - Ensure equivalent coverage and reporting

4. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - High complexity
   - Replace with Ansible playbooks for deploying alternative solutions
   - Implement secure credential management

### Assumptions

1. The primary goal is to eliminate Chef dependencies while maintaining the same functionality
2. The existing Ansible playbooks are working correctly and don't require functional changes
3. The target environment will continue to be Ubuntu 20.04 or compatible
4. Vagrant will continue to be used for development/testing environments
5. The security compliance requirements (STIG references) in the InSpec tests must be maintained
6. The repository is primarily for demonstration/educational purposes rather than production use
7. No external Chef cookbooks or dependencies are being used beyond what's in the repository
8. The Chef Automate and Chef Server deployment is not the primary focus of the migration