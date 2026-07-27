# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef Automate/Infra Server deployment scripts. The migration scope is relatively small, focusing on:

1. Two Ansible playbooks that configure a web server with HTTPS support and SSL security fixes
2. Chef InSpec tests used for compliance verification of the Ansible-managed infrastructure
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing capabilities while consolidating all infrastructure management into Ansible.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **inspec-website-https**:
    - Description: Chef InSpec test profile that verifies HTTPS functionality and SSL security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **inspec-ssh-profile**:
    - Description: Chef InSpec test profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check with STIG compliance metadata

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Shell Script
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Shell Script
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Simple HTML file used as a template. Migration consideration: Convert to an Ansible template.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use ansible-lint for static analysis
  - Option 2: Integrate with Molecule for comprehensive testing
  - Option 3: Maintain InSpec as a standalone compliance tool but invoke it from Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Evaluate if these components are needed or if they can be replaced with:
  - Ansible Tower/AWX for orchestration and control
  - GitLab CI/CD or GitHub Actions for pipeline automation
  - Compliance scanning tools like OpenSCAP or maintaining InSpec as a standalone tool

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening that disables SSLv3 and enables only TLSv1.2
  - Migration approach: Convert the Apache SSL configuration to an Ansible template with the same security settings

- **Self-signed Certificates**: The current implementation generates self-signed certificates
  - Migration approach: Use Ansible's crypto modules to generate certificates or integrate with Let's Encrypt for production environments

- **SSH Hardening**: The InSpec tests verify SSH security configurations
  - Migration approach: Implement equivalent SSH hardening in Ansible and maintain compliance checks

- **Vault/secrets management**:
  - Hardcoded credentials in deploy scripts (username, password)
  - Migration approach: Move credentials to Ansible Vault

### Technical Challenges

- **Compliance Testing**: The repository uses Chef InSpec for compliance testing
  - Mitigation: Either maintain InSpec as a standalone tool called from Ansible or migrate tests to an Ansible-compatible testing framework

- **Test Kitchen Integration**: The current setup uses Test Kitchen to orchestrate Ansible and InSpec
  - Mitigation: Replace with Ansible Molecule for a more Ansible-native testing approach

- **Chef Automate Deployment**: The repository includes scripts to deploy Chef Automate
  - Mitigation: Evaluate if Chef Automate is still needed or if it can be replaced with Ansible Tower/AWX

### Migration Order

1. **website-https playbook** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Convert inline templates to separate template files
   - Implement Ansible best practices (roles, variables)

2. **poodle-fix playbook** (low risk, already in Ansible)
   - Integrate with the website-https playbook as a role or include
   - Ensure idempotence and proper handler usage

3. **InSpec tests** (moderate complexity)
   - Option 1: Keep as-is and call from Ansible
   - Option 2: Convert to Ansible-native testing with Molecule

4. **Chef deployment scripts** (high complexity)
   - Evaluate if Chef components are still needed
   - If needed, convert bash scripts to Ansible playbooks
   - If not needed, document the replacement strategy with Ansible Tower/AWX

### Assumptions

1. The repository is primarily used for demonstration purposes, as indicated by the README mentioning "working examples" and "how-tos"
2. The Chef InSpec tests are valuable for compliance verification and should be preserved in some form
3. The Chef Automate and Chef Infra Server deployment scripts may not be needed if moving entirely to Ansible
4. The hardcoded credentials in the deployment scripts are for demonstration purposes only
5. The SSL configuration and security hardening are important aspects to preserve in the migration
6. The target environment is Ubuntu 20.04 running on Vagrant VMs
7. There may be additional Chef cookbooks or Ansible playbooks not included in this repository that interact with these components