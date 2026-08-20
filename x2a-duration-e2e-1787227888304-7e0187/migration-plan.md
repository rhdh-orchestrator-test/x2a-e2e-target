# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef Automate and Chef Infra Server setup scripts. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a more standardized Ansible structure while preserving the compliance testing capabilities currently provided by Chef InSpec.

**Estimated Timeline**: 1-2 weeks for a single engineer, including testing and documentation.

**Complexity**: Low to Medium - The existing Ansible playbooks are straightforward, but integrating the compliance testing functionality currently provided by Chef InSpec will require careful planning.

## Module Migration Plan

This repository contains Ansible playbooks and Chef components that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS configuration and security compliance
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening tests, HTTPS response validation, SSL protocol security verification

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Static HTML content for the website

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static code analysis
  - Option 3: Convert InSpec tests to Molecule tests for Ansible role testing
  - Option 4: Maintain InSpec as a separate tool but invoke it from Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible Playbook integration tests using the `ansible-playbook --check` mode

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Tower/AWX for orchestration and management
  - GitLab CI/CD or GitHub Actions for pipeline automation
  - Ansible Collections for role and module management

### Security Considerations

- **SSL Configuration**: The current playbooks configure SSL with self-signed certificates and harden against POODLE vulnerability
  - Migration approach: Preserve the same security hardening in Ansible roles
  - Consider using Ansible Vault for certificate management

- **Compliance Testing**: Currently using InSpec for compliance validation
  - Migration approach: Implement equivalent tests using Ansible's assert module or maintain InSpec tests but invoke them from Ansible

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected in deploy scripts

### Technical Challenges

- **Compliance Testing**: The InSpec tests provide valuable security validation that must be preserved
  - Mitigation: Either maintain InSpec as a separate tool or implement equivalent tests using Ansible's native capabilities

- **Integration Testing**: The current setup uses Test Kitchen for integration testing
  - Mitigation: Implement equivalent testing using Molecule or another Ansible-compatible testing framework

### Migration Order

1. **website_https playbook** (Priority 1): Convert to an Ansible role with proper structure
   - Create role with tasks, handlers, templates, and defaults
   - Move inline templates to template files
   - Implement variable defaults

2. **poodle_fix playbook** (Priority 1): Convert to an Ansible role or include in the website_https role
   - Create dedicated tasks for security hardening
   - Implement idempotent checks

3. **InSpec tests** (Priority 2): Convert to Ansible assertions or maintain as separate tests
   - Create equivalent tests using Ansible's assert module
   - Implement test playbooks that can be run in check mode

4. **Chef Automate/Server deployment scripts** (Priority 3): Convert to Ansible roles
   - Create roles for Ansible Tower/AWX deployment
   - Implement user and organization management through Ansible

### Assumptions

1. The primary goal is to standardize on Ansible and remove Chef dependencies where possible
2. The InSpec tests are valuable and their functionality should be preserved
3. The deployment scripts for Chef Automate/Server will be replaced with equivalent Ansible Tower/AWX deployment
4. The current Ansible playbooks are functional but need restructuring into proper roles
5. No custom Chef cookbooks or resources are in use beyond what's visible in the repository
6. The target environment will continue to be Ubuntu 20.04 or compatible systems
7. The self-signed certificates are acceptable for the target environment
8. The hardcoded credentials in the deployment scripts are for demonstration purposes only