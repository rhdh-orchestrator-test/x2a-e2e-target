# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The estimated timeline for this migration is 1-2 weeks, with low complexity as most of the configuration is already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash scripts
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used as a test page for the web server. No migration needed as it's a static content file.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace InSpec tests with Ansible Molecule for infrastructure testing
  - Consider using ansible-lint for static code analysis
  - For compliance testing, evaluate OpenSCAP with ansible-playbook or ansible.posix.scan module

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in poodle_fix.yml that disables SSLv3 and enables only TLSv1.2
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates; ensure this functionality is preserved
- **SSH Security**: The ssh_profile.rb InSpec test verifies SSH root login is disabled; this compliance check must be maintained
- **Vault/secrets management**:
  - Hardcoded credentials detected in setup-automate scripts (username, password)
  - Recommend migrating these to Ansible Vault

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing frameworks will require understanding the specific assertions and controls
  - Mitigation: Use Ansible assert module or Molecule verifiers to replicate InSpec tests
  
- **Compliance Testing**: InSpec provides built-in resources for compliance testing that may not have direct equivalents in Ansible
  - Mitigation: Evaluate OpenSCAP integration or custom Ansible modules for compliance checks

- **Test Kitchen Integration**: The current setup uses Test Kitchen to orchestrate Ansible and InSpec
  - Mitigation: Replace with Molecule for Ansible-native testing workflow

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they can remain largely unchanged
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible-native testing solutions
3. **Test Kitchen Configuration** (kitchen.yml): Replace with Molecule configuration
4. **Chef Automate Deployment Scripts**: Convert Bash scripts to Ansible roles for Chef server deployment

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependency while preserving the security testing capabilities
2. The existing Ansible playbooks are functioning correctly and don't require significant modifications
3. There's no requirement to maintain backward compatibility with Chef InSpec
4. The deployment scripts for Chef Automate and Chef Server will be replaced with Ansible equivalents rather than maintained for Chef deployment
5. No external data sources or complex variable management is present in the current implementation
6. The target environment will continue to be Ubuntu 20.04 or compatible systems
7. The self-signed certificates are acceptable for the environment (not production)
8. No complex authentication mechanisms are in place beyond what's visible in the scripts