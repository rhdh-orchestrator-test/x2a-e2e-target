# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec tests for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while standardizing on Ansible for all infrastructure provisioning.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Apache web server configuration with HTTPS/SSL setup and self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **ssl-poodle-remediation**:
    - Description: Security fix for POODLE vulnerability in SSL configurations
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enforces TLSv1.2

- **https-compliance-tests**:
    - Description: InSpec tests for verifying HTTPS configuration and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS response validation, SSL protocol verification

- **ssh-security-compliance**:
    - Description: InSpec profile for SSH security compliance checking
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **chef-infrastructure-deployment**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts
    - Key Features: Chef server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for website testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use ansible-lint for basic compliance checks
  - Option 2: Integrate with Ansible Automation Platform's compliance capabilities
  - Option 3: Maintain InSpec as a separate tool but invoke it from Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - ansible-test for collection testing

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 enforcement is maintained
  - Consider updating to include TLSv1.3 support

- **SSH Security**: Maintain the SSH security controls from the InSpec profile
  - Convert InSpec tests to Ansible assert tasks or ansible-lint rules

- **Vault/secrets management**:
  - Hardcoded credentials detected in setup scripts (username, password)
  - Replace with Ansible Vault for secure credential storage
  - Consider integrating with external secret management systems

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible verification methods
  - Mitigation: Use assert modules in Ansible or consider maintaining InSpec for testing only

- **Compliance Reporting**: Ensuring equivalent compliance reporting capabilities
  - Mitigation: Explore Ansible Automation Platform's compliance features or integrate with external compliance tools

### Migration Order

1. **website-https-configuration** (low risk, already in Ansible)
   - Review and optimize existing Ansible playbook
   - Convert to Ansible role structure for better reusability

2. **ssl-poodle-remediation** (low risk, already in Ansible)
   - Integrate with website-https-configuration role
   - Update to include latest SSL/TLS best practices

3. **chef-infrastructure-deployment** (moderate complexity)
   - Convert bash scripts to Ansible playbooks
   - Implement secure credential handling

4. **https-compliance-tests** and **ssh-security-compliance** (high complexity)
   - Evaluate options for compliance testing in Ansible ecosystem
   - Implement chosen solution (ansible-lint, assert tasks, or maintain InSpec)

### Assumptions

1. The primary purpose of this repository is demonstrating Chef InSpec with Ansible rather than production deployment
2. The target environment will continue to be Ubuntu 20.04 or compatible systems
3. Vagrant will continue to be used for development/testing environments
4. There are no external dependencies or integrations beyond what's visible in the repository
5. The Chef Automate and Chef Infra Server deployment scripts are for demonstration purposes and not critical production components
6. The security compliance requirements (SSH configuration, SSL protocols) will remain consistent during migration
7. No database or complex state management is required
8. No custom modules or complex logic exists that would require special handling