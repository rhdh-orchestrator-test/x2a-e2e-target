# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef server deployment scripts that need to be migrated to a unified Ansible approach. The repository appears to be a collection of examples demonstrating Chef InSpec with Ansible for compliance automation, along with Chef Automate and Chef Infra Server deployment scripts.

The migration scope is relatively small, with only a few Ansible playbooks and bash scripts to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity for the Ansible playbooks (which can be directly reused) and medium complexity for the Chef server deployment scripts (which need to be converted to Ansible roles).

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec
- `tests/website_https_verify.rb`: InSpec tests for verifying HTTPS website functionality
- `tests/ssh_profile.rb`: InSpec profile for SSH security compliance checks

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Keep InSpec as a testing tool but invoke it from Ansible

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides native testing for Ansible roles and collections
  - Supports multiple drivers including Vagrant, Docker, and cloud providers

- **Chef Automate/Infra Server**: Replace with Ansible automation platform
  - Ansible AWX/Tower for web UI, job scheduling, and inventory management
  - Ansible Galaxy for role and collection management

### Security Considerations

- **SSL Configuration**: The playbooks include SSL hardening (disabling SSLv3, enabling TLSv1.2)
  - Migration approach: Preserve these security configurations in the Ansible roles
  - Consider updating to also disable TLSv1.0 and TLSv1.1 for modern security standards

- **SSH Hardening**: InSpec tests verify SSH root login is disabled
  - Migration approach: Create an Ansible role for SSH hardening that implements the same controls
  - Include tasks to disable root login and implement other SSH best practices

- **Self-signed Certificates**: The playbook generates self-signed certificates
  - Migration approach: Consider using Ansible's `community.crypto` collection for certificate management
  - Provide option to use Let's Encrypt for production environments

- **Vault/secrets management**: 
  - Hardcoded credentials in the Chef deployment scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible
  - Challenge: Ensuring idempotent installation and configuration of Chef components
  - Mitigation: Create dedicated Ansible roles for Chef server deployment with proper state checking

- **InSpec Integration**: Maintaining compliance testing capabilities
  - Challenge: Preserving the compliance testing functionality currently provided by InSpec
  - Mitigation: Either integrate InSpec with Ansible or migrate tests to Ansible-native solutions

- **Testing Framework**: Replacing Test Kitchen with Molecule
  - Challenge: Ensuring test coverage and functionality is maintained
  - Mitigation: Create equivalent Molecule scenarios for each Test Kitchen suite

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml)
   - Low risk, can be directly reused with minimal changes
   - Convert to Ansible roles for better organization and reusability

2. **Testing Framework**
   - Moderate complexity
   - Set up Molecule for testing
   - Either integrate InSpec or convert tests to Ansible assertions

3. **Chef Server Deployment Scripts**
   - Higher complexity
   - Create Ansible roles to replace the bash scripts for Chef server deployment
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The primary goal is to migrate all components to Ansible, including the Chef server deployment scripts
2. InSpec testing can either be integrated with Ansible or replaced with Ansible-native testing
3. The current Ansible playbooks are functional and follow best practices
4. No external dependencies or integrations beyond what's visible in the repository
5. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
6. The deployment scripts are intended for on-premises or cloud VMs, not containers
7. No specific performance requirements are defined for the applications
8. The security requirements from the InSpec tests should be maintained in the migrated solution