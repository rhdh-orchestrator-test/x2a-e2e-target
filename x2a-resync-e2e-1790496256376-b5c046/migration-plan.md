# MIGRATION FROM CHEF INFRASTRUCTURE TO ANSIBLE

This repository contains Chef infrastructure deployment scripts and Ansible playbook examples demonstrating compliance automation integration. The migration scope is limited as the primary configuration management is already implemented in Ansible playbooks. The main migration effort involves consolidating Chef infrastructure deployment into Ansible-based infrastructure provisioning.

## Module Migration Plan

This repository contains Chef infrastructure deployment scripts and Ansible demonstration playbooks that need consolidation and standardization:

### MODULE INVENTORY

**chef-and-ansible**:
- Description: Ansible playbook demonstrating Apache HTTPS website deployment with SSL certificate generation, virtual host configuration, and security hardening
- Path: chef-and-ansible/
- Technology: Ansible (already migrated)
- Key Features: Self-signed SSL certificates via OpenSSL modules, Apache virtual host configuration, POODLE vulnerability mitigation, InSpec compliance testing integration

**setup-automate**:
- Description: Bash scripts for deploying Chef Automate and Chef Infra Server infrastructure with user and organization provisioning
- Path: setup-automate/
- Technology: Bash/Shell scripts with Chef server deployment
- Key Features: Chef Automate deployment, Chef Infra Server setup, user/organization creation, system tuning parameters

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `deploy-automate.sh`: Chef Automate and Infra Server deployment script with system configuration
- `deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `website_https.yml`: Ansible playbook for Apache HTTPS configuration and SSL setup
- `poodle_fix.yml`: Ansible playbook for SSL security hardening (POODLE vulnerability mitigation)
- `website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL protocol validation
- `ssh_profile.rb`: InSpec compliance profile for SSH security configuration (root login disabled)

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant (configured in kitchen.yml driver)
- **Cloud Platform**: Not specified (deployment scripts support on-premises or cloud VMs)

## Migration Approach

### Key Dependencies to Address

- **Chef Automate/Infra Server**: Replace bash deployment scripts with Ansible infrastructure provisioning playbooks
- **Test Kitchen**: Integrate existing kitchen.yml configuration into Ansible testing framework (molecule or native ansible-test)
- **InSpec**: Maintain existing InSpec compliance tests as they already integrate well with Ansible workflows

### Security Considerations

- **SSL Certificate Management**: Current implementation uses self-signed certificates via OpenSSL Ansible modules - consider integration with Let's Encrypt or enterprise CA for production
- **Hardcoded Credentials**: The deployment scripts contain hardcoded usernames, passwords, and email addresses that need to be externalized to Ansible Vault
- **SSH Security**: Existing InSpec profiles enforce SSH root login restrictions - maintain these compliance checks in migrated infrastructure
- **SSL Protocol Security**: POODLE fix playbook demonstrates security hardening - ensure similar security configurations are maintained

### Technical Challenges

- **Infrastructure Deployment**: Converting bash-based Chef server deployment to Ansible requires creating playbooks for Chef Automate installation, system tuning, and user provisioning
- **Testing Integration**: Maintaining Test Kitchen workflow with InSpec while transitioning to Ansible-native testing approaches
- **Compliance Continuity**: Ensuring existing InSpec compliance profiles continue to work with new Ansible-managed infrastructure

### Migration Order

1. **chef-and-ansible playbooks** (already complete - no migration needed)
2. **InSpec compliance profiles** (maintain existing - already Ansible-compatible)
3. **Chef infrastructure deployment** (convert bash scripts to Ansible playbooks)

### Assumptions

- The existing Ansible playbooks in chef-and-ansible/ are demonstration examples and may need production hardening
- Chef Automate/Infra Server deployment will be replaced with Ansible-managed infrastructure rather than maintaining Chef infrastructure
- InSpec compliance testing framework will be retained as it provides value for continuous compliance validation
- The target environment supports Ansible execution and has necessary privileges for system configuration
- SSL certificate management strategy (self-signed vs. CA-issued) needs to be determined based on production requirements
- User credentials and organizational details in deployment scripts represent example values that need to be replaced with actual production values