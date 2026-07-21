# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. The repository also includes scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration effort will involve converting the Chef InSpec tests to Ansible-native testing solutions and updating the Chef server deployment scripts to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a complete migration, with the majority of time spent on converting InSpec tests to Ansible-native testing frameworks.

## Module Migration Plan

This repository contains a mix of Ansible playbooks, Chef InSpec tests, and bash scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test profile for verifying HTTPS configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Verifies port 443 is listening, HTTPS status is 200, content matches, and SSL protocols are properly configured

- **ssh_profile**:
    - Description: Chef InSpec test profile for SSH security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: Verifies SSH root login is disabled according to security standards

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/index.html`: Sample HTML file for testing web server

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for both on-premises and cloud deployment (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace InSpec tests with Ansible Molecule for infrastructure testing
  - Consider using ansible-lint for static code analysis
  - For compliance testing, evaluate OpenSCAP with Ansible or Ansible's built-in assert module

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure
  - Molecule provides similar functionality for testing Ansible roles and playbooks
  - Supports multiple drivers including Vagrant, Docker, and cloud providers

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks
  - Create Ansible roles for configuration management
  - Consider using AWX/Ansible Tower as a replacement for Chef Automate's dashboard functionality

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure the Ansible migration maintains:
  - Proper SSL protocol configuration (TLSv1.2 enforcement)
  - Self-signed certificate generation
  - Secure virtual host configuration

- **SSH Hardening**: The InSpec tests verify SSH security configurations:
  - Ensure the migration includes Ansible tasks to enforce SSH security settings
  - Implement equivalent checks for SSH root login restrictions

- **Vault/secrets management**:
  - The current implementation has hardcoded credentials in the deployment scripts
  - Migrate to Ansible Vault for secure credential storage
  - Replace hardcoded passwords in deploy-automate.sh and deploy-chef-server.sh
  - Document the count and type of credentials detected: 2 sets of credentials in deployment scripts (username, password)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing solutions:
  - InSpec has specific matchers and resources that may not have direct equivalents in Ansible
  - Develop custom Ansible modules or use assert module for complex compliance checks
  - Consider using Ansible's built-in modules like stat, command, and shell for system verification

- **Maintaining Compliance Reporting**: Chef InSpec provides rich compliance reporting:
  - Evaluate Ansible's compliance capabilities or integrate with third-party tools
  - Consider implementing custom reporting using Ansible's callback plugins

- **Security Standards Compliance**: The InSpec tests include specific security standard references:
  - The SSH profile includes tags for security standards (SRG-OS-000112, V-38607, etc.)
  - Ensure equivalent compliance tracking in the Ansible implementation

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format):
   - website_https.yml and poodle_fix.yml are already in Ansible format
   - Review and update as needed to follow best practices

2. **Test Framework** (Moderate complexity):
   - Convert Test Kitchen configuration to Molecule
   - Develop equivalent tests using Ansible's testing capabilities

3. **InSpec Tests** (Moderate complexity):
   - Convert website_https_verify.rb to Ansible assertions or Molecule verifiers
   - Convert ssh_profile.rb to Ansible assertions or Molecule verifiers

4. **Deployment Scripts** (High complexity):
   - Convert deploy-automate.sh and deploy-chef-server.sh to Ansible playbooks
   - Implement secure credential management using Ansible Vault

### Assumptions

1. The primary goal is to migrate all components to pure Ansible without dependencies on Chef products
2. The current setup uses Chef InSpec primarily for testing, not for configuration management
3. The deployment scripts are used for setting up Chef infrastructure, which will be replaced by Ansible infrastructure
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. Vagrant will continue to be used for development/testing environments
6. The security requirements (SSL configuration, SSH hardening) will remain the same
7. No external data sources or complex data structures are being used that would require special handling
8. The migration will maintain the same level of compliance testing and reporting capabilities
9. The security standard references in the InSpec tests (SRG-OS-000112, V-38607, etc.) need to be preserved in the Ansible implementation