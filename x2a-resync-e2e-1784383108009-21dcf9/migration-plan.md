# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Chef Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on two main components:

1. Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks
2. Existing Ansible playbooks with Chef InSpec tests that need to be consolidated into a pure Ansible solution

The migration complexity is **LOW to MEDIUM** with an estimated timeline of 1-2 weeks. The main complexity comes from ensuring proper security configurations and maintaining the compliance testing capabilities currently provided by Chef InSpec.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization creation

- **secure-web-server**:
    - Description: Ansible playbook for deploying a secure HTTPS web server with Apache
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration, security hardening

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec tests for HTTPS website verification. Migration consideration: Convert to Ansible-native testing with pytest or testinfra.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Migration consideration: Convert to Ansible-native security checks or integrate with ansible-lint.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying HTTPS website. Migration consideration: Maintain as-is but update testing framework.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability. Migration consideration: Integrate with main security playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and package versions in Ansible playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for both on-premises and cloud deployment (based on comments in deployment scripts)

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef InSpec**: Replace with Ansible-native testing frameworks (Molecule, testinfra) or maintain as a separate tool called from Ansible
- **Test Kitchen**: Replace with Molecule for Ansible playbook testing

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols. Migration must maintain these security settings.
- **SSH Hardening**: InSpec tests verify SSH root login is disabled. Migration must include equivalent security checks.
- **Self-signed Certificates**: The playbooks generate self-signed certificates. Consider integrating with Let's Encrypt for production environments.
- **Vault/secrets management**:
  - Hardcoded credentials in `setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh` (username, password)
  - Count: 2 credential sets detected in deployment scripts

### Technical Challenges

- **Compliance Testing**: Chef InSpec provides robust compliance testing. Challenge: Replicating the same level of compliance testing with Ansible-native tools.
  - Mitigation: Consider using ansible-lint with custom rules, or maintain InSpec as a separate tool called from Ansible.

- **Certificate Management**: The current solution generates self-signed certificates. Challenge: Implementing proper certificate management in Ansible.
  - Mitigation: Use the Ansible `community.crypto` collection for certificate management or integrate with Let's Encrypt.

### Migration Order

1. **secure-web-server** (low risk, already in Ansible): Convert InSpec tests to Ansible-native testing
   - Start with `chef-and-ansible/website_https.yml` and `chef-and-ansible/poodle_fix.yml`
   - Convert `chef-and-ansible/tests/website_https_verify.rb` and `chef-and-ansible/tests/ssh_profile.rb` to Ansible-native tests

2. **chef-automate-deployment** (moderate complexity): Create Ansible playbooks to replace Chef deployment scripts
   - Convert `setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh` to Ansible playbooks

### Assumptions

1. The current Chef InSpec tests are required for compliance purposes and need to be maintained in some form.
2. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with proper secret management in the migrated solution.
3. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
4. The deployment scripts are intended for both on-premises and cloud environments.
5. The migration does not need to maintain backward compatibility with Chef Automate/Infra Server.