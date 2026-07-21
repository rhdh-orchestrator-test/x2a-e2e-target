# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec test profiles that demonstrate how to use Chef InSpec for compliance testing with Ansible deployments. Additionally, it includes bash scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, focusing on:

1. Preserving the existing Ansible playbooks
2. Converting Chef InSpec tests to Ansible-native testing solutions
3. Replacing Chef Automate/Server deployment scripts with Ansible playbooks

**Estimated Timeline**: 1-2 weeks for a single engineer, with the majority of time spent on converting InSpec tests to Ansible-native testing frameworks.

## Module Migration Plan

This repository contains Ansible playbooks with Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that hardens SSL configuration in Apache to mitigate the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS configuration on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification
- `chef-and-ansible/index.html`: Sample HTML file used in testing
- `chef-and-ansible/README.md`: Documentation explaining the purpose of the Chef InSpec and Ansible integration

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - **Option 1**: Ansible Molecule with Testinfra for infrastructure testing
  - **Option 2**: Ansible Molecule with Goss for infrastructure testing
  - **Option 3**: Maintain InSpec as a standalone testing tool but integrate with Ansible CI/CD

- **Test Kitchen**: Replace with:
  - **Option 1**: Ansible Molecule for testing Ansible roles and playbooks
  - **Option 2**: GitHub Actions or other CI/CD pipeline for automated testing

- **Chef Automate/Server**: Replace deployment scripts with:
  - Ansible playbooks for deploying alternative compliance and infrastructure management tools

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Migration should preserve:
  - Self-signed certificate generation
  - TLS 1.2 protocol enforcement
  - Disabling of vulnerable SSL/TLS protocols

- **SSH Hardening**: The InSpec tests verify SSH security configurations. Migration should:
  - Maintain SSH hardening checks
  - Ensure root login remains disabled
  - Preserve compliance with security standards (SRG-OS-000112, V-38607, etc.)

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be moved to Ansible Vault
  - No encrypted data bags or Chef Vault usage detected
  - Total credentials detected: 2 (username/password in deployment scripts)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing frameworks will require:
  - Mapping InSpec resources to equivalent Testinfra or Goss checks
  - Preserving compliance metadata and documentation
  - Ensuring equivalent test coverage

- **Test Kitchen to Molecule**: Migrating the testing framework will require:
  - Creating equivalent Molecule scenarios
  - Configuring Molecule to use the same Vagrant driver
  - Setting up appropriate verifiers for the tests

- **Chef Automate/Server Deployment**: Replacing the deployment scripts will require:
  - Determining if Chef Automate/Server is still needed or if alternative tools should be used
  - Creating Ansible playbooks that perform equivalent setup steps
  - Handling user and organization creation through Ansible

### Migration Order

1. **Preserve Existing Ansible Playbooks** (Low risk, immediate value)
   - website_https.yml and poodle_fix.yml can be kept as-is
   - Update documentation to reflect the migration

2. **Convert InSpec Tests to Ansible Testing** (Moderate complexity)
   - Create equivalent tests using Molecule with Testinfra or Goss
   - Ensure all compliance checks are preserved

3. **Replace Chef Automate/Server Deployment Scripts** (High complexity)
   - Create Ansible playbooks for deploying alternative compliance tools
   - Or create Ansible playbooks that deploy Chef Automate/Server if still needed

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible integration, not to provide production-ready infrastructure code.
2. The deployment scripts for Chef Automate and Chef Server are examples and not actively used in production.
3. The security compliance requirements (referenced in the InSpec tests) need to be maintained in any migration.
4. The target environment will continue to be Ubuntu 20.04 or a compatible Linux distribution.
5. Vagrant will continue to be used for local development and testing.
6. The migration will focus on maintaining the same functionality while moving to Ansible-native solutions where possible.
7. No actual Chef cookbooks or recipes are present in the repository, so no cookbook migration is needed.