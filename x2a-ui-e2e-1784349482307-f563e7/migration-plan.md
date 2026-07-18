# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Ansible playbooks and Chef InSpec tests that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting the existing Ansible playbooks to a more structured Ansible role-based approach while preserving the compliance testing functionality currently provided by Chef InSpec.

**Estimated Timeline**: 1-2 weeks for a single developer, including testing and documentation.
**Complexity**: Low to Medium - The existing Ansible playbooks are straightforward, but the InSpec tests will need to be replaced with equivalent Ansible testing mechanisms.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Collection of Ansible playbooks with Chef InSpec tests for compliance validation
    - Path: chef-and-ansible
    - Technology: Ansible + Chef InSpec
    - Key Features: Apache HTTPS setup, SSL security configuration, compliance testing

- **chef-and-ansible/tests**:
    - Description: Chef InSpec tests for validating security compliance
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSH security validation

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/index.html`: Sample HTML file for the web server
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec test that verifies HTTPS functionality and security
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec control that verifies SSH root login is disabled
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server without Automate

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace InSpec tests with equivalent Ansible Molecule tests
  - Consider using ansible-lint for static code analysis
  - For compliance testing, consider using ansible-compliance or integrating with OpenSCAP

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure
  - Molecule provides similar functionality for testing Ansible roles
  - Supports multiple drivers including Vagrant, Docker, and cloud providers

- **Vagrant**: Can be retained as a provider for local testing or replaced with Docker for faster testing cycles

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced
  - Consider updating to also include TLSv1.3 support

- **SSH Security**: The SSH root login check must be preserved
  - Convert the InSpec control to an equivalent Ansible assertion or Molecule verification

- **Certificate Management**: The self-signed certificate generation should be preserved
  - Consider enhancing with Let's Encrypt support for production environments

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - No other credentials were detected in the repository

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible/Molecule tests
  - Challenge: InSpec has specific matchers and resources that may not have direct equivalents
  - Mitigation: Use Molecule's verify phase with custom Python test scripts or Testinfra

- **Compliance Testing**: Maintaining compliance validation capabilities
  - Challenge: InSpec is specifically designed for compliance testing
  - Mitigation: Evaluate ansible-compliance or integrate with OpenSCAP for compliance reporting

- **Chef Automate Deployment**: Replacing Chef Automate deployment scripts
  - Challenge: Determining if Chef Automate is still needed after migration
  - Mitigation: If Chef Automate is only used for InSpec reporting, consider alternatives like AWX/Tower

### Migration Order

1. **Ansible Playbooks** (Priority 1, low risk)
   - Convert website_https.yml and poodle_fix.yml to an Ansible role with proper structure
   - Implement idempotency improvements
   - Add proper variable handling

2. **InSpec Tests** (Priority 2, moderate complexity)
   - Convert to Molecule tests
   - Ensure equivalent coverage for security checks

3. **Chef Automate Deployment** (Priority 3, evaluate necessity)
   - Determine if Chef Automate is still needed
   - If needed, convert deployment scripts to Ansible roles

### Assumptions

1. The primary purpose of this repository is to demonstrate InSpec with Ansible, not for production use
2. The Chef Automate deployment scripts are examples and may not be needed in the final Ansible-only solution
3. The target environment will continue to be Ubuntu 20.04 or compatible
4. No external dependencies or integrations beyond what's visible in the repository
5. No complex state management or database interactions are present
6. The migration will preserve all current functionality including security checks
7. Test Kitchen is only used for development/testing and not for production deployments