# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef Automate/Chef Infra Server setup scripts. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a standardized Ansible structure while preserving the compliance testing capabilities currently provided by Chef InSpec.

**Estimated Timeline**: 1-2 weeks for a single engineer, including testing and documentation.
**Complexity**: Low to Medium - The existing Ansible playbooks are straightforward, but integrating the compliance testing functionality will require careful planning.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS configuration and security compliance
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS response validation, SSL protocol security verification

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Static HTML file for the website example

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Convert InSpec tests to Ansible assert modules and blocks
  - Option 2: Use ansible-lint for static analysis
  - Option 3: Integrate with Molecule for testing
  - Option 4: Keep InSpec as a separate tool but invoke it from Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role/playbook testing
  - Vagrant directly for local testing if needed

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in poodle_fix.yml
  - Ensure TLSv1.2 remains the only enabled protocol
  - Maintain proper service restarts after configuration changes

- **Self-signed Certificates**: The migration should maintain the same level of certificate security
  - Consider using ansible.builtin.openssl_* modules which are already in use

- **Vault/secrets management**:
  - No encrypted secrets were found in the current repository
  - Consider implementing Ansible Vault for the hardcoded passwords in the Chef server deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible's testing capabilities
  - Mitigation: Use Ansible's assert module combined with uri module to check HTTP responses
  - For SSL protocol verification, use the openssl_certificate_info module

- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible
  - Mitigation: Create an Ansible role for Chef server deployment if this functionality is still needed
  - Alternative: If Chef is being completely replaced, this component can be removed

### Migration Order

1. **website_https.yml** (Priority 1 - already Ansible, just needs restructuring)
   - Convert to Ansible role with proper directory structure
   - Add documentation

2. **poodle_fix.yml** (Priority 1 - already Ansible, just needs restructuring)
   - Convert to Ansible role or include in the website_https role
   - Add documentation

3. **website_https_verify.rb** (Priority 2 - requires conversion from InSpec to Ansible)
   - Convert InSpec tests to Ansible assertions
   - Integrate with Molecule testing framework

4. **Chef Server Deployment Scripts** (Priority 3 - only if still needed)
   - Convert bash scripts to Ansible roles if Chef infrastructure is still required
   - Otherwise document as deprecated

### Assumptions

1. The primary goal is to standardize on Ansible and remove Chef dependencies where possible
2. InSpec testing functionality needs to be preserved in some form
3. The Chef server deployment scripts may no longer be needed if fully migrating away from Chef
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. The repository is primarily for demonstration/example purposes rather than production use
6. No external inventory or variable files exist that weren't discovered in the analysis