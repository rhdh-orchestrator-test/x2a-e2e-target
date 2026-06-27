# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec tests for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is **LOW** with an estimated timeline of **1-2 weeks** to fully migrate all components to pure Ansible. The primary focus will be on replacing Chef InSpec tests with equivalent Ansible-native testing solutions.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Apache web server configuration with SSL/TLS setup, self-signed certificates, and basic website deployment
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **ssl-poodle-remediation**:
    - Description: Security fix for POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **compliance-testing**:
    - Description: Chef InSpec tests for verifying HTTPS website functionality and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol testing, SSH root login security check

- **chef-infrastructure-deployment**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts
    - Key Features: Chef server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - will need to be replaced with Ansible-native testing framework
- `index.html`: Sample HTML file used in the website deployment - can be reused as-is

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible Lint for static analysis
  - Option 3: Use Ansible assert module for runtime verification

- **Test Kitchen**: Replace with Molecule for Ansible role testing, which provides similar functionality but is designed specifically for Ansible

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and enables only TLSv1.2
  - Migration approach: Convert the existing Ansible replace module usage to an equivalent Ansible template or lineinfile task

- **SSH Security Controls**: The SSH root login restriction test must be maintained
  - Migration approach: Convert the InSpec test to an Ansible assert task that verifies the same condition

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible verification tasks
  - Mitigation: Use Ansible's uri module to replace the HTTP tests and command/shell modules with assert for the SSL protocol verification

- **Chef Server Deployment**: The Chef server deployment scripts need to be reimagined as Ansible roles
  - Mitigation: Create an Ansible role that can deploy alternative configuration management or compliance tools if needed

### Migration Order

1. **website-https-configuration** (low risk, already in Ansible)
   - Simply organize into a proper Ansible role structure
   - Add documentation and variables

2. **ssl-poodle-remediation** (low risk, already in Ansible)
   - Integrate with the website-https role as an optional security enhancement
   - Add conditional logic for applying the fix

3. **compliance-testing** (moderate complexity)
   - Convert InSpec tests to Ansible verification tasks
   - Implement Molecule for testing the roles

4. **chef-infrastructure-deployment** (high complexity)
   - Determine if Chef infrastructure is still needed
   - If not, document the decommissioning process
   - If yes, create Ansible roles to deploy Chef infrastructure

### Assumptions

1. The primary purpose of this repository is demonstration/educational rather than production use
2. The Chef InSpec tests are used for compliance verification of Ansible-managed systems
3. The Chef server deployment scripts may not be needed in a pure Ansible environment
4. No external dependencies or integrations beyond what's visible in the repository
5. No complex data handling or state management requirements
6. The target environment is Ubuntu 20.04 running on Vagrant VMs
7. No specific cloud provider requirements or dependencies
8. No custom modules or complex logic that would be difficult to migrate
9. No existing Ansible inventory or group variables to integrate with