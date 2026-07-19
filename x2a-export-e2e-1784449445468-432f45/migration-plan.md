# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, with two main components:

1. Chef InSpec tests for compliance verification
2. Ansible playbooks for web server configuration and security hardening

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while consolidating all infrastructure provisioning into Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **inspec-tests**:
    - Description: Chef InSpec tests that verify HTTPS functionality, security compliance, and SSH hardening
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: Port listening verification, HTTPS response validation, SSL protocol security checks, SSH configuration validation

- **chef-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
  - Migration consideration: Replace with Ansible-native testing framework like Molecule

- `index.html`: Sample HTML file for testing web server functionality
  - Migration consideration: Preserve as a template file for Ansible

## Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Keep InSpec as a standalone tool but invoke it from Ansible

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality for testing Ansible roles with various drivers and verifiers

- **Chef Automate/Server**: Replace with Ansible Automation Platform or AWX
  - For enterprise automation, orchestration, and compliance reporting

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure the Apache SSL configuration continues to enforce TLSv1.2 and disable insecure protocols

- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates
  - Consider enhancing with Let's Encrypt integration for production environments

- **SSH Hardening**: The ssh_profile.rb InSpec test verifies SSH security compliance
  - Ensure SSH hardening is implemented in the Ansible roles
  - Maintain compliance with referenced security standards (STIG)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **Compliance Testing**: Transitioning from InSpec to Ansible-native testing
  - Challenge: InSpec provides rich compliance testing capabilities that may be difficult to replicate in Ansible
  - Mitigation: Consider using Ansible to invoke InSpec tests or integrate with other compliance tools

- **Test Kitchen to Molecule**: Converting test infrastructure
  - Challenge: Ensuring test coverage and functionality remains consistent
  - Mitigation: Create equivalent Molecule scenarios for each Test Kitchen suite

- **Chef Automate Functionality**: Replacing Chef Automate's compliance reporting
  - Challenge: Finding equivalent functionality in Ansible ecosystem
  - Mitigation: Evaluate Ansible Automation Platform or integrate with compliance tools like OpenSCAP

### Migration Order

1. **website-https** and **poodle-fix** playbooks (low risk, already in Ansible)
   - Consolidate into a single role with appropriate tags for selective execution
   - Enhance with Ansible best practices (variables, handlers, templates)

2. **inspec-tests** (moderate complexity)
   - Convert to Ansible assert tasks or maintain as InSpec tests invoked by Ansible
   - Ensure compliance reporting is preserved

3. **chef-deployment** (high complexity)
   - Replace with Ansible roles for deploying Ansible Automation Platform or AWX
   - Migrate user and organization management to Ansible inventory and AAP/AWX

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than production deployment
2. The security compliance requirements (STIG references) must be maintained in the migrated solution
3. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
4. Self-signed certificates are acceptable for the demonstration environment
5. The hardcoded credentials in the deployment scripts are for demonstration purposes only
6. The Apache configuration is relatively simple and doesn't include complex customizations
7. There are no external dependencies or integrations beyond what's visible in the repository
8. Test Kitchen is used primarily for demonstration and not as part of a CI/CD pipeline