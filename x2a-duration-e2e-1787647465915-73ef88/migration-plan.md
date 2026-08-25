# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on:

1. Ansible playbooks that configure web servers with HTTPS
2. Chef InSpec tests used for compliance verification
3. Shell scripts for deploying Chef infrastructure

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The main effort will involve preserving the compliance testing functionality while consolidating all infrastructure management into Ansible.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS configuration and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Simple HTML file for the web server

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing framework:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Keep InSpec as a standalone tool but invoke it from Ansible

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing Ansible roles and playbooks
  - Molecule can use Vagrant as a driver, maintaining compatibility with existing VM setup

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform for enterprise automation
  - Ansible AWX (open source) for smaller deployments
  - GitLab CI/CD or Jenkins for pipeline integration

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains the minimum protocol version
  - Consider updating to include TLSv1.3 support

- **Certificate Management**: 
  - Current implementation uses self-signed certificates
  - Consider integrating with Let's Encrypt for production environments
  - Implement proper certificate rotation and management

- **Vault/secrets management**:
  - Current implementation has hardcoded passwords in the deployment scripts
  - Migrate to Ansible Vault for secure credential storage
  - Consider integration with external secret management systems (HashiCorp Vault, AWS Secrets Manager, etc.)

### Technical Challenges

- **Compliance Testing**: Ensuring that the compliance testing functionality provided by InSpec is maintained
  - Solution: Implement equivalent tests using Ansible's assert module or maintain InSpec as a separate tool

- **Configuration Validation**: Ensuring that the migrated Ansible roles correctly implement all the security configurations
  - Solution: Comprehensive testing with Molecule and validation scripts

- **Deployment Automation**: Replacing the Chef Automate/Infra Server deployment with equivalent Ansible functionality
  - Solution: Create Ansible roles for deploying Ansible Automation Platform or AWX

### Migration Order

1. **website_https playbook** (low risk, already Ansible)
   - Refactor into a proper Ansible role structure
   - Add documentation and improve variable naming

2. **poodle_fix playbook** (low risk, already Ansible)
   - Integrate into the website_https role as a security hardening task
   - Update to include modern TLS best practices

3. **InSpec tests** (moderate complexity)
   - Convert to Ansible assert tests or Molecule tests
   - Ensure all compliance checks are preserved

4. **Chef deployment scripts** (high complexity)
   - Replace with Ansible playbooks for deploying Ansible Automation Platform or AWX
   - Implement secure credential management

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being production infrastructure code
2. The target environment will continue to be Ubuntu 20.04 or newer
3. Vagrant will continue to be used for development/testing environments
4. The security requirements (TLS configuration, etc.) will remain the same or become more stringent
5. The deployment scripts are examples and not used in production (due to hardcoded credentials)
6. The migration will consolidate all automation into Ansible, removing the dependency on Chef products