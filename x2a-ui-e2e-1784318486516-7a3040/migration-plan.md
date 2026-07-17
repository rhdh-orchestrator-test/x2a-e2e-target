# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations, with a focus on demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec tests for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while consolidating all infrastructure provisioning into Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-playbook**:
    - Description: Ansible playbook for configuring Apache with HTTPS
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **inspec-tests**:
    - Description: Chef InSpec tests for verifying HTTPS and SSH compliance
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol testing, SSH security testing

- **chef-deployment**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Chef server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring Apache with HTTPS. Will be converted to a proper Ansible role.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability. Will be integrated into the Apache role.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible Molecule or another Ansible-native testing framework.
- `chef-and-ansible/index.html`: Sample HTML file used in the website deployment. Can be directly used in Ansible content.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration. Will need equivalent Ansible-based testing.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Will need equivalent Ansible-based testing.
- `setup-automate/deploy-automate.sh`: Script for deploying Chef Automate and Chef Infra Server. Will need to be replaced with Ansible roles for deploying compliance tools.
- `setup-automate/deploy-chef-server.sh`: Script for deploying Chef Infra Server. Will need to be replaced with Ansible roles for deploying compliance tools.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and apt package references)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native compliance solutions:
  - Option 1: Use ansible-lint for static analysis
  - Option 2: Integrate with OpenSCAP using the ansible-openscap module
  - Option 3: Keep InSpec as a standalone tool but invoke it from Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Tower/AWX for orchestration
  - Ansible Content Collections for compliance profiles
  - GitLab CI/GitHub Actions for pipeline integration

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in the poodle_fix.yml playbook
  - Approach: Create an Ansible role for Apache SSL hardening that enforces TLSv1.2 and disables vulnerable protocols

- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates
  - Approach: Create an Ansible role for certificate management with options for both self-signed and proper CA-signed certificates

- **SSH Hardening**: The SSH InSpec profile checks for secure SSH configuration
  - Approach: Create an Ansible role that applies SSH hardening based on the same compliance requirements

- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password)
  - Approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Compliance Testing**: The primary challenge is replacing Chef InSpec tests with equivalent Ansible-based testing
  - Mitigation: Evaluate ansible-lint, OpenSCAP, and other compliance tools to determine the best fit
  - Consider keeping InSpec as a standalone tool if no suitable Ansible alternative exists

- **Test Kitchen Integration**: The current setup uses Test Kitchen to orchestrate Ansible and InSpec
  - Mitigation: Implement Ansible Molecule for testing, which is designed specifically for Ansible roles and playbooks

### Migration Order

1. **website-https-playbook** (low risk, already in Ansible)
   - Convert to Ansible role structure
   - Enhance with better variable management
   - Add proper documentation

2. **inspec-tests** (moderate complexity)
   - Evaluate alternatives for compliance testing in Ansible
   - Implement chosen solution (ansible-lint, OpenSCAP, or keep InSpec)
   - Update documentation for new testing approach

3. **chef-deployment** (high complexity)
   - Create Ansible roles for deploying compliance tools
   - Implement secure credential management with Ansible Vault
   - Add documentation for the new deployment process

### Assumptions

1. The primary goal is to consolidate on Ansible while maintaining the compliance testing capabilities
2. The InSpec tests are valuable and need equivalent functionality in the migrated solution
3. The deployment scripts for Chef Automate/Infra Server will be replaced with Ansible roles for deploying compliance tools
4. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
5. The migration will include improving security practices, such as replacing hardcoded credentials with Ansible Vault
6. Test Kitchen will be replaced with Ansible Molecule or another Ansible-native testing framework
7. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) will be restructured as proper Ansible roles