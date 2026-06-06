# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components that demonstrate how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, focusing on:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec tests for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while standardizing on Ansible for all infrastructure provisioning.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Ansible playbook for configuring Apache web server with HTTPS support, including self-signed certificate generation
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-vulnerability-fix**:
    - Description: Ansible playbook for remediating SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **https-compliance-tests**:
    - Description: Chef InSpec tests for verifying HTTPS configuration and SSL security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening verification, HTTPS response validation, SSL protocol security checks

- **ssh-security-compliance**:
    - Description: Chef InSpec profile for SSH security compliance checking
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Shell script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible-native testing framework or adapt to use Molecule.
- `index.html`: Simple HTML file used for testing web server deployment. Migration consideration: Preserve as-is or incorporate into Ansible templates.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Maintain InSpec as a complementary tool for compliance testing
  - Option 4: Migrate to Ansible Molecule for testing

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that can:
  - Option 1: Deploy alternative compliance and automation tools (e.g., AWX/Ansible Tower)
  - Option 2: Maintain Chef Automate deployment capability via Ansible if required

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening that disables SSLv3 and enables only TLSv1.2
  - Migration approach: Create dedicated Ansible role for Apache SSL hardening

- **SSH Security**: Maintain compliance checks for SSH configuration
  - Migration approach: Convert InSpec tests to Ansible assert statements or maintain as InSpec tests

- **Vault/secrets management**:
  - Hardcoded credentials detected in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Compliance Testing**: The primary challenge is maintaining the compliance testing capabilities currently provided by Chef InSpec
  - Mitigation strategy: Either maintain InSpec as a complementary tool or develop equivalent testing in Ansible

- **Test Kitchen Integration**: The current setup uses Test Kitchen to orchestrate Ansible and InSpec
  - Mitigation strategy: Migrate to Ansible Molecule for a more Ansible-native testing approach

### Migration Order

1. **website-https-configuration** (low risk, already in Ansible)
   - Convert to Ansible role structure
   - Enhance with best practices (variables, handlers)

2. **poodle-vulnerability-fix** (low risk, already in Ansible)
   - Incorporate into the HTTPS configuration role
   - Add conditional logic for applying the fix

3. **https-compliance-tests** and **ssh-security-compliance** (moderate complexity)
   - Decision point: Convert to Ansible assertions or maintain as InSpec

4. **chef-automate-deployment** and **chef-server-deployment** (high complexity)
   - Convert shell scripts to Ansible playbooks
   - Implement secure credential handling

### Assumptions

1. The primary goal is standardizing on Ansible while maintaining compliance capabilities
2. Chef InSpec tests may be preserved if they provide value not easily replicated in Ansible
3. The deployment of Chef Automate/Infra Server may be replaced with alternative tools
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. The security requirements (SSL/TLS, SSH) must be maintained or enhanced
6. Test Kitchen can be replaced with Ansible Molecule without loss of functionality
7. The example website configuration is representative of actual production needs