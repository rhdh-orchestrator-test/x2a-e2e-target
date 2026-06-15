# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mixed environment of Chef InSpec tests and Ansible playbooks that are used together for compliance automation. The primary focus is on migrating the Chef InSpec tests to Ansible while maintaining the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server setup scripts that will need to be replaced with Ansible equivalents.

The migration complexity is relatively low as most of the repository already consists of Ansible playbooks. The main effort will be converting the Chef InSpec tests to Ansible-compatible testing frameworks like Ansible Molecule or integrating with other testing tools that can work with Ansible.

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (SRG-OS-000112)

- **chef-automate-setup**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-setup**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - will need to be replaced with Ansible Molecule or similar testing framework
- `index.html`: Sample HTML file used for testing the web server - can be reused as-is or incorporated into Ansible templates

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule for testing Ansible roles and playbooks
  - Option 2: Integrate with pytest-ansible for Python-based testing
  - Option 3: Use ansible-test for Ansible Collections testing

- **Test Kitchen**: Replace with Ansible Molecule which provides similar functionality for Ansible

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or Jenkins for pipeline integration
  - Ansible Automation Platform for enterprise features

### Security Considerations

- **SSL Configuration**: The poodle_fix.yml playbook addresses SSL vulnerabilities by enforcing TLSv1.2. This security hardening should be maintained in the migrated solution.
  - Migration approach: Incorporate these security settings into the main Apache role or create a dedicated security role

- **SSH Hardening**: The ssh_profile.rb InSpec test verifies SSH security configurations.
  - Migration approach: Create Ansible tasks to enforce the same SSH security settings and use Ansible Molecule to verify compliance

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated in the playbook - consider using Ansible Vault for storing production certificates
  - Document the count and type of credentials detected per module:
    - chef-automate-setup: 1 password (userpassword variable)
    - chef-server-setup: 1 password (userpassword variable)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks will require understanding the equivalent assertions and test structures.
  - Mitigation: Use Ansible's assert module for basic tests and consider integrating with specialized testing tools for more complex validations

- **Chef Automate Replacement**: Finding equivalent functionality in Ansible ecosystem for Chef Automate features.
  - Mitigation: Map Chef Automate features to Ansible AWX/Tower and supplement with additional tools as needed

- **Compliance Reporting**: Chef InSpec provides compliance reporting that needs to be replicated in the Ansible environment.
  - Mitigation: Integrate with compliance tools like OpenSCAP or use Ansible AWX/Tower's reporting capabilities

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format and only need minor adjustments to follow best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity to convert to Ansible testing framework
3. **Chef Setup Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity as they involve replacing Chef infrastructure with Ansible equivalents

### Assumptions

1. The primary goal is to maintain the same functionality while moving completely to Ansible ecosystem
2. The existing Ansible playbooks are working correctly and don't need functional changes
3. The target environment will continue to be Ubuntu 20.04 or compatible systems
4. The security compliance requirements (like those referenced in ssh_profile.rb) will remain the same
5. The team has access to Ansible AWX/Tower or is willing to set it up as a replacement for Chef Automate
6. The hardcoded credentials in the setup scripts are for demonstration purposes only and will be properly secured in the migrated solution
7. The self-signed certificates in the playbooks are for testing only and would be replaced with proper certificates in production