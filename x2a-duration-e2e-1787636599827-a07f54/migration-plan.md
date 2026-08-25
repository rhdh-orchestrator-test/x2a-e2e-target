# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks while standardizing them
3. Maintaining Chef InSpec tests for compliance validation
4. Ensuring proper integration between components

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The repository contains minimal Chef-specific code, with most infrastructure already defined in Ansible

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys a secure web server with SSL/TLS configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
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
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website deployment
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance
- `chef-and-ansible/index.html`: Static HTML file for website content

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Maintain InSpec for compliance testing, integrate with Ansible using the `ansible.builtin.shell` module or consider migrating to Ansible's built-in assertion modules
- **Test Kitchen**: Replace with Ansible Molecule for testing or maintain Test Kitchen with the `kitchen-ansible` plugin
- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that install and configure Chef components if still needed, or migrate completely to Ansible AWX/Tower

### Security Considerations

- **SSL/TLS Configuration**: The repository contains specific SSL hardening (POODLE mitigation). Ensure these security controls are maintained in the migrated Ansible playbooks.
- **Self-signed Certificates**: The current implementation generates self-signed certificates. Consider implementing proper certificate management using Ansible Vault or external certificate management.
- **SSH Hardening**: InSpec tests verify SSH security configurations. Ensure these controls are implemented in the Ansible playbooks.
- **Vault/secrets management**:
  - Hardcoded credentials in `deploy-automate.sh` and `deploy-chef-server.sh` (username, password) should be moved to Ansible Vault
  - No other credentials detected in the repository

### Technical Challenges

- **Chef Automate/Infra Server Deployment**: Converting the bash scripts to idempotent Ansible playbooks will require careful handling of installation steps and configuration management.
- **InSpec Integration**: Maintaining InSpec tests while migrating to Ansible requires proper integration between the two tools.
- **SSL Certificate Management**: Ensuring proper certificate generation and management in Ansible.

### Migration Order

1. **Existing Ansible Playbooks** (Low risk, already in Ansible format)
   - Standardize `website_https.yml` and `poodle_fix.yml` to follow Ansible best practices
   - Update variable naming conventions and structure

2. **InSpec Tests** (Low risk, can be used with Ansible)
   - Integrate existing InSpec tests with Ansible playbooks
   - Update Test Kitchen configuration or migrate to Molecule

3. **Chef Deployment Scripts** (Medium complexity)
   - Convert `deploy-automate.sh` and `deploy-chef-server.sh` to Ansible playbooks
   - Implement proper secret management using Ansible Vault
   - Ensure idempotence in the deployment process

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production deployment, based on the README content.
2. The Chef Automate and Chef Infra Server deployment scripts are still needed in the environment. If not, they can be removed rather than migrated.
3. InSpec will continue to be used for compliance testing alongside Ansible.
4. The hardcoded credentials in the deployment scripts are examples and not actual production credentials.
5. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions.
6. The existing Ansible playbooks (`website_https.yml` and `poodle_fix.yml`) are functional and only need standardization rather than complete rewriting.