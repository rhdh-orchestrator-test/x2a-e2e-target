# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components that need to be migrated to a pure Ansible solution. The repository appears to be primarily focused on examples and demonstrations rather than production infrastructure code. It contains:

1. Chef InSpec test profiles used alongside Ansible playbooks
2. Ansible playbooks for configuring web servers with HTTPS
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration scope is relatively small, with only a few Ansible playbooks and InSpec test profiles to convert. The estimated timeline for migration is 1-2 weeks, with low complexity due to the limited number of components and their straightforward nature.

## Module Migration Plan

This repository contains Chef InSpec profiles and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec profile that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Tests for port 443 listening, HTTPS response, and SSL/TLS protocol security

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: Tests for SSH root login being disabled, compliance with security standards

- **chef-automate-deploy**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Shell script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework.
- `chef-and-ansible/index.html`: Static HTML file, can be directly included in Ansible content.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Convert InSpec profiles to Ansible roles with test tasks

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing Ansible roles and playbooks
  - GitHub Actions or other CI/CD pipeline for automated testing

- **Chef Automate/Infra Server**: Replace deployment scripts with:
  - Ansible roles for configuration management
  - Consider migrating to AWX/Ansible Tower for web UI and control

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security improvements in the poodle_fix.yml playbook:
  - Ensure TLSv1.2 is enabled and older protocols are disabled
  - Maintain proper certificate generation and configuration

- **SSH Security**: The SSH security controls tested by the InSpec profile should be implemented in Ansible:
  - Create an Ansible task to ensure PermitRootLogin is not set to 'yes'
  - Implement the security requirements from the STIG referenced in the InSpec profile

- **Vault/secrets management**:
  - Current repository has hardcoded credentials in the Chef server deployment scripts
  - Migrate to Ansible Vault for secure credential storage
  - Document the count and type of credentials detected per module:
    - chef-automate-deploy: 1 password (userpassword variable)
    - chef-server-deploy: 1 password (userpassword variable)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or Molecule tests will require careful mapping of test functionality:
  - Challenge: InSpec has specific matchers for SSL/TLS testing that may not have direct equivalents in Ansible
  - Mitigation: May need to use Ansible's `command` module with custom commands and assertions to achieve the same level of testing

- **Chef Server Deployment**: The Chef server deployment scripts perform specific Chef-related tasks:
  - Challenge: Creating equivalent Ansible automation for AWX/Tower deployment
  - Mitigation: Research AWX/Tower API and deployment options to create equivalent functionality

### Migration Order

1. **website_https.yml** (low risk, already Ansible): Minimal changes needed, just review and optimize
2. **poodle_fix.yml** (low risk, already Ansible): Minimal changes needed, just review and optimize
3. **InSpec Tests** (moderate complexity): Convert to Ansible assertions or Molecule tests
4. **Chef Deployment Scripts** (high complexity): Replace with Ansible roles for AWX/Tower deployment

### Assumptions

1. The repository is primarily for demonstration purposes and not production infrastructure
2. The InSpec tests are used for validation and compliance checking rather than continuous monitoring
3. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
4. The deployment scripts are examples and not used for actual production Chef server deployments
5. No external dependencies or integrations beyond what's visible in the repository
6. The migration will maintain the same level of security testing and validation
7. The Ansible playbooks are already in a format that requires minimal changes