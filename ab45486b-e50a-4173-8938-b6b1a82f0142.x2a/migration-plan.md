# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on:

1. Ansible playbooks that configure a web server with HTTPS
2. Chef InSpec tests for validating compliance requirements
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while standardizing on Ansible for all configuration management.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Directory containing Ansible playbooks and InSpec tests for configuring and validating HTTPS websites
    - Path: chef-and-ansible
    - Technology: Ansible/Chef InSpec
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration, compliance testing

- **chef-and-ansible/tests**:
    - Description: Directory containing Chef InSpec tests for validating HTTPS website functionality and SSH security
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: Port listening tests, HTTPS content verification, SSL protocol security checks, SSH security checks

- **setup-automate**:
    - Description: Directory containing shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Shell script
    - Key Features: Chef Automate installation, Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `chef-and-ansible/index.html`: Simple HTML file used as a test page for the web server
- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring HTTPS website
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use ansible-lint for basic compliance checks
  - Option 2: Integrate with Ansible Automation Platform's compliance capabilities
  - Option 3: Keep InSpec as a standalone tool but invoke it from Ansible

- **Test Kitchen with Vagrant**: Replace with:
  - Molecule for Ansible role testing
  - ansible-test for collection testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Migration approach: Convert to an Ansible role with appropriate variables for SSL protocols
  
- **SSH Security Controls**: The SSH compliance checks must be preserved
  - Migration approach: Convert InSpec tests to Ansible assert tasks or ansible-lint rules

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible validation
  - Mitigation: Use assert modules in Ansible or consider keeping InSpec for testing while standardizing on Ansible for configuration

- **Compliance Reporting**: Maintaining compliance reporting capabilities
  - Mitigation: Integrate with Ansible Automation Platform's compliance capabilities or use a dedicated compliance tool

### Migration Order

1. **website-https playbook** (already Ansible, low risk)
   - Convert to a proper Ansible role with variables
   - Improve idempotence and error handling

2. **poodle-fix playbook** (already Ansible, low risk)
   - Integrate into the website-https role as a security hardening task
   - Add conditional logic for different Apache versions

3. **InSpec tests** (moderate complexity)
   - Convert to Ansible assert tasks where possible
   - For complex compliance checks, consider keeping InSpec and integrating with Ansible

4. **Chef deployment scripts** (high complexity)
   - Replace with Ansible playbooks for deploying alternative automation platforms
   - Consider migrating to Ansible Automation Platform

### Assumptions

1. The primary goal is to standardize on Ansible while maintaining the compliance testing capabilities
2. The InSpec tests are valuable and need to be preserved in some form
3. The Chef Automate and Chef Infra Server deployment scripts may be replaced with equivalent Ansible automation
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. Vagrant will continue to be used for development/testing environments