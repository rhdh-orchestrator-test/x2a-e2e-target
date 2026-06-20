# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites with Apache
2. Chef InSpec tests for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while standardizing on Ansible for all configuration management.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Apache web server configuration with HTTPS, self-signed certificates, and security hardening
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL/TLS configuration, virtual host setup, self-signed certificate generation

- **poodle-vulnerability-fix**:
    - Description: Security patch for POODLE vulnerability in SSL/TLS configuration
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enforces TLSv1.2

- **compliance-testing**:
    - Description: InSpec tests for verifying HTTPS configuration and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL/TLS protocol testing, SSH root login security check

- **chef-infrastructure-deployment**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts
    - Key Features: Chef server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing framework or adapting to use Molecule.
- `index.html`: Simple HTML file used as website content. No special migration considerations.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Maintain InSpec as a complementary tool called from Ansible
  - Option 4: Migrate to Molecule for testing Ansible roles

- **Test Kitchen**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening that disables vulnerable protocols (SSL3) and enforces TLSv1.2
  - Approach: Create dedicated Ansible role for Apache SSL hardening with appropriate templates

- **SSH Security Hardening**: Maintain compliance checks for SSH root login restrictions
  - Approach: Create Ansible tasks to enforce SSH configuration and add assert statements to verify compliance

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **Compliance Testing Framework**: The repository demonstrates Chef InSpec for compliance testing with Ansible. Deciding on a testing approach that maintains the same level of compliance verification while standardizing on Ansible tools will be the main challenge.
  - Mitigation: Evaluate Ansible's built-in assert module, Molecule, and other testing frameworks to determine the best fit for compliance testing needs.

- **Test Kitchen Integration**: The current setup uses Test Kitchen to orchestrate Ansible and InSpec. This will need to be replaced with an Ansible-native testing approach.
  - Mitigation: Implement Molecule for testing Ansible roles, which provides similar functionality to Test Kitchen but is designed specifically for Ansible.

### Migration Order

1. **website-https-configuration** (low risk, already in Ansible)
   - Convert to proper Ansible role structure
   - Add documentation
   - Implement idempotency improvements

2. **poodle-vulnerability-fix** (low risk, already in Ansible)
   - Integrate into the website-https role as a security hardening task
   - Add conditional logic for different Apache versions

3. **compliance-testing** (moderate complexity)
   - Develop equivalent tests using Ansible's testing capabilities
   - Ensure all security checks are preserved

4. **chef-infrastructure-deployment** (high complexity)
   - Determine if Chef infrastructure is still needed
   - If not, document removal process
   - If yes, create Ansible playbooks to replace bash scripts for Chef deployment

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than to provide production-ready infrastructure code.
2. The Chef Automate and Chef Infra Server deployment scripts are examples and may not be needed in the final Ansible implementation.
3. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
4. The security compliance requirements (TLS 1.2, SSH hardening) must be maintained in the migrated solution.
5. There is no external dependency on Chef beyond the InSpec testing tool.
6. The migration will standardize on Ansible while maintaining or improving the compliance testing capabilities currently provided by InSpec.