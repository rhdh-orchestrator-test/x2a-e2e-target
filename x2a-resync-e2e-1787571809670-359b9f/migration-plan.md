# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server setup scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks while standardizing them
3. Integrating Chef InSpec tests into an Ansible-native testing framework

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The repository contains minimal Chef-specific code, with most infrastructure already defined in Ansible

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to address POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3, enables TLSv1.2 only

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance
- `chef-and-ansible/index.html`: Simple HTML file for website content

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use ansible-test with custom Python test modules
  - Option 2: Integrate with Molecule for testing
  - Option 3: Keep InSpec as a testing tool but invoke it from Ansible

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role/playbook testing
  - Option 2: Custom Ansible playbook for test environment provisioning

- **Chef Automate/Infra Server**: Replace with:
  - Option 1: AWX/Ansible Tower for web UI and job scheduling
  - Option 2: Ansible Automation Platform for enterprise features

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with TLS 1.2 and disable SSL3 to address POODLE vulnerability. This security hardening should be preserved in the migrated Ansible playbooks.

- **SSH Hardening**: The InSpec tests verify SSH root login is disabled. This security check should be maintained in the Ansible testing framework.

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated on the fly but should be managed securely in production

### Technical Challenges

- **Challenge 1: InSpec Test Migration**: 
  Description: The repository relies on InSpec for compliance testing
  Mitigation: Either maintain InSpec as a testing tool called from Ansible, or convert tests to Ansible assert statements or custom modules

- **Challenge 2: Chef Automate Functionality Replacement**: 
  Description: Chef Automate provides a web UI, reporting, and compliance scanning
  Mitigation: Implement AWX/Tower or Ansible Automation Platform for similar functionality

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/*.yml): Low risk, already in Ansible format, just need standardization
2. **Chef Deployment Scripts** (setup-automate/*.sh): Medium complexity, convert bash scripts to Ansible playbooks
3. **Testing Framework** (chef-and-ansible/tests/*.rb): Higher complexity, requires decision on testing approach

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production deployment, based on the README content
2. The Chef InSpec tests are intended to work alongside Ansible rather than as part of a Chef-specific workflow
3. The hardcoded credentials in the setup scripts are for demonstration only and would be replaced in a production environment
4. The target environment is Ubuntu 20.04 running on Vagrant VMs for testing
5. The Apache web server configuration is a simple example and may need additional security hardening in production
6. The self-signed certificates are for testing only and would be replaced with proper certificates in production