# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks while standardizing them
3. Maintaining Chef InSpec tests for compliance validation

**Timeline Estimate**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The repository contains minimal Chef-specific code, with most infrastructure already defined in Ansible

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys a secure Apache web server with HTTPS configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user/organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user/organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for HTTPS website validation
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance
- `chef-and-ansible/index.html`: Simple HTML file (not found in repository but referenced in playbooks)

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly defined in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Maintain as-is for compliance testing or migrate to Ansible's built-in assert module for simpler tests
- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **kitchen-ansible**: No longer needed when using Molecule
- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that achieve the same configuration

### Security Considerations

- **SSL Configuration**: The playbooks properly configure Apache with TLSv1.2 and disable vulnerable protocols
- **SSH Hardening**: InSpec tests verify SSH root login is disabled
- **Self-signed Certificates**: The playbooks generate self-signed certificates; consider integrating with Let's Encrypt for production
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - No other credential patterns detected in the repository

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment script to Ansible requires understanding the Chef Automate API and configuration options
  - Mitigation: Use the `uri` module in Ansible to interact with Chef Automate API endpoints
  - Consider using the official Chef Automate Ansible collection if available

- **InSpec Test Integration**: Maintaining the InSpec tests while moving to pure Ansible
  - Mitigation: Keep InSpec for compliance testing or convert tests to Ansible assertions

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format
   - Standardize variable naming
   - Add proper documentation
   - Convert to Ansible roles for better organization

2. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Medium complexity
   - Create Ansible roles for Chef Automate and Chef Infra Server deployment
   - Use Ansible Vault for credentials
   - Add idempotency checks

3. **Testing Framework**: Medium complexity
   - Replace Test Kitchen with Molecule
   - Maintain InSpec tests or convert to Ansible assertions

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment (based on README content)
2. The Chef InSpec tests are valuable and should be preserved in some form
3. The hardcoded credentials in the deployment scripts are for demonstration only and would be replaced in a production environment
4. The target environment is Ubuntu 20.04 based on the kitchen.yml configuration
5. The Apache configuration in the Ansible playbooks is sufficient for the use case and doesn't require additional modules or configurations
6. The self-signed certificates are acceptable for the environment, but production would likely require proper CA-signed certificates