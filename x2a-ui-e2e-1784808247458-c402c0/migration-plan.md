# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components that need to be migrated to a pure Ansible solution. The repository appears to be a demonstration environment showing how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, focusing on:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec tests for compliance verification
3. Chef Automate and Chef Infra Server deployment scripts

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks for a complete migration. The main effort will be in converting the Chef InSpec tests to Ansible-compatible testing frameworks while maintaining the existing Ansible playbooks.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef components that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support, including self-signed certificate generation
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL module configuration, service restart handlers

- **inspec-website-tests**:
    - Description: Chef InSpec tests that verify HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening tests, HTTP response validation, SSL protocol verification

- **inspec-ssh-profile**:
    - Description: Chef InSpec profile that verifies SSH security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance tagging with STIG references

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework.
- `index.html`: Static HTML content for the test website. Can be directly used in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible-specific CI/CD pipelines

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Tower/AWX for enterprise orchestration
  - GitLab CI or GitHub Actions for pipeline automation
  - Compliance automation using OpenSCAP or similar tools integrated with Ansible

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should maintain or enhance the security posture:
  - Ensure TLSv1.2+ remains enforced
  - Consider upgrading to TLSv1.3 where supported
  - Replace self-signed certificates with Let's Encrypt integration

- **SSH Hardening**: The InSpec profile checks for SSH root login restrictions. Migration should:
  - Incorporate these checks into Ansible-native assertions
  - Expand SSH hardening using Ansible security roles

- **Vault/secrets management**:
  - Current implementation has hardcoded credentials in the Chef Automate/Server deployment scripts
  - Migration should use Ansible Vault for securing:
    - User passwords (currently plaintext in deploy scripts)
    - SSL private keys
    - Any other sensitive information

### Technical Challenges

- **Compliance Testing**: Converting Chef InSpec tests to Ansible-native testing will require careful mapping of test assertions to maintain the same level of compliance verification.
  - Mitigation: Create a mapping document between InSpec resources and Ansible modules/assertions

- **Test Kitchen Integration**: The current setup uses Test Kitchen to orchestrate Ansible and InSpec.
  - Mitigation: Implement Molecule testing framework which is designed specifically for Ansible roles

- **Chef Automate Functionality**: The Chef Automate deployment provides compliance reporting and visualization.
  - Mitigation: Evaluate Ansible Tower/AWX with compliance reporting plugins or integrate with tools like OpenSCAP

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format. May need minor updates for best practices.

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible-native testing or Molecule tests.

3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Replace with Ansible playbooks for deploying Ansible Tower/AWX or other orchestration tools.

4. **Test Kitchen Configuration** (kitchen.yml): Replace with Molecule configuration for testing the Ansible roles.

### Assumptions

1. The repository is primarily for demonstration purposes showing Chef InSpec with Ansible, not a production environment.

2. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions.

3. The security compliance requirements (STIG references in the SSH profile) will need to be maintained in the Ansible solution.

4. The self-signed certificates are acceptable for the demonstration environment but may need to be replaced with proper certificate management in production.

5. The hardcoded credentials in the deployment scripts are for demonstration only and will be properly secured in the migrated solution.

6. The Test Kitchen setup is primarily for local testing and development, not CI/CD pipelines.