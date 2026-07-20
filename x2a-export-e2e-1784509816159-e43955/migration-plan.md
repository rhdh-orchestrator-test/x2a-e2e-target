# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be consolidated into a unified Ansible approach. The repository primarily consists of:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks for configuring HTTPS websites with Apache
3. Chef InSpec tests for compliance verification

The migration complexity is relatively low as most of the configuration is already in Ansible format. The primary focus will be on replacing the Chef Automate/Infra Server deployment scripts with Ansible equivalents and ensuring the InSpec tests can be integrated into an Ansible-based workflow. Estimated timeline: 1-2 weeks for a complete migration.

## Module Migration Plan

This repository contains Chef and Ansible configurations that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring HTTPS websites with Apache and InSpec tests for compliance verification
    - Path: chef-and-ansible
    - Technology: Ansible + Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL/TLS security settings, InSpec compliance testing for HTTPS and SSH

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash + Chef
    - Key Features: Chef Automate deployment, Chef Infra Server configuration, user and organization setup

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that configures Apache with HTTPS support, creates self-signed certificates, and deploys a simple website. Migration considerations: Can be directly used in the Ansible environment with minimal changes.
  
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that addresses SSL POODLE vulnerability by enforcing TLSv1.2. Migration considerations: Can be directly used in the Ansible environment with minimal changes.
  
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec. Migration considerations: Will need to be updated to use Ansible-native testing frameworks or adapted to work with the new Ansible structure.
  
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS website functionality. Migration considerations: Can be integrated with Ansible using ansible-test or molecule with an InSpec verifier.
  
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Migration considerations: Can be integrated with Ansible using ansible-test or molecule with an InSpec verifier.
  
- `setup-automate/deploy-automate.sh`: Bash script to deploy Chef Automate and Chef Infra Server. Migration considerations: Needs to be replaced with Ansible playbooks for infrastructure setup.
  
- `setup-automate/deploy-chef-server.sh`: Bash script to deploy Chef Infra Server. Migration considerations: Needs to be replaced with Ansible playbooks for infrastructure setup.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and package versions in the Ansible playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but the scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for infrastructure management
- **Chef InSpec**: Integrate with Ansible using one of these approaches:
  1. Use ansible-test framework with InSpec verifier
  2. Use Molecule with InSpec verifier
  3. Create custom Ansible roles that execute InSpec tests
  4. Consider migrating to Ansible-native testing with testinfra
- **Apache2**: Continue using Ansible modules for Apache configuration (apache2 package version 2.4.41-4ubuntu3.10)
- **OpenSSL**: Continue using Ansible's openssl_* modules for certificate management

### Security Considerations

- **SSL/TLS Configuration**: The playbooks enforce TLSv1.2 and disable insecure protocols. This security practice should be maintained in the migrated Ansible roles.
  
- **SSH Security**: The InSpec profile checks for secure SSH configuration, specifically ensuring root login is disabled. This should be incorporated into the Ansible roles as both configuration and verification steps.
  
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL/TLS certificate generation should use Ansible Vault for storing private keys
  - Count of credentials detected: 3 (username, password, SSL private key)

### Technical Challenges

- **InSpec Integration**: Determining the best approach to integrate InSpec tests with Ansible workflows. Mitigation strategy: Evaluate ansible-test and Molecule frameworks to determine which provides the best integration with InSpec.
  
- **Chef Automate Replacement**: Identifying Ansible equivalents for Chef Automate functionality. Mitigation strategy: Consider using AWX/Tower as a replacement for Chef Automate's dashboard and control features.

- **Self-signed Certificate Management**: Ensuring secure handling of self-signed certificates. Mitigation strategy: Use Ansible Vault for storing certificate private keys and implement proper certificate rotation.

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/*.yml): Low risk as they're already in Ansible format. May need minor adjustments for best practices.
   
2. **InSpec Tests** (chef-and-ansible/tests/*.rb): Moderate complexity to integrate with Ansible testing frameworks.
   
3. **Chef Deployment Scripts** (setup-automate/*.sh): High complexity as they need to be completely rewritten as Ansible playbooks.

### Assumptions

1. The primary goal is to consolidate on Ansible as the configuration management tool while maintaining the compliance testing capabilities of InSpec.
   
2. The current Chef Automate and Chef Infra Server deployment is used for managing infrastructure that will be migrated to Ansible.
   
3. The security compliance requirements enforced by the InSpec tests must be maintained in the Ansible implementation.
   
4. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs.
   
5. The hardcoded credentials in the deployment scripts are for testing purposes only and will be replaced with secure credential management in the production implementation.
   
6. The Apache HTTPS configuration represents a typical web server setup that will be replicated across multiple servers.

7. The migration will maintain the same level of security compliance currently enforced by the InSpec tests, particularly for HTTPS and SSH configurations.