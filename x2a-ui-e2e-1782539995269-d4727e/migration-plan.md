# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites with security compliance
2. Chef InSpec test profiles for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is **LOW to MEDIUM** with an estimated timeline of **1-2 weeks** due to the limited number of components and their relatively straightforward functionality. The primary focus will be on preserving the compliance testing capabilities while consolidating everything into Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Ansible playbook that configures Apache with HTTPS, self-signed certificates, and a basic website
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-vulnerability-fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **https-compliance-tests**:
    - Description: Chef InSpec profile for verifying HTTPS configuration and website availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening tests, HTTPS content verification, SSL protocol security checks

- **ssh-security-compliance**:
    - Description: Chef InSpec profile for verifying SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration verification, security compliance checks with STIG references

- **chef-infrastructure-deployment**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash scripts with Chef commands
    - Key Features: Chef server deployment, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and verifying with InSpec
- `index.html`: Sample HTML file used in the website deployment example

### Target Details

Analyzing the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use ansible-lint for static analysis
  - Option 2: Use Molecule for Ansible role testing
  - Option 3: Maintain InSpec as a separate tool but invoke it from Ansible

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Simple Vagrant or Docker-based testing scripts

- **Chef Automate/Infra Server**: Replace with:
  - Option 1: Ansible Tower/AWX for enterprise orchestration
  - Option 2: GitLab CI/CD or Jenkins for pipeline orchestration

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Approach: Convert to an Ansible role with appropriate variables for SSL protocols
  
- **SSH Security**: Maintain the SSH hardening checks from the InSpec profile
  - Approach: Convert to Ansible security role with appropriate checks

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible verification
  - Mitigation: Consider using Ansible assert modules or maintaining InSpec as a separate tool called from Ansible

- **Compliance Reporting**: Maintaining compliance reporting capabilities without Chef Automate
  - Mitigation: Implement custom reporting using Ansible callback plugins or integrate with tools like Prometheus/Grafana

### Migration Order

1. **website-https-configuration** (low risk, already in Ansible)
   - Convert to a proper Ansible role with variables
   - Add documentation

2. **poodle-vulnerability-fix** (low risk, already in Ansible)
   - Integrate into the HTTPS configuration role as a security option
   - Add documentation

3. **InSpec Tests** (medium complexity)
   - Decide on testing strategy (keep InSpec or migrate to Ansible-native)
   - Implement chosen approach

4. **Chef Infrastructure Deployment** (high complexity)
   - Replace with Ansible playbooks for deploying alternative orchestration platform
   - Implement user/organization management in the new platform

### Assumptions

1. The primary goal is to consolidate on Ansible rather than maintain a hybrid Chef/Ansible environment
2. The InSpec tests are valuable and their functionality should be preserved in some form
3. The deployment scripts for Chef infrastructure will be replaced with equivalent Ansible automation for a different orchestration platform
4. The target environment will remain Ubuntu 20.04 or compatible
5. The security compliance requirements (STIG references in InSpec tests) must be maintained
6. No external data sources or databases are involved in the current implementation
7. No complex state management is required beyond what's visible in the playbooks