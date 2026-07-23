# MIGRATION FROM ANSIBLE WITH CHEF INSPEC TO ANSIBLE

## Executive Summary

This repository contains a mixed environment with Ansible playbooks for configuration management and Chef InSpec for compliance testing. The migration scope involves converting the existing Ansible playbooks to a more structured Ansible format while preserving the compliance testing capabilities currently provided by Chef InSpec.

The repository appears to be a demonstration environment showing how Chef InSpec can be used alongside Ansible for compliance automation. It also contains scripts for setting up Chef Automate and Chef Infra Server environments.

**Estimated Timeline:** 2-3 weeks for a small team (2-3 people)
**Complexity:** Medium - The existing Ansible playbooks are relatively straightforward, but integrating compliance testing into pure Ansible will require careful planning.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (STIG)

- **automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and verifying with InSpec
- `index.html`: Sample HTML file for the web server
- `README.md`: Documentation files explaining the purpose of the examples

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - **Option 1**: Use Ansible's assert module for basic compliance checks
  - **Option 2**: Integrate with Molecule for more comprehensive testing
  - **Option 3**: Use ansible-lint for static analysis of playbooks
  - **Option 4**: Consider OpenSCAP integration for compliance scanning

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - GitHub Actions or other CI/CD pipeline for automated testing

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure the migration preserves:
  - Proper certificate generation
  - Secure protocol settings (TLSv1.2 only, no SSLv3)
  - Appropriate file permissions for certificates

- **SSH Security**: The InSpec tests verify SSH security configurations:
  - Ensure the migration includes equivalent checks for SSH root login
  - Maintain compliance with security standards (STIG)

- **Vault/secrets management**:
  - Hardcoded credentials in the deploy scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **Compliance Testing**: The primary challenge is replacing Chef InSpec with equivalent Ansible-native testing:
  - InSpec provides a domain-specific language for compliance testing that is more expressive than Ansible's built-in testing capabilities
  - Consider using a combination of Ansible assert module and custom modules to achieve similar functionality

- **Test Kitchen Integration**: The current setup uses Test Kitchen to orchestrate testing:
  - Molecule provides similar functionality for Ansible but with a different workflow
  - Migration will require adapting the testing workflow

- **Certificate Management**: The current playbook generates self-signed certificates:
  - Consider using Ansible's crypto modules for certificate management
  - Evaluate whether to continue with self-signed certificates or integrate with Let's Encrypt

### Migration Order

1. **website_https playbook** (Priority 1): Core web server configuration
   - Convert to Ansible role with proper structure
   - Implement idempotent certificate management
   - Add proper variable management

2. **poodle_fix playbook** (Priority 2): Security hardening
   - Integrate into the web server role as a security task
   - Ensure idempotence with proper state checking

3. **Testing Framework** (Priority 3): Replace Chef InSpec
   - Implement Molecule testing framework
   - Create equivalent tests using Ansible assertions or custom modules

4. **Deployment Scripts** (Priority 4): Chef Automate/Server deployment
   - Convert bash scripts to Ansible roles for Chef infrastructure deployment
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The primary goal is to migrate from a mixed Ansible/Chef InSpec environment to pure Ansible while maintaining equivalent functionality.
2. The Chef Automate and Chef Infra Server deployment scripts are intended for setting up testing infrastructure and may not be needed in the final Ansible implementation.
3. The security compliance requirements (STIG standards mentioned in InSpec tests) must be maintained in the Ansible implementation.
4. The target environment will continue to be Ubuntu 20.04 or compatible systems.
5. The self-signed certificate approach is acceptable for the migrated solution rather than integrating with a certificate authority.
6. The current implementation is for demonstration/example purposes and may need to be enhanced for production use.
7. The hardcoded credentials in the deployment scripts are for demonstration purposes only and will be replaced with secure credential management in the final implementation.