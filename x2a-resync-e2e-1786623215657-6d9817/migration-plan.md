# MIGRATION FROM ANSIBLE WITH CHEF INSPEC TO ANSIBLE

## Executive Summary

This repository contains a small set of Ansible playbooks with Chef InSpec tests that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting the existing Ansible playbooks to a more structured Ansible format while preserving the compliance testing capabilities provided by Chef InSpec.

**Estimated Timeline**: 1-2 weeks for a single developer to complete the migration, including testing and documentation.

**Complexity**: Low to Medium - The existing Ansible playbooks are straightforward, but proper integration of compliance testing in the new Ansible structure requires careful planning.

## Module Migration Plan

This repository contains Ansible playbooks with Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration should preserve test capabilities.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS website functionality and security. Should be converted to Ansible-compatible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test to verify SSH security configuration. Should be converted to Ansible-compatible testing framework.
- `chef-and-ansible/index.html`: Sample HTML file used in the website deployment. Can be migrated as-is.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or any cloud environment

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen (kitchen.yml)**: Replace with Ansible Molecule for testing Ansible roles
- **Chef InSpec**: Options include:
  1. Continue using InSpec as a standalone tool integrated with Ansible
  2. Replace with Ansible-native testing using ansible-lint and testinfra
  3. Use Ansible's assert module for basic compliance checks

- **Apache2 (2.4.41-4ubuntu3.10)**: Maintain version-specific installation in Ansible roles

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Approach: Create a dedicated Ansible role for Apache security with appropriate TLS configuration
  
- **SSH Hardening**: The SSH security profile tests must be maintained
  - Approach: Create an Ansible role for SSH hardening that implements the same controls tested by the InSpec profile

- **Self-signed Certificates**: The migration should maintain the same approach for certificate generation
  - Approach: Use Ansible's openssl_* modules as already implemented in the current playbooks

- **Vault/secrets management**:
  - Hardcoded credentials found in setup-automate scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Compliance Testing Integration**: Maintaining the compliance testing capabilities currently provided by InSpec
  - Mitigation: Either keep InSpec as a standalone tool or implement equivalent tests using Ansible-compatible testing frameworks

- **Test Kitchen to Molecule Migration**: Converting the existing test infrastructure
  - Mitigation: Create equivalent Molecule scenarios that replicate the current Test Kitchen setup

- **Chef Automate/Server Deployment**: Converting bash scripts to Ansible roles
  - Mitigation: Create dedicated Ansible roles for Chef server deployment, potentially using the chef_automate Ansible collection if available

### Migration Order

1. **website_https playbook** (low risk, high value) - Convert to Ansible role with proper structure
2. **poodle_fix playbook** (low risk, security-focused) - Convert to Ansible role or integrate into the website role
3. **InSpec tests** (moderate complexity) - Convert to Ansible-compatible testing framework
4. **Chef deployment scripts** (high complexity) - Convert bash scripts to Ansible roles

### Assumptions

1. The current Ansible playbooks are already functional and tested in the target environment
2. The InSpec tests are correctly validating the desired state of the systems
3. The repository is primarily for demonstration purposes rather than production use
4. The Chef Automate and Chef Server deployment scripts are intended to be run on separate systems from the web server
5. No external dependencies or inventory files exist beyond what's visible in the repository
6. The migration will maintain the same target OS (Ubuntu 20.04) and deployment method (Vagrant)
7. No CI/CD pipeline integration is currently in place
8. No specific Ansible version requirements exist