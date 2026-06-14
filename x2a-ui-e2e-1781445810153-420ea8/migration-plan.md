# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites with security compliance
2. Chef InSpec tests for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is **LOW** with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while standardizing on Ansible for all infrastructure provisioning.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Apache web server configuration with HTTPS, self-signed certificates, and security hardening
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL/TLS configuration, virtual host setup, self-signed certificate generation

- **poodle-vulnerability-fix**:
    - Description: Security fix for POODLE vulnerability in SSL/TLS by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL module configuration, security hardening

- **compliance-testing**:
    - Description: Chef InSpec tests for verifying HTTPS configuration and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: Port verification, HTTPS content verification, SSL/TLS protocol verification, SSH root login verification

- **chef-infrastructure-deployment**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash
    - Key Features: Chef server deployment, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and verifying with InSpec. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Sample HTML file used for testing web server deployment. Can be directly incorporated into Ansible content.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Keep InSpec as a standalone tool called from Ansible

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Infra Server**: Evaluate if these components are needed or if they can be replaced with:
  - Ansible Tower/AWX for orchestration
  - GitLab CI/CD or GitHub Actions for pipeline automation
  - Compliance scanning tools like OpenSCAP or Ansible's built-in security automation

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and enables only TLSv1.2
  - Migration approach: Preserve the same Apache configuration settings in Ansible tasks

- **Self-signed Certificates**: The current implementation generates self-signed certificates
  - Migration approach: Use Ansible's `openssl_*` modules as already implemented

- **SSH Security Hardening**: InSpec tests verify SSH root login is disabled
  - Migration approach: Implement equivalent checks using Ansible's assert module or maintain InSpec tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Compliance Testing**: The primary challenge is replacing or integrating Chef InSpec tests
  - Mitigation: Either maintain InSpec as a standalone tool called from Ansible or implement equivalent tests using Ansible's native capabilities

- **Test Kitchen Integration**: The current setup uses Test Kitchen to orchestrate Ansible and InSpec
  - Mitigation: Replace with Molecule which is designed specifically for Ansible testing

### Migration Order

1. **website-https-configuration** (low risk, already in Ansible)
   - Review and optimize existing Ansible playbook
   - Add documentation and variable parameterization

2. **poodle-vulnerability-fix** (low risk, already in Ansible)
   - Integrate into the main website configuration playbook
   - Add conditional logic if needed

3. **compliance-testing** (moderate complexity)
   - Decide on testing strategy (keep InSpec or migrate to Ansible-native)
   - Implement chosen testing approach

4. **chef-infrastructure-deployment** (high complexity)
   - Determine if Chef infrastructure is still needed
   - If not, remove; if yes, create Ansible playbooks to replace shell scripts

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being production infrastructure code
2. The Chef components (Automate, Infra Server) are not critical to the functionality and may be removed
3. The compliance testing functionality is the most important aspect to preserve
4. No external systems or services depend on the current implementation
5. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
6. No specific cloud provider integration is required
7. The hardcoded credentials in the setup scripts are for demonstration purposes only