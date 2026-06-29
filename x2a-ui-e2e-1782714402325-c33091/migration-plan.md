# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Two Ansible playbooks for configuring HTTPS websites and fixing SSL vulnerabilities
2. Chef InSpec test profiles for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is **LOW** with an estimated timeline of **1-2 weeks** to fully migrate all components to pure Ansible. The primary focus will be on converting InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Ansible playbook that configures Apache with HTTPS, creates self-signed certificates, and deploys a simple website
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-vulnerability-fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **https-compliance-tests**:
    - Description: Chef InSpec tests that verify HTTPS configuration, port availability, and SSL protocol security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: HTTPS validation, SSL protocol verification

- **ssh-compliance-profile**:
    - Description: Chef InSpec profile that verifies SSH security configurations including root login restrictions
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH security compliance checks, STIG validation

- **chef-infrastructure-deployment**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef CLI tools
    - Key Features: Chef server deployment, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and verifying with InSpec
- `index.html`: Sample HTML file used in the website deployment example

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be infrastructure-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule for infrastructure testing
  - Option 2: ansible-lint for static analysis
  - Option 3: Maintain InSpec as a standalone tool called from Ansible

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing Ansible roles and playbooks
  - GitHub Actions or other CI/CD pipeline for automated testing

- **Chef Automate/Infra Server**: Replace deployment scripts with:
  - Ansible playbooks for infrastructure deployment
  - Consider migrating to Ansible Tower/AWX for enterprise management

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Maintain TLSv1.2 requirement and disable insecure protocols
  - Ensure certificate generation follows best practices

- **SSH Hardening**: Preserve the SSH security controls verified by the InSpec profile
  - Create equivalent Ansible tasks to enforce SSH security configurations
  - Implement checks to verify SSH hardening

- **Vault/secrets management**:
  - Hardcoded credentials detected in setup scripts (username, password)
  - Recommend migrating to Ansible Vault for secure credential storage
  - No encrypted data bags or Chef Vault usage detected

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible verification
  - Mitigation: Use Ansible assert modules or custom modules to perform equivalent checks
  - Consider maintaining InSpec as a compliance tool called from Ansible if complex tests are difficult to migrate

- **Chef Server Deployment**: Replacing Chef server deployment with equivalent infrastructure
  - Mitigation: Evaluate if Chef server is still needed or if Ansible can fully replace its functionality
  - If Chef server is still required, create Ansible playbooks to deploy it with proper configuration

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk as they're already in Ansible format
   - Review and optimize existing playbooks
   - Add documentation and improve variable usage

2. **Testing Framework** - Medium complexity
   - Set up Ansible Molecule for testing
   - Create equivalent tests for the InSpec functionality

3. **InSpec Tests** - Medium complexity
   - Convert InSpec tests to Ansible assertions or Molecule verifiers
   - Ensure all compliance checks are preserved

4. **Chef Server Deployment** - High complexity
   - Create Ansible playbooks to replace the Chef server deployment scripts
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The primary purpose of this repository is demonstration/educational rather than production use
2. The InSpec tests are used for compliance verification of infrastructure configured by Ansible
3. The Chef server deployment scripts may not be needed if moving entirely to Ansible
4. No complex Chef cookbooks or recipes need migration (none were found in the repository)
5. The target environment will continue to be Ubuntu 20.04 or compatible systems
6. The hardcoded credentials in the deployment scripts are for demonstration purposes only
7. No external data sources or integrations were identified that would complicate migration