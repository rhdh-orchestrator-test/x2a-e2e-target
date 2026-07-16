# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mixed environment of Chef and Ansible components focused on compliance automation and Chef server deployment. The migration scope is relatively small, with two main components:

1. A Chef InSpec compliance testing framework used alongside Ansible playbooks
2. Chef Automate and Chef Infra Server deployment scripts

The migration complexity is **LOW to MEDIUM** with an estimated timeline of 1-2 weeks. The primary challenge will be replacing Chef InSpec compliance testing with Ansible-native solutions while maintaining the same level of compliance validation.

## Module Migration Plan

This repository contains Chef and Ansible technologies that need individual migration planning:

### MODULE INVENTORY

- **website-https-deployment**:
    - Description: Apache web server deployment with HTTPS configuration, self-signed certificates, and security hardening
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL/TLS configuration, virtual host setup, self-signed certificate generation

- **poodle-vulnerability-fix**:
    - Description: Security patch for POODLE vulnerability in SSL/TLS configurations
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3, enforces TLSv1.2

- **compliance-testing**:
    - Description: Chef InSpec tests for validating HTTPS configuration and SSH security settings
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS validation, SSL/TLS protocol verification, SSH root login security check

- **chef-infrastructure-deployment**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts for Chef deployment
    - Key Features: User and organization creation, Chef server configuration

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `index.html`: Simple HTML test page for web server deployment
- `deploy-automate.sh`: Script to deploy Chef Automate and Chef Infra Server
- `deploy-chef-server.sh`: Script to deploy Chef Infra Server only

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with on-premises focus

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - For compliance testing: Use ansible-lint for static analysis
  - For runtime validation: Use Ansible assert module or Molecule for testing
  - Alternative: Consider integrating with OpenSCAP or DISA STIG tools

- **Test Kitchen**: Replace with Molecule for Ansible role/playbook testing

- **Chef Automate/Infra Server**: Evaluate if these need to be replaced with:
  - AWX/Ansible Tower for orchestration
  - Ansible Automation Platform for compliance reporting
  - GitLab CI/CD or Jenkins for pipeline integration

### Security Considerations

- **SSL/TLS Configuration**: The current implementation enforces TLSv1.2 and disables SSLv3 to address POODLE vulnerability
  - Migration approach: Maintain the same security posture in Ansible playbooks using the same configuration parameters
  
- **SSH Security**: InSpec tests verify SSH root login is disabled
  - Migration approach: Implement equivalent checks using Ansible assert module or ansible-lint

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Compliance Testing**: Replacing Chef InSpec with Ansible-native testing
  - Mitigation: Use a combination of ansible-lint, assert module, and potentially Molecule for testing
  - Consider maintaining InSpec as a standalone tool if needed for specific compliance requirements

- **Certificate Management**: Self-signed certificate generation
  - Mitigation: Use Ansible's openssl_* modules (already in use in the current playbooks)

### Migration Order

1. **website-https-deployment** (low risk, already in Ansible)
   - No migration needed, already implemented as Ansible playbook
   - Review and optimize according to current Ansible best practices

2. **poodle-vulnerability-fix** (low risk, already in Ansible)
   - No migration needed, already implemented as Ansible playbook
   - Consider integrating into the main website-https-deployment playbook

3. **compliance-testing** (medium complexity)
   - Convert InSpec tests to Ansible assertions or Molecule tests
   - Implement ansible-lint checks for static validation

4. **chef-infrastructure-deployment** (high complexity)
   - Determine if Chef infrastructure is still needed
   - If not, replace with Ansible Automation Platform or AWX/Tower
   - If yes, maintain scripts but improve security by implementing Ansible Vault

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment
2. The Chef Automate and Chef Infra Server deployment is intended for testing/demo purposes
3. The hardcoded credentials in the deployment scripts are not used in production environments
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. There is no existing CI/CD pipeline integration that needs to be preserved
6. The compliance testing requirements will remain the same after migration
7. The team has expertise in both Chef and Ansible technologies